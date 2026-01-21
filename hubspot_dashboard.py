"""
HubSpot Dashboard Component for AMANDA Portal
==============================================
Admin UI for managing HubSpot CRM integration.

Author: rockITdata LLC
Version: 7.3 (Phase 1B)
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os

# Import HubSpot connector (handle gracefully if not available)
try:
    from hubspot_connector import (
        HubSpotClient,
        HubSpotSyncService,
        HubSpotDeal,
        SyncResult,
        get_hubspot_client,
    )
    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False


# =============================================================================
# STYLING
# =============================================================================

HUBSPOT_ORANGE = "#FF7A59"

HUBSPOT_STYLES = """
<style>
.hubspot-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}

.hubspot-logo {
    width: 32px;
    height: 32px;
}

.connection-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 500;
}

.connection-badge.connected {
    background: #DCFCE7;
    color: #166534;
}

.connection-badge.disconnected {
    background: #FEE2E2;
    color: #991B1B;
}

.connection-badge.connecting {
    background: #FEF3C7;
    color: #92400E;
}

.sync-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

.sync-stat {
    text-align: center;
}

.sync-stat-value {
    font-size: 28px;
    font-weight: 700;
    color: #1E293B;
}

.sync-stat-label {
    font-size: 12px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.deal-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-bottom: 8px;
}

.deal-name {
    font-weight: 600;
    color: #1E293B;
}

.deal-amount {
    color: #059669;
    font-weight: 600;
}

.deal-stage {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #F1F5F9;
    color: #475569;
}

.error-banner {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 8px;
    padding: 12px 16px;
    color: #991B1B;
    margin-bottom: 16px;
}

.success-banner {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 8px;
    padding: 12px 16px;
    color: #166534;
    margin-bottom: 16px;
}
</style>
"""


# =============================================================================
# SESSION STATE
# =============================================================================

def init_hubspot_state() -> None:
    """Initialize HubSpot-related session state."""
    defaults = {
        "hubspot_connected": False,
        "hubspot_status": None,
        "hubspot_last_sync": None,
        "hubspot_sync_result": None,
        "hubspot_deals": [],
        "hubspot_config": {
            "access_token": "",
            "portal_id": "",
            "pipeline_id": "",
        },
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# CONNECTION MANAGEMENT
# =============================================================================

def test_hubspot_connection(access_token: str) -> Dict[str, Any]:
    """
    Test HubSpot connection with provided token.
    
    Args:
        access_token: HubSpot Private App access token
        
    Returns:
        Connection status dictionary
    """
    if not HUBSPOT_AVAILABLE:
        return {"connected": False, "error": "HubSpot connector module not available"}
    
    try:
        client = HubSpotClient(access_token=access_token)
        return client.test_connection()
    except Exception as e:
        return {"connected": False, "error": str(e)}


def connect_hubspot(access_token: str) -> bool:
    """
    Establish HubSpot connection and store in session.
    
    Args:
        access_token: HubSpot Private App access token
        
    Returns:
        True if connection successful
    """
    status = test_hubspot_connection(access_token)
    
    if status["connected"]:
        st.session_state.hubspot_connected = True
        st.session_state.hubspot_status = status
        st.session_state.hubspot_client = HubSpotClient(access_token=access_token)
        
        # Store token securely (in production, use secrets management)
        st.session_state.hubspot_config["access_token"] = access_token
        st.session_state.hubspot_config["portal_id"] = status.get("portal_id", "")
        
        return True
    
    return False


def disconnect_hubspot() -> None:
    """Disconnect HubSpot and clear session state."""
    st.session_state.hubspot_connected = False
    st.session_state.hubspot_status = None
    st.session_state.hubspot_client = None
    st.session_state.hubspot_deals = []
    st.session_state.hubspot_config["access_token"] = ""


# =============================================================================
# SYNC OPERATIONS
# =============================================================================

def sync_deals_from_hubspot() -> Optional[SyncResult]:
    """
    Pull deals from HubSpot.
    
    Returns:
        SyncResult or None if failed
    """
    if not st.session_state.hubspot_connected:
        return None
    
    try:
        client = st.session_state.hubspot_client
        deals, _ = client.list_deals(limit=100)
        
        st.session_state.hubspot_deals = deals
        st.session_state.hubspot_last_sync = datetime.utcnow().isoformat()
        
        return SyncResult(
            success=True,
            deals_synced=len(deals),
        )
        
    except Exception as e:
        return SyncResult(
            success=False,
            errors=[str(e)],
        )


def push_deal_to_hubspot(deal_data: Dict) -> Optional[str]:
    """
    Push a single deal to HubSpot.
    
    Args:
        deal_data: AMANDA deal dictionary
        
    Returns:
        HubSpot deal ID or None if failed
    """
    if not st.session_state.hubspot_connected:
        return None
    
    try:
        client = st.session_state.hubspot_client
        
        deal = HubSpotDeal(
            name=deal_data.get("name", ""),
            amount=deal_data.get("value", 0),
            amanda_pwin=deal_data.get("pwin", 0),
            amanda_gate_status=deal_data.get("gate_status", "PENDING"),
            amanda_phase=deal_data.get("phase", "qualification"),
            amanda_agency=deal_data.get("agency", ""),
            amanda_solicitation_number=deal_data.get("solicitation", ""),
            amanda_priority_tier=deal_data.get("priority", "P-2"),
        )
        
        if deal_data.get("hubspot_deal_id"):
            # Update existing
            updated = client.update_deal(deal_data["hubspot_deal_id"], deal)
            return updated.id
        else:
            # Create new
            created = client.create_deal(deal)
            return created.id
            
    except Exception as e:
        st.error(f"Failed to sync deal: {e}")
        return None


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_connection_status() -> None:
    """Render connection status badge."""
    if st.session_state.hubspot_connected:
        status = st.session_state.hubspot_status
        st.markdown(f"""
            <div class="connection-badge connected">
                <span>●</span>
                <span>Connected to {status.get('hub_domain', 'HubSpot')}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="connection-badge disconnected">
                <span>●</span>
                <span>Not Connected</span>
            </div>
        """, unsafe_allow_html=True)


def render_connection_form() -> None:
    """Render HubSpot connection configuration form."""
    st.subheader("🔧 Connection Settings")
    
    with st.form("hubspot_connection_form"):
        st.markdown("""
        **To connect HubSpot:**
        1. Go to HubSpot → Settings → Integrations → Private Apps
        2. Create a new Private App with these scopes:
           - `crm.objects.deals.read`
           - `crm.objects.deals.write`
           - `crm.schemas.deals.read`
        3. Copy the Access Token below
        """)
        
        access_token = st.text_input(
            "Access Token",
            type="password",
            placeholder="pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            help="Your HubSpot Private App access token",
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submitted = st.form_submit_button("Connect", type="primary")
        
        if submitted and access_token:
            with st.spinner("Testing connection..."):
                if connect_hubspot(access_token):
                    st.success("✓ Connected successfully!")
                    st.rerun()
                else:
                    st.error("✗ Connection failed. Please check your access token.")


def render_sync_stats() -> None:
    """Render sync statistics cards."""
    deals = st.session_state.hubspot_deals
    last_sync = st.session_state.hubspot_last_sync
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="sync-card">
                <div class="sync-stat">
                    <div class="sync-stat-value">{len(deals)}</div>
                    <div class="sync-stat-label">Total Deals</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        open_deals = len([d for d in deals if d.stage not in ["closedwon", "closedlost"]])
        st.markdown(f"""
            <div class="sync-card">
                <div class="sync-stat">
                    <div class="sync-stat-value">{open_deals}</div>
                    <div class="sync-stat-label">Open Deals</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_value = sum(d.amount for d in deals if d.stage not in ["closedlost"])
        st.markdown(f"""
            <div class="sync-card">
                <div class="sync-stat">
                    <div class="sync-stat-value">${total_value:,.0f}</div>
                    <div class="sync-stat-label">Pipeline Value</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if last_sync:
            sync_time = datetime.fromisoformat(last_sync)
            time_ago = datetime.utcnow() - sync_time
            if time_ago.seconds < 60:
                time_str = "Just now"
            elif time_ago.seconds < 3600:
                time_str = f"{time_ago.seconds // 60}m ago"
            else:
                time_str = f"{time_ago.seconds // 3600}h ago"
        else:
            time_str = "Never"
        
        st.markdown(f"""
            <div class="sync-card">
                <div class="sync-stat">
                    <div class="sync-stat-value" style="font-size: 18px;">{time_str}</div>
                    <div class="sync-stat-label">Last Sync</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_deals_table() -> None:
    """Render deals from HubSpot."""
    deals = st.session_state.hubspot_deals
    
    if not deals:
        st.info("No deals synced yet. Click 'Sync Now' to pull deals from HubSpot.")
        return
    
    st.subheader("📊 Synced Deals")
    
    # Search/filter
    search = st.text_input("🔍 Search deals", placeholder="Filter by name, agency...")
    
    filtered_deals = deals
    if search:
        search_lower = search.lower()
        filtered_deals = [
            d for d in deals
            if search_lower in d.name.lower() or search_lower in d.amanda_agency.lower()
        ]
    
    # Display deals
    for deal in filtered_deals[:20]:  # Limit to 20 for performance
        stage_colors = {
            "closedwon": ("🏆", "#059669", "#DCFCE7"),
            "closedlost": ("❌", "#DC2626", "#FEE2E2"),
            "contractsent": ("📝", "#7C3AED", "#EDE9FE"),
            "qualifiedtobuy": ("✓", "#2563EB", "#DBEAFE"),
        }
        
        icon, color, bg = stage_colors.get(deal.stage, ("📋", "#475569", "#F1F5F9"))
        
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{deal.name}**")
            st.caption(f"{deal.amanda_agency} • {deal.amanda_solicitation_number}")
        
        with col2:
            st.markdown(f"<span style='color: #059669; font-weight: 600;'>${deal.amount:,.0f}</span>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"<span style='background: {bg}; color: {color}; padding: 2px 8px; border-radius: 4px; font-size: 12px;'>{icon} {deal.stage}</span>", unsafe_allow_html=True)
        
        with col4:
            if deal.amanda_pwin > 0:
                st.progress(deal.amanda_pwin / 100, text=f"{deal.amanda_pwin:.0f}%")
            else:
                st.caption("—")
        
        with col5:
            st.caption(deal.amanda_gate_status)
        
        st.divider()


def render_sync_actions() -> None:
    """Render sync action buttons."""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("🔄 Sync Now", type="primary", use_container_width=True):
            with st.spinner("Syncing deals from HubSpot..."):
                result = sync_deals_from_hubspot()
                if result and result.success:
                    st.success(f"✓ Synced {result.deals_synced} deals")
                    st.rerun()
                else:
                    st.error(f"Sync failed: {result.errors if result else 'Unknown error'}")
    
    with col2:
        if st.button("📤 Push All", use_container_width=True):
            st.info("Push AMANDA deals to HubSpot (coming soon)")
    
    with col3:
        if st.button("⚙️ Setup Properties", use_container_width=True):
            if st.session_state.hubspot_connected:
                with st.spinner("Creating AMANDA custom properties..."):
                    try:
                        client = st.session_state.hubspot_client
                        client.create_amanda_properties()
                        st.success("✓ AMANDA properties created in HubSpot!")
                    except Exception as e:
                        st.error(f"Failed to create properties: {e}")
            else:
                st.warning("Connect to HubSpot first")
    
    with col4:
        if st.session_state.hubspot_connected:
            if st.button("🔌 Disconnect", type="secondary"):
                disconnect_hubspot()
                st.rerun()


def render_webhook_config() -> None:
    """Render webhook configuration section."""
    with st.expander("🔔 Webhook Configuration (Advanced)"):
        st.markdown("""
        **Real-time sync with HubSpot Webhooks**
        
        To receive real-time deal updates from HubSpot:
        
        1. In HubSpot, go to Settings → Integrations → Private Apps
        2. Select your AMANDA app → Webhooks
        3. Create subscription for `deal.propertyChange`
        4. Set target URL to:
        """)
        
        # Get the app URL (would come from environment in production)
        app_url = os.getenv("APP_URL", "https://your-app.streamlit.app")
        webhook_url = f"{app_url}/api/hubspot/webhook"
        
        st.code(webhook_url, language=None)
        
        st.markdown("""
        5. Copy the Webhook Secret and add it to your environment:
        """)
        
        st.code("HUBSPOT_WEBHOOK_SECRET=your-webhook-secret", language="bash")
        
        # Show current webhook secret status
        webhook_secret = os.getenv("HUBSPOT_WEBHOOK_SECRET")
        if webhook_secret:
            st.success("✓ Webhook secret configured")
        else:
            st.warning("⚠ Webhook secret not configured")


# =============================================================================
# MAIN DASHBOARD
# =============================================================================

def render_hubspot_dashboard() -> None:
    """
    Render the complete HubSpot integration dashboard.
    Call this from your main app.py admin section.
    """
    init_hubspot_state()
    
    # Inject styles
    st.markdown(HUBSPOT_STYLES, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="hubspot-header">
            <svg class="hubspot-logo" viewBox="0 0 24 24" fill="#FF7A59">
                <path d="M18.164 7.93V5.652a2.277 2.277 0 0 0 1.31-2.054 2.293 2.293 0 0 0-4.586 0c0 .9.52 1.678 1.278 2.054V7.93a5.675 5.675 0 0 0-3.156 1.49L6.018 4.28a2.5 2.5 0 0 0 .478-1.478 2.52 2.52 0 1 0-2.52 2.52c.478 0 .92-.135 1.297-.365l6.924 5.088a5.7 5.7 0 0 0-.53 2.396c0 .862.19 1.68.53 2.413l-2.25 1.653a2.1 2.1 0 0 0-1.296-.443 2.127 2.127 0 1 0 2.127 2.127c0-.306-.068-.595-.184-.858l2.143-1.575a5.692 5.692 0 1 0 5.427-7.828zm.01 8.863a3.187 3.187 0 1 1 0-6.373 3.187 3.187 0 0 1 0 6.373z"/>
            </svg>
            <h1 style="margin: 0;">HubSpot Integration</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Connection status
    render_connection_status()
    
    st.divider()
    
    if not HUBSPOT_AVAILABLE:
        st.error("⚠️ HubSpot connector module not available. Ensure `hubspot_connector.py` is in your project.")
        return
    
    if st.session_state.hubspot_connected:
        # Sync stats
        render_sync_stats()
        
        st.divider()
        
        # Actions
        render_sync_actions()
        
        st.divider()
        
        # Deals table
        render_deals_table()
        
        # Webhook config
        render_webhook_config()
        
    else:
        # Connection form
        render_connection_form()
        
        # Info about HubSpot integration
        with st.expander("ℹ️ About HubSpot Integration"):
            st.markdown("""
            **HubSpot serves as the single source of truth for opportunity data.**
            
            ### What syncs from HubSpot → AMANDA:
            - Deal name, value, stage
            - Close date and pipeline
            - Associated contacts
            
            ### What syncs from AMANDA → HubSpot:
            - Win Probability (pWin)
            - Gate Status (GO/NO-GO)
            - Proposal Phase
            - Compliance Coverage %
            
            ### Pipeline Stage Mapping:
            
            | HubSpot Stage | AMANDA Phase | Auto-Action |
            |---------------|--------------|-------------|
            | Appointment Scheduled | Qualification | Create deal |
            | Qualified to Buy | Gate 1 | Trigger Go/No-Go |
            | Presentation Scheduled | Capture | Enable win themes |
            | Decision Maker Bought-In | Development | Unlock drafting |
            | Contract Sent | Review | Enable review cycles |
            | Closed Won | Submitted | 🎉 Aurora celebration |
            | Closed Lost | Archived | Capture lessons |
            """)


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="HubSpot Integration | AMANDA",
        page_icon="🔗",
        layout="wide",
    )
    
    render_hubspot_dashboard()
