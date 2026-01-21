"""
HubSpot CRM Connector for AMANDA Portal
========================================
Bidirectional sync between HubSpot CRM and AMANDA proposal pipeline.

Author: rockITdata LLC
Version: 7.3 (Phase 1B)
"""

import os
import time
import json
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import threading
from functools import wraps

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

class HubSpotConfig:
    """HubSpot API configuration."""
    BASE_URL = "https://api.hubapi.com"
    API_VERSION = "v3"
    
    # Rate limiting: 100 requests per 10 seconds
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 10  # seconds
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF = 0.5
    
    # Custom property group
    AMANDA_PROPERTY_GROUP = "amanda_portal"


class HubSpotStage(Enum):
    """HubSpot deal stages mapped to AMANDA phases."""
    APPOINTMENT_SCHEDULED = "appointmentscheduled"
    QUALIFIED_TO_BUY = "qualifiedtobuy"
    PRESENTATION_SCHEDULED = "presentationscheduled"
    DECISION_MAKER_BOUGHT_IN = "decisionmakerboughtin"
    CONTRACT_SENT = "contractsent"
    CLOSED_WON = "closedwon"
    CLOSED_LOST = "closedlost"


class AmandaPhase(Enum):
    """AMANDA proposal phases."""
    QUALIFICATION = "qualification"
    GATE_1 = "gate_1"
    CAPTURE = "capture"
    DEVELOPMENT = "development"
    REVIEW = "review"
    SUBMITTED = "submitted"
    ARCHIVED = "archived"


# Stage mapping: HubSpot → AMANDA
STAGE_MAPPING = {
    HubSpotStage.APPOINTMENT_SCHEDULED: AmandaPhase.QUALIFICATION,
    HubSpotStage.QUALIFIED_TO_BUY: AmandaPhase.GATE_1,
    HubSpotStage.PRESENTATION_SCHEDULED: AmandaPhase.CAPTURE,
    HubSpotStage.DECISION_MAKER_BOUGHT_IN: AmandaPhase.DEVELOPMENT,
    HubSpotStage.CONTRACT_SENT: AmandaPhase.REVIEW,
    HubSpotStage.CLOSED_WON: AmandaPhase.SUBMITTED,
    HubSpotStage.CLOSED_LOST: AmandaPhase.ARCHIVED,
}

# Reverse mapping: AMANDA → HubSpot
REVERSE_STAGE_MAPPING = {v: k for k, v in STAGE_MAPPING.items()}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class HubSpotDeal:
    """Represents a HubSpot deal with AMANDA custom properties."""
    id: Optional[str] = None
    name: str = ""
    amount: float = 0.0
    stage: str = ""
    close_date: Optional[str] = None
    pipeline: str = "default"
    
    # Standard HubSpot properties
    owner_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # AMANDA custom properties
    amanda_pwin: float = 0.0
    amanda_gate_status: str = "PENDING"
    amanda_phase: str = "qualification"
    amanda_compliance_coverage: float = 0.0
    amanda_solicitation_number: str = ""
    amanda_agency: str = ""
    amanda_priority_tier: str = "P-2"
    amanda_contract_vehicle: str = ""
    
    # Sync metadata
    last_synced: Optional[str] = None
    sync_direction: str = "bidirectional"
    
    def to_hubspot_properties(self) -> Dict[str, Any]:
        """Convert to HubSpot API format for create/update."""
        return {
            "dealname": self.name,
            "amount": str(self.amount),
            "dealstage": self.stage,
            "closedate": self.close_date,
            "pipeline": self.pipeline,
            "hubspot_owner_id": self.owner_id,
            # AMANDA custom properties
            "amanda_pwin": str(self.amanda_pwin),
            "amanda_gate_status": self.amanda_gate_status,
            "amanda_phase": self.amanda_phase,
            "amanda_compliance_coverage": str(self.amanda_compliance_coverage),
            "amanda_solicitation_number": self.amanda_solicitation_number,
            "amanda_agency": self.amanda_agency,
            "amanda_priority_tier": self.amanda_priority_tier,
            "amanda_contract_vehicle": self.amanda_contract_vehicle,
        }
    
    @classmethod
    def from_hubspot_response(cls, data: Dict[str, Any]) -> "HubSpotDeal":
        """Create instance from HubSpot API response."""
        props = data.get("properties", {})
        return cls(
            id=data.get("id"),
            name=props.get("dealname", ""),
            amount=float(props.get("amount", 0) or 0),
            stage=props.get("dealstage", ""),
            close_date=props.get("closedate"),
            pipeline=props.get("pipeline", "default"),
            owner_id=props.get("hubspot_owner_id"),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
            # AMANDA properties (with defaults for missing)
            amanda_pwin=float(props.get("amanda_pwin", 0) or 0),
            amanda_gate_status=props.get("amanda_gate_status", "PENDING"),
            amanda_phase=props.get("amanda_phase", "qualification"),
            amanda_compliance_coverage=float(props.get("amanda_compliance_coverage", 0) or 0),
            amanda_solicitation_number=props.get("amanda_solicitation_number", ""),
            amanda_agency=props.get("amanda_agency", ""),
            amanda_priority_tier=props.get("amanda_priority_tier", "P-2"),
            amanda_contract_vehicle=props.get("amanda_contract_vehicle", ""),
        )


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    deals_synced: int = 0
    deals_created: int = 0
    deals_updated: int = 0
    deals_failed: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class WebhookEvent:
    """Parsed HubSpot webhook event."""
    event_id: str
    subscription_type: str
    object_id: str
    property_name: Optional[str] = None
    property_value: Optional[str] = None
    occurred_at: Optional[str] = None
    portal_id: Optional[str] = None


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Thread-safe rate limiter for HubSpot API.
    Allows 100 requests per 10 seconds.
    """
    
    def __init__(
        self,
        max_requests: int = HubSpotConfig.RATE_LIMIT_REQUESTS,
        window_seconds: int = HubSpotConfig.RATE_LIMIT_WINDOW
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []
        self._lock = threading.Lock()
    
    def acquire(self) -> float:
        """
        Acquire permission to make a request.
        Returns wait time in seconds (0 if no wait needed).
        """
        with self._lock:
            now = time.time()
            
            # Remove expired timestamps
            cutoff = now - self.window_seconds
            self.requests = [t for t in self.requests if t > cutoff]
            
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest = self.requests[0]
                wait_time = oldest + self.window_seconds - now
                return max(0, wait_time)
            
            # Record this request
            self.requests.append(now)
            return 0
    
    def wait_and_acquire(self) -> None:
        """Wait if necessary, then acquire permission."""
        wait_time = self.acquire()
        if wait_time > 0:
            logger.info(f"Rate limit: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            self.acquire()


def rate_limited(func: Callable) -> Callable:
    """Decorator to apply rate limiting to API calls."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, '_rate_limiter'):
            self._rate_limiter.wait_and_acquire()
        return func(self, *args, **kwargs)
    return wrapper


# =============================================================================
# HUBSPOT CLIENT
# =============================================================================

class HubSpotClient:
    """
    HubSpot API client with OAuth support, rate limiting, and retry logic.
    """
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize HubSpot client.
        
        Args:
            access_token: HubSpot API access token (Private App or OAuth)
            refresh_token: OAuth refresh token (optional)
            client_id: OAuth client ID (optional)
            client_secret: OAuth client secret (optional)
        """
        self.access_token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.refresh_token = refresh_token or os.getenv("HUBSPOT_REFRESH_TOKEN")
        self.client_id = client_id or os.getenv("HUBSPOT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("HUBSPOT_CLIENT_SECRET")
        
        self._rate_limiter = RateLimiter()
        self._session = self._create_session()
        self._token_expires_at: Optional[datetime] = None
        
        # Webhook secret for signature verification
        self.webhook_secret = os.getenv("HUBSPOT_WEBHOOK_SECRET")
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=HubSpotConfig.MAX_RETRIES,
            backoff_factor=HubSpotConfig.RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PATCH", "DELETE"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    @property
    def _headers(self) -> Dict[str, str]:
        """Get request headers with current access token."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _refresh_token_if_needed(self) -> None:
        """Refresh OAuth token if expired."""
        if not self.refresh_token or not self.client_id or not self.client_secret:
            return
        
        if self._token_expires_at and datetime.utcnow() < self._token_expires_at:
            return
        
        logger.info("Refreshing HubSpot OAuth token...")
        
        response = self._session.post(
            f"{HubSpotConfig.BASE_URL}/oauth/v1/token",
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            expires_in = data.get("expires_in", 1800)
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
            logger.info("Token refreshed successfully")
        else:
            logger.error(f"Token refresh failed: {response.text}")
            raise HubSpotAuthError(f"Token refresh failed: {response.status_code}")
    
    @rate_limited
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request with rate limiting and error handling.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (relative to base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
        """
        self._refresh_token_if_needed()
        
        url = f"{HubSpotConfig.BASE_URL}/{endpoint}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=self._headers,
                json=data,
                params=params,
            )
            
            # Log for debugging
            logger.debug(f"{method} {endpoint}: {response.status_code}")
            
            if response.status_code == 204:
                return {"success": True}
            
            if response.status_code >= 400:
                error_data = response.json() if response.text else {}
                raise HubSpotAPIError(
                    message=error_data.get("message", f"HTTP {response.status_code}"),
                    status_code=response.status_code,
                    details=error_data,
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise HubSpotConnectionError(str(e))
    
    # -------------------------------------------------------------------------
    # DEAL OPERATIONS
    # -------------------------------------------------------------------------
    
    def get_deal(self, deal_id: str) -> HubSpotDeal:
        """
        Get a single deal by ID.
        
        Args:
            deal_id: HubSpot deal ID
            
        Returns:
            HubSpotDeal instance
        """
        properties = [
            "dealname", "amount", "dealstage", "closedate", "pipeline",
            "hubspot_owner_id", "amanda_pwin", "amanda_gate_status",
            "amanda_phase", "amanda_compliance_coverage",
            "amanda_solicitation_number", "amanda_agency",
            "amanda_priority_tier", "amanda_contract_vehicle",
        ]
        
        response = self._request(
            "GET",
            f"crm/{HubSpotConfig.API_VERSION}/objects/deals/{deal_id}",
            params={"properties": ",".join(properties)},
        )
        
        return HubSpotDeal.from_hubspot_response(response)
    
    def list_deals(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        pipeline_id: Optional[str] = None,
    ) -> tuple[List[HubSpotDeal], Optional[str]]:
        """
        List deals with pagination.
        
        Args:
            limit: Number of deals to retrieve (max 100)
            after: Pagination cursor
            pipeline_id: Filter by pipeline
            
        Returns:
            Tuple of (deals list, next page cursor)
        """
        properties = [
            "dealname", "amount", "dealstage", "closedate", "pipeline",
            "hubspot_owner_id", "amanda_pwin", "amanda_gate_status",
            "amanda_phase", "amanda_compliance_coverage",
            "amanda_solicitation_number", "amanda_agency",
            "amanda_priority_tier", "amanda_contract_vehicle",
        ]
        
        params = {
            "limit": min(limit, 100),
            "properties": ",".join(properties),
        }
        
        if after:
            params["after"] = after
        
        response = self._request(
            "GET",
            f"crm/{HubSpotConfig.API_VERSION}/objects/deals",
            params=params,
        )
        
        deals = [
            HubSpotDeal.from_hubspot_response(d)
            for d in response.get("results", [])
        ]
        
        # Filter by pipeline if specified
        if pipeline_id:
            deals = [d for d in deals if d.pipeline == pipeline_id]
        
        paging = response.get("paging", {})
        next_cursor = paging.get("next", {}).get("after")
        
        return deals, next_cursor
    
    def create_deal(self, deal: HubSpotDeal) -> HubSpotDeal:
        """
        Create a new deal in HubSpot.
        
        Args:
            deal: HubSpotDeal instance with properties
            
        Returns:
            Created deal with HubSpot ID
        """
        response = self._request(
            "POST",
            f"crm/{HubSpotConfig.API_VERSION}/objects/deals",
            data={"properties": deal.to_hubspot_properties()},
        )
        
        return HubSpotDeal.from_hubspot_response(response)
    
    def update_deal(self, deal_id: str, deal: HubSpotDeal) -> HubSpotDeal:
        """
        Update an existing deal.
        
        Args:
            deal_id: HubSpot deal ID
            deal: HubSpotDeal instance with updated properties
            
        Returns:
            Updated deal
        """
        response = self._request(
            "PATCH",
            f"crm/{HubSpotConfig.API_VERSION}/objects/deals/{deal_id}",
            data={"properties": deal.to_hubspot_properties()},
        )
        
        return HubSpotDeal.from_hubspot_response(response)
    
    def delete_deal(self, deal_id: str) -> bool:
        """
        Delete (archive) a deal.
        
        Args:
            deal_id: HubSpot deal ID
            
        Returns:
            True if successful
        """
        self._request(
            "DELETE",
            f"crm/{HubSpotConfig.API_VERSION}/objects/deals/{deal_id}",
        )
        return True
    
    # -------------------------------------------------------------------------
    # BATCH OPERATIONS
    # -------------------------------------------------------------------------
    
    def batch_get_deals(self, deal_ids: List[str]) -> List[HubSpotDeal]:
        """
        Get multiple deals by ID in a single request.
        
        Args:
            deal_ids: List of HubSpot deal IDs
            
        Returns:
            List of HubSpotDeal instances
        """
        properties = [
            "dealname", "amount", "dealstage", "closedate", "pipeline",
            "hubspot_owner_id", "amanda_pwin", "amanda_gate_status",
            "amanda_phase", "amanda_compliance_coverage",
        ]
        
        response = self._request(
            "POST",
            f"crm/{HubSpotConfig.API_VERSION}/objects/deals/batch/read",
            data={
                "inputs": [{"id": did} for did in deal_ids],
                "properties": properties,
            },
        )
        
        return [
            HubSpotDeal.from_hubspot_response(d)
            for d in response.get("results", [])
        ]
    
    def batch_update_deals(self, updates: List[tuple[str, HubSpotDeal]]) -> SyncResult:
        """
        Update multiple deals in a single request.
        
        Args:
            updates: List of (deal_id, deal) tuples
            
        Returns:
            SyncResult with operation counts
        """
        result = SyncResult(success=True)
        
        # HubSpot batch limit is 100
        for i in range(0, len(updates), 100):
            batch = updates[i:i + 100]
            
            try:
                response = self._request(
                    "POST",
                    f"crm/{HubSpotConfig.API_VERSION}/objects/deals/batch/update",
                    data={
                        "inputs": [
                            {
                                "id": deal_id,
                                "properties": deal.to_hubspot_properties(),
                            }
                            for deal_id, deal in batch
                        ]
                    },
                )
                
                result.deals_updated += len(response.get("results", []))
                
            except HubSpotAPIError as e:
                result.errors.append(str(e))
                result.deals_failed += len(batch)
        
        result.deals_synced = result.deals_updated
        result.success = result.deals_failed == 0
        
        return result
    
    # -------------------------------------------------------------------------
    # CUSTOM PROPERTIES
    # -------------------------------------------------------------------------
    
    def create_amanda_properties(self) -> bool:
        """
        Create AMANDA custom properties in HubSpot.
        Should be called once during initial setup.
        
        Returns:
            True if successful
        """
        # First, create the property group
        try:
            self._request(
                "POST",
                f"crm/{HubSpotConfig.API_VERSION}/properties/deals/groups",
                data={
                    "name": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                    "label": "AMANDA Portal",
                    "displayOrder": 0,
                },
            )
        except HubSpotAPIError as e:
            if "already exists" not in str(e).lower():
                logger.warning(f"Could not create property group: {e}")
        
        # Define AMANDA properties
        properties = [
            {
                "name": "amanda_pwin",
                "label": "Win Probability",
                "type": "number",
                "fieldType": "number",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "AMANDA calculated probability of win (0-100)",
            },
            {
                "name": "amanda_gate_status",
                "label": "Gate Status",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "Current gate decision status",
                "options": [
                    {"label": "Pending", "value": "PENDING"},
                    {"label": "Go", "value": "GO"},
                    {"label": "Conditional Go", "value": "CONDITIONAL_GO"},
                    {"label": "Pause", "value": "PAUSE"},
                    {"label": "No-Go", "value": "NO_GO"},
                ],
            },
            {
                "name": "amanda_phase",
                "label": "Proposal Phase",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "Current Shipley proposal phase",
                "options": [
                    {"label": "Qualification", "value": "qualification"},
                    {"label": "Gate 1", "value": "gate_1"},
                    {"label": "Capture", "value": "capture"},
                    {"label": "Development", "value": "development"},
                    {"label": "Review", "value": "review"},
                    {"label": "Submitted", "value": "submitted"},
                    {"label": "Archived", "value": "archived"},
                ],
            },
            {
                "name": "amanda_compliance_coverage",
                "label": "Compliance Coverage %",
                "type": "number",
                "fieldType": "number",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "Percentage of requirements with evidence",
            },
            {
                "name": "amanda_solicitation_number",
                "label": "Solicitation Number",
                "type": "string",
                "fieldType": "text",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "Federal solicitation/RFP number",
            },
            {
                "name": "amanda_agency",
                "label": "Agency",
                "type": "string",
                "fieldType": "text",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "Target federal agency (VA, DHA, CMS, etc.)",
            },
            {
                "name": "amanda_priority_tier",
                "label": "Priority Tier",
                "type": "enumeration",
                "fieldType": "select",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "Opportunity priority classification",
                "options": [
                    {"label": "P-0 (Must Win)", "value": "P-0"},
                    {"label": "P-1 (Strategic)", "value": "P-1"},
                    {"label": "P-2 (Gap Filler)", "value": "P-2"},
                ],
            },
            {
                "name": "amanda_contract_vehicle",
                "label": "Contract Vehicle",
                "type": "string",
                "fieldType": "text",
                "groupName": HubSpotConfig.AMANDA_PROPERTY_GROUP,
                "description": "IDIQ vehicle (GSA, T4NG, etc.)",
            },
        ]
        
        created_count = 0
        for prop in properties:
            try:
                self._request(
                    "POST",
                    f"crm/{HubSpotConfig.API_VERSION}/properties/deals",
                    data=prop,
                )
                created_count += 1
                logger.info(f"Created property: {prop['name']}")
            except HubSpotAPIError as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Property already exists: {prop['name']}")
                else:
                    logger.error(f"Failed to create property {prop['name']}: {e}")
        
        return created_count > 0
    
    # -------------------------------------------------------------------------
    # WEBHOOK VERIFICATION
    # -------------------------------------------------------------------------
    
    def verify_webhook_signature(
        self,
        request_body: bytes,
        signature: str,
        timestamp: Optional[str] = None,
    ) -> bool:
        """
        Verify HubSpot webhook signature.
        
        Args:
            request_body: Raw request body bytes
            signature: X-HubSpot-Signature header value
            timestamp: Optional timestamp for v3 signatures
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured - skipping verification")
            return True
        
        # HubSpot v2 signature: SHA-256(client_secret + request_body)
        expected = hmac.new(
            self.webhook_secret.encode(),
            request_body,
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature.lower())
    
    def parse_webhook_events(self, payload: List[Dict]) -> List[WebhookEvent]:
        """
        Parse webhook payload into event objects.
        
        Args:
            payload: Raw webhook payload (list of events)
            
        Returns:
            List of WebhookEvent instances
        """
        events = []
        for item in payload:
            events.append(WebhookEvent(
                event_id=str(item.get("eventId", "")),
                subscription_type=item.get("subscriptionType", ""),
                object_id=str(item.get("objectId", "")),
                property_name=item.get("propertyName"),
                property_value=item.get("propertyValue"),
                occurred_at=item.get("occurredAt"),
                portal_id=str(item.get("portalId", "")),
            ))
        return events
    
    # -------------------------------------------------------------------------
    # CONNECTION TEST
    # -------------------------------------------------------------------------
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test HubSpot API connection.
        
        Returns:
            Dict with connection status and account info
        """
        try:
            # Get account info
            response = self._request(
                "GET",
                "integrations/v1/me",
            )
            
            return {
                "connected": True,
                "portal_id": response.get("portalId"),
                "hub_domain": response.get("hubDomain"),
                "time_zone": response.get("timeZone"),
                "currency": response.get("currency"),
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
            }


# =============================================================================
# SYNC SERVICE
# =============================================================================

class HubSpotSyncService:
    """
    Bidirectional sync service between AMANDA and HubSpot.
    """
    
    def __init__(self, client: HubSpotClient, db_session=None):
        """
        Initialize sync service.
        
        Args:
            client: HubSpotClient instance
            db_session: Database session for sync state (optional)
        """
        self.client = client
        self.db = db_session
        self._callbacks: Dict[str, List[Callable]] = {
            "deal_created": [],
            "deal_updated": [],
            "deal_won": [],
            "deal_lost": [],
        }
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for sync events."""
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
    
    def _trigger_callbacks(self, event_type: str, deal: HubSpotDeal) -> None:
        """Trigger registered callbacks for an event."""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(deal)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")
    
    def sync_from_hubspot(
        self,
        pipeline_id: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> SyncResult:
        """
        Pull deals from HubSpot into AMANDA.
        
        Args:
            pipeline_id: Filter by specific pipeline
            since: Only sync deals modified after this time
            
        Returns:
            SyncResult with operation counts
        """
        result = SyncResult(success=True)
        cursor = None
        
        while True:
            deals, cursor = self.client.list_deals(
                limit=100,
                after=cursor,
                pipeline_id=pipeline_id,
            )
            
            for deal in deals:
                try:
                    # Check if deal exists in AMANDA
                    # This would be implemented with actual DB operations
                    result.deals_synced += 1
                    
                    # Trigger callbacks
                    if deal.stage == HubSpotStage.CLOSED_WON.value:
                        self._trigger_callbacks("deal_won", deal)
                    elif deal.stage == HubSpotStage.CLOSED_LOST.value:
                        self._trigger_callbacks("deal_lost", deal)
                    else:
                        self._trigger_callbacks("deal_updated", deal)
                        
                except Exception as e:
                    result.errors.append(f"Deal {deal.id}: {e}")
                    result.deals_failed += 1
            
            if not cursor:
                break
        
        result.success = result.deals_failed == 0
        return result
    
    def sync_to_hubspot(self, amanda_deals: List[Dict]) -> SyncResult:
        """
        Push AMANDA deals to HubSpot.
        
        Args:
            amanda_deals: List of AMANDA deal dictionaries
            
        Returns:
            SyncResult with operation counts
        """
        result = SyncResult(success=True)
        
        for deal_data in amanda_deals:
            try:
                deal = HubSpotDeal(
                    id=deal_data.get("hubspot_deal_id"),
                    name=deal_data.get("name", ""),
                    amount=deal_data.get("value", 0),
                    amanda_pwin=deal_data.get("pwin", 0),
                    amanda_gate_status=deal_data.get("gate_status", "PENDING"),
                    amanda_phase=deal_data.get("phase", "qualification"),
                    amanda_compliance_coverage=deal_data.get("compliance_pct", 0),
                    amanda_solicitation_number=deal_data.get("solicitation", ""),
                    amanda_agency=deal_data.get("agency", ""),
                    amanda_priority_tier=deal_data.get("priority", "P-2"),
                )
                
                if deal.id:
                    # Update existing
                    self.client.update_deal(deal.id, deal)
                    result.deals_updated += 1
                else:
                    # Create new
                    created = self.client.create_deal(deal)
                    result.deals_created += 1
                    # Return new ID to caller
                    deal_data["hubspot_deal_id"] = created.id
                
                result.deals_synced += 1
                
            except Exception as e:
                result.errors.append(f"Deal {deal_data.get('name')}: {e}")
                result.deals_failed += 1
        
        result.success = result.deals_failed == 0
        return result
    
    def handle_webhook_event(self, event: WebhookEvent) -> None:
        """
        Process a webhook event from HubSpot.
        
        Args:
            event: Parsed webhook event
        """
        logger.info(f"Processing webhook: {event.subscription_type} for {event.object_id}")
        
        if event.subscription_type == "deal.creation":
            deal = self.client.get_deal(event.object_id)
            self._trigger_callbacks("deal_created", deal)
            
        elif event.subscription_type == "deal.propertyChange":
            deal = self.client.get_deal(event.object_id)
            
            # Check for stage changes
            if event.property_name == "dealstage":
                if event.property_value == HubSpotStage.CLOSED_WON.value:
                    self._trigger_callbacks("deal_won", deal)
                elif event.property_value == HubSpotStage.CLOSED_LOST.value:
                    self._trigger_callbacks("deal_lost", deal)
                else:
                    self._trigger_callbacks("deal_updated", deal)
            else:
                self._trigger_callbacks("deal_updated", deal)
        
        elif event.subscription_type == "deal.deletion":
            # Handle archived deals
            logger.info(f"Deal {event.object_id} was deleted/archived")


# =============================================================================
# EXCEPTIONS
# =============================================================================

class HubSpotError(Exception):
    """Base exception for HubSpot errors."""
    pass


class HubSpotAuthError(HubSpotError):
    """Authentication/authorization error."""
    pass


class HubSpotAPIError(HubSpotError):
    """API request error."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 0,
        details: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class HubSpotConnectionError(HubSpotError):
    """Connection/network error."""
    pass


# =============================================================================
# STREAMLIT INTEGRATION
# =============================================================================

def get_hubspot_client() -> Optional[HubSpotClient]:
    """
    Get HubSpot client from Streamlit session state or environment.
    
    Returns:
        HubSpotClient instance or None if not configured
    """
    import streamlit as st
    
    # Check session state first
    if "hubspot_client" in st.session_state:
        return st.session_state.hubspot_client
    
    # Check environment variables
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if access_token:
        client = HubSpotClient(access_token=access_token)
        st.session_state.hubspot_client = client
        return client
    
    return None


def render_hubspot_status() -> None:
    """Render HubSpot connection status widget in Streamlit."""
    import streamlit as st
    
    client = get_hubspot_client()
    
    if client:
        status = client.test_connection()
        if status["connected"]:
            st.success(f"✓ Connected to HubSpot ({status.get('hub_domain', 'Unknown')})")
        else:
            st.error(f"✗ Connection failed: {status.get('error', 'Unknown error')}")
    else:
        st.warning("HubSpot not configured. Set HUBSPOT_ACCESS_TOKEN in environment.")


# =============================================================================
# CLI / TESTING
# =============================================================================

if __name__ == "__main__":
    # Test connection
    client = HubSpotClient()
    
    print("Testing HubSpot connection...")
    status = client.test_connection()
    
    if status["connected"]:
        print(f"✓ Connected to portal: {status['portal_id']}")
        print(f"  Domain: {status['hub_domain']}")
        
        # List some deals
        print("\nFetching deals...")
        deals, _ = client.list_deals(limit=5)
        for deal in deals:
            print(f"  - {deal.name}: ${deal.amount:,.0f} ({deal.stage})")
    else:
        print(f"✗ Connection failed: {status['error']}")
