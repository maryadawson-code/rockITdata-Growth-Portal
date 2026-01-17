"""
AMANDA™ Portal Database Layer
==============================
Mock database with seed data for demonstration.
In production, replace with Supabase/PostgreSQL connections.

Author: rockITdata LLC
Version: 2.0.0
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
import random

# =============================================================================
# ENUMS
# =============================================================================

class DealStatus(Enum):
    NEW = "NEW"
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"
    WON = "WON"
    LOST = "LOST"


class DealPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ArtifactStatus(Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    CURRENT = "CURRENT"
    ARCHIVED = "ARCHIVED"


class RequirementType(Enum):
    SHALL = "SHALL"
    SHOULD = "SHOULD"
    MAY = "MAY"
    EVAL = "EVAL"


class RequirementStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    PARTIAL = "PARTIAL"
    ADDRESSED = "ADDRESSED"


class ReviewType(Enum):
    BLUE = "BLUE"
    PINK = "PINK"
    RED = "RED"
    GOLD = "GOLD"


class ReviewStatus(Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class IssueSeverity(Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class IssueStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    WONT_FIX = "WONT_FIX"


class PartnerType(Enum):
    PRIME = "PRIME"
    MAJOR_SUB = "MAJOR_SUB"
    MINOR_SUB = "MINOR_SUB"
    VENDOR = "VENDOR"
    CONSULTANT = "CONSULTANT"


class PartnerStatus(Enum):
    PROSPECTIVE = "PROSPECTIVE"
    CONDITIONAL = "CONDITIONAL"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TAStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    NEGOTIATING = "NEGOTIATING"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"


class LessonCategory(Enum):
    WIN_THEME = "WIN_THEME"
    DISCRIMINATOR = "DISCRIMINATOR"
    BOILERPLATE = "BOILERPLATE"
    TEMPLATE = "TEMPLATE"
    BEST_PRACTICE = "BEST_PRACTICE"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Deal:
    """A pipeline opportunity/deal."""
    id: str
    name: str
    customer: str
    agency: str
    value: int
    p_win: int
    phase: str
    stage: str
    priority: DealPriority
    status: DealStatus
    due_date: str
    capture_manager: str
    proposal_manager: Optional[str] = None
    risk_score: int = 5
    description: str = ""
    solicitation_number: str = ""
    contract_type: str = "FFP"
    set_aside: str = "SDVOSB"
    naics: str = "541512"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Artifact:
    """A document artifact."""
    id: str
    name: str
    artifact_type: str
    deal_id: str
    deal_name: str
    version: str
    status: ArtifactStatus
    owner: str
    last_modified: str
    size: str
    compliance_pct: Optional[int] = None
    file_path: str = ""
    description: str = ""


@dataclass
class Requirement:
    """A compliance requirement."""
    id: str
    deal_id: str
    section: str
    text: str
    req_type: RequirementType
    status: RequirementStatus
    volume: str
    page: Optional[int] = None
    evidence_count: int = 0
    assignee: str = ""
    notes: str = ""


@dataclass
class Review:
    """A color team review."""
    id: str
    review_type: ReviewType
    deal_id: str
    deal_name: str
    status: ReviewStatus
    scheduled_date: str
    findings_count: int = 0
    critical_count: int = 0
    resolved_count: int = 0
    lead: str = ""
    participants: list = field(default_factory=list)
    notes: str = ""


@dataclass
class Issue:
    """A review issue/finding."""
    id: str
    title: str
    description: str
    severity: IssueSeverity
    status: IssueStatus
    review_id: str
    review_type: str
    deal_id: str
    deal_name: str
    assignee: str
    due_date: str
    resolution: str = ""
    created_at: str = ""


@dataclass
class Partner:
    """A teaming partner."""
    id: str
    name: str
    partner_type: PartnerType
    status: PartnerStatus
    deals: list
    workshare_pct: int
    ta_status: TAStatus
    risk_level: str
    contact_name: str
    contact_email: str = ""
    capabilities: list = field(default_factory=list)
    notes: str = ""


@dataclass
class PlaybookLesson:
    """A playbook lesson/golden example."""
    id: str
    title: str
    category: LessonCategory
    content: str
    rating: int
    uses: int
    last_used: str
    source: str
    tags: list
    created_by: str = ""
    deal_id: str = ""


@dataclass
class User:
    """A system user."""
    id: str
    name: str
    email: str
    role: str
    status: str
    last_login: str
    deals_count: int
    avatar_initials: str = ""


# =============================================================================
# SEED DATA
# =============================================================================

DEALS_DATA: list[Deal] = [
    Deal(
        id="D001",
        name="CCN Next Gen",
        customer="DHA/TMA",
        agency="DHA",
        value=850_000_000,
        p_win=75,
        phase="P3",
        stage="RED",
        priority=DealPriority.HIGH,
        status=DealStatus.ON_TRACK,
        due_date="2026-03-15",
        capture_manager="Mary Womack",
        proposal_manager="John Smith",
        risk_score=6,
        description="Next generation Community Care Network contract for TRICARE beneficiaries",
        solicitation_number="HT9402-25-R-0001",
        contract_type="IDIQ",
        set_aside="Full & Open",
    ),
    Deal(
        id="D002",
        name="EHRM Restart",
        customer="VA OIT",
        agency="VA",
        value=120_000_000,
        p_win=65,
        phase="P2",
        stage="PINK",
        priority=DealPriority.HIGH,
        status=DealStatus.AT_RISK,
        due_date="2026-04-01",
        capture_manager="John Smith",
        proposal_manager="Sarah Davis",
        risk_score=8,
        description="Electronic Health Record Modernization support services",
        solicitation_number="36C10B25R0042",
        contract_type="T&M",
        set_aside="SDVOSB",
    ),
    Deal(
        id="D003",
        name="IHT 2.0",
        customer="VA/IHS",
        agency="VA",
        value=45_000_000,
        p_win=80,
        phase="P1",
        stage="BLUE",
        priority=DealPriority.MEDIUM,
        status=DealStatus.ON_TRACK,
        due_date="2026-06-15",
        capture_manager="Mary Womack",
        risk_score=3,
        description="Interoperability & Health Technology modernization",
        solicitation_number="TBD",
        contract_type="FFP",
        set_aside="SDVOSB",
    ),
    Deal(
        id="D004",
        name="DHA Data Governance",
        customer="DHA CIO",
        agency="DHA",
        value=25_000_000,
        p_win=60,
        phase="P0",
        stage="G1",
        priority=DealPriority.LOW,
        status=DealStatus.NEW,
        due_date="2026-08-01",
        capture_manager="Sarah Davis",
        risk_score=5,
        description="Enterprise data governance and analytics platform",
        solicitation_number="TBD",
        contract_type="FFP",
        set_aside="8(a)",
    ),
    Deal(
        id="D005",
        name="PPI MEDIC Zone 2",
        customer="CMS/OIT",
        agency="CMS",
        value=180_000_000,
        p_win=55,
        phase="P1",
        stage="CAP",
        priority=DealPriority.HIGH,
        status=DealStatus.ON_TRACK,
        due_date="2026-05-20",
        capture_manager="Mary Womack",
        risk_score=7,
        description="Program & Provider Integrity MEDIC Zone 2 contract",
        solicitation_number="75FCMC25R0018",
        contract_type="CPFF",
        set_aside="Full & Open",
    ),
]

ARTIFACTS_DATA: list[Artifact] = [
    Artifact(
        id="A001",
        name="CCN Technical Volume Draft",
        artifact_type="Vol I",
        deal_id="D001",
        deal_name="CCN Next Gen",
        version="v2.3",
        status=ArtifactStatus.IN_REVIEW,
        owner="Mary Womack",
        last_modified="2026-01-14",
        size="2.4 MB",
        compliance_pct=85,
    ),
    Artifact(
        id="A002",
        name="CCN Compliance Matrix",
        artifact_type="Matrix",
        deal_id="D001",
        deal_name="CCN Next Gen",
        version="v1.8",
        status=ArtifactStatus.CURRENT,
        owner="John Smith",
        last_modified="2026-01-13",
        size="156 KB",
        compliance_pct=100,
    ),
    Artifact(
        id="A003",
        name="EHRM Win Strategy Brief",
        artifact_type="Strategy",
        deal_id="D002",
        deal_name="EHRM Restart",
        version="v1.0",
        status=ArtifactStatus.APPROVED,
        owner="Sarah Davis",
        last_modified="2026-01-10",
        size="1.1 MB",
    ),
    Artifact(
        id="A004",
        name="IHT Teaming Agreement Template",
        artifact_type="Legal",
        deal_id="D003",
        deal_name="IHT 2.0",
        version="v1.2",
        status=ArtifactStatus.DRAFT,
        owner="Legal Team",
        last_modified="2026-01-12",
        size="890 KB",
    ),
    Artifact(
        id="A005",
        name="Past Performance - DHA MIDS",
        artifact_type="PP",
        deal_id="MULTI",
        deal_name="Multiple",
        version="v3.0",
        status=ArtifactStatus.APPROVED,
        owner="Mary Womack",
        last_modified="2026-01-08",
        size="3.2 MB",
    ),
    Artifact(
        id="A006",
        name="CCN Management Volume Draft",
        artifact_type="Vol II",
        deal_id="D001",
        deal_name="CCN Next Gen",
        version="v2.1",
        status=ArtifactStatus.IN_REVIEW,
        owner="John Smith",
        last_modified="2026-01-14",
        size="1.8 MB",
        compliance_pct=78,
    ),
    Artifact(
        id="A007",
        name="CCN Past Performance Volume",
        artifact_type="Vol III",
        deal_id="D001",
        deal_name="CCN Next Gen",
        version="v1.5",
        status=ArtifactStatus.APPROVED,
        owner="Mary Womack",
        last_modified="2026-01-11",
        size="2.1 MB",
        compliance_pct=100,
    ),
]

REQUIREMENTS_DATA: list[Requirement] = [
    Requirement(
        id="REQ-001",
        deal_id="D001",
        section="L.5.1",
        text="The Offeror shall demonstrate understanding of DHA healthcare IT environment",
        req_type=RequirementType.SHALL,
        status=RequirementStatus.ADDRESSED,
        volume="Technical",
        page=12,
        evidence_count=3,
        assignee="Mary Womack",
    ),
    Requirement(
        id="REQ-002",
        deal_id="D001",
        section="L.5.2",
        text="Technical approach shall include transition-in plan not exceeding 90 days",
        req_type=RequirementType.SHALL,
        status=RequirementStatus.ADDRESSED,
        volume="Technical",
        page=24,
        evidence_count=2,
        assignee="John Smith",
    ),
    Requirement(
        id="REQ-003",
        deal_id="D001",
        section="L.5.3",
        text="Offeror should describe experience with Cerner/Oracle Health integration",
        req_type=RequirementType.SHOULD,
        status=RequirementStatus.PARTIAL,
        volume="Technical",
        evidence_count=1,
        assignee="Sarah Davis",
    ),
    Requirement(
        id="REQ-004",
        deal_id="D001",
        section="M.2.1",
        text="Technical approach will be evaluated for innovation and risk mitigation strategies",
        req_type=RequirementType.EVAL,
        status=RequirementStatus.ADDRESSED,
        volume="Technical",
        page=8,
        evidence_count=4,
        assignee="Mary Womack",
    ),
    Requirement(
        id="REQ-005",
        deal_id="D001",
        section="L.6.1",
        text="Past performance shall include minimum 3 relevant contracts of similar scope",
        req_type=RequirementType.SHALL,
        status=RequirementStatus.NOT_STARTED,
        volume="Past Perf",
        evidence_count=0,
        assignee="Mary Womack",
    ),
    Requirement(
        id="REQ-006",
        deal_id="D001",
        section="L.7.1",
        text="Key Personnel resumes shall not exceed 2 pages each",
        req_type=RequirementType.SHALL,
        status=RequirementStatus.ADDRESSED,
        volume="Management",
        page=15,
        evidence_count=5,
        assignee="HR Team",
    ),
    Requirement(
        id="REQ-007",
        deal_id="D001",
        section="L.8.1",
        text="Pricing shall be submitted using provided templates",
        req_type=RequirementType.SHALL,
        status=RequirementStatus.PARTIAL,
        volume="Pricing",
        evidence_count=1,
        assignee="Finance Team",
    ),
]

REVIEWS_DATA: list[Review] = [
    Review(
        id="RV001",
        review_type=ReviewType.PINK,
        deal_id="D001",
        deal_name="CCN Next Gen",
        status=ReviewStatus.COMPLETED,
        scheduled_date="2026-01-10",
        findings_count=12,
        critical_count=2,
        resolved_count=10,
        lead="External SME",
        participants=["Mary Womack", "John Smith", "External SME"],
    ),
    Review(
        id="RV002",
        review_type=ReviewType.RED,
        deal_id="D001",
        deal_name="CCN Next Gen",
        status=ReviewStatus.IN_PROGRESS,
        scheduled_date="2026-01-18",
        findings_count=8,
        critical_count=3,
        resolved_count=2,
        lead="John Smith",
        participants=["Mary Womack", "John Smith", "Sarah Davis"],
    ),
    Review(
        id="RV003",
        review_type=ReviewType.GOLD,
        deal_id="D001",
        deal_name="CCN Next Gen",
        status=ReviewStatus.SCHEDULED,
        scheduled_date="2026-01-25",
        findings_count=0,
        critical_count=0,
        resolved_count=0,
        lead="Mary Womack",
    ),
    Review(
        id="RV004",
        review_type=ReviewType.BLUE,
        deal_id="D002",
        deal_name="EHRM Restart",
        status=ReviewStatus.COMPLETED,
        scheduled_date="2026-01-05",
        findings_count=5,
        critical_count=0,
        resolved_count=5,
        lead="Sarah Davis",
    ),
]

ISSUES_DATA: list[Issue] = [
    Issue(
        id="ISS-001",
        title="Technical approach lacks specificity on AI governance framework",
        description="Section 3.2 discusses AI capabilities but doesn't address governance, oversight, or ethical considerations required by DHA policy.",
        severity=IssueSeverity.CRITICAL,
        status=IssueStatus.OPEN,
        review_id="RV002",
        review_type="RED",
        deal_id="D001",
        deal_name="CCN Next Gen",
        assignee="Mary Womack",
        due_date="2026-01-16",
    ),
    Issue(
        id="ISS-002",
        title="Missing clearance verification for Key Personnel #3",
        description="Resume for Program Manager does not include clearance level or verification date.",
        severity=IssueSeverity.MAJOR,
        status=IssueStatus.IN_PROGRESS,
        review_id="RV002",
        review_type="RED",
        deal_id="D001",
        deal_name="CCN Next Gen",
        assignee="HR Team",
        due_date="2026-01-17",
    ),
    Issue(
        id="ISS-003",
        title="Page count exceeds limit by 2 pages in Vol II",
        description="Management Volume is 52 pages but limit is 50. Need to trim content.",
        severity=IssueSeverity.MINOR,
        status=IssueStatus.RESOLVED,
        review_id="RV002",
        review_type="RED",
        deal_id="D001",
        deal_name="CCN Next Gen",
        assignee="John Smith",
        due_date="2026-01-15",
        resolution="Consolidated sections 4.2 and 4.3, removed redundant org chart",
    ),
    Issue(
        id="ISS-004",
        title="Win theme not consistently reinforced across volumes",
        description="Primary win theme 'Seamless Transition' appears in Tech Vol but not in Management or Executive Summary.",
        severity=IssueSeverity.MAJOR,
        status=IssueStatus.OPEN,
        review_id="RV002",
        review_type="RED",
        deal_id="D001",
        deal_name="CCN Next Gen",
        assignee="Mary Womack",
        due_date="2026-01-17",
    ),
]

PARTNERS_DATA: list[Partner] = [
    Partner(
        id="P001",
        name="TriWest Healthcare",
        partner_type=PartnerType.MAJOR_SUB,
        status=PartnerStatus.ACTIVE,
        deals=["CCN Next Gen"],
        workshare_pct=35,
        ta_status=TAStatus.EXECUTED,
        risk_level="MEDIUM",
        contact_name="Jane Wilson",
        contact_email="jane.wilson@triwest.com",
        capabilities=["Claims Processing", "Provider Network", "Care Coordination"],
    ),
    Partner(
        id="P002",
        name="Peraton",
        partner_type=PartnerType.PRIME,
        status=PartnerStatus.ACTIVE,
        deals=["PPI MEDIC Zone 2"],
        workshare_pct=60,
        ta_status=TAStatus.EXECUTED,
        risk_level="LOW",
        contact_name="Mike Johnson",
        contact_email="mike.johnson@peraton.com",
        capabilities=["Program Management", "Data Analytics", "Fraud Detection"],
    ),
    Partner(
        id="P003",
        name="TISTA Science",
        partner_type=PartnerType.MINOR_SUB,
        status=PartnerStatus.CONDITIONAL,
        deals=["IHT 2.0"],
        workshare_pct=15,
        ta_status=TAStatus.NEGOTIATING,
        risk_level="HIGH",
        contact_name="Robert Chen",
        contact_email="robert.chen@tistascience.com",
        capabilities=["Interoperability", "FHIR Implementation", "EHR Integration"],
        notes="Sized out of SB - need to verify eligibility",
    ),
    Partner(
        id="P004",
        name="Leidos",
        partner_type=PartnerType.MAJOR_SUB,
        status=PartnerStatus.PROSPECTIVE,
        deals=["DHA Data Governance"],
        workshare_pct=40,
        ta_status=TAStatus.NOT_STARTED,
        risk_level="LOW",
        contact_name="TBD",
        capabilities=["Data Governance", "Cloud Infrastructure", "Cybersecurity"],
    ),
]

PLAYBOOK_DATA: list[PlaybookLesson] = [
    PlaybookLesson(
        id="L001",
        title="DHA Modernization Win Theme",
        category=LessonCategory.WIN_THEME,
        content="""**Win Theme: Seamless Modernization, Zero Disruption**

Feature: Our proven transition methodology reduces deployment risk through parallel operations.

Benefit: DHA achieves modernization goals without impacting beneficiary care or provider workflows.

Proof: On [CONTRACT], we migrated 2.3M records with 99.97% accuracy and zero downtime, completing 30 days ahead of schedule.

**Usage Notes:**
- Emphasize 'zero disruption' for risk-averse evaluators
- Include specific metrics from past performance
- Tie to DHA's stated priority of continuity of care""",
        rating=5,
        uses=23,
        last_used="2026-01-12",
        source="CCN Original Win",
        tags=["DHA", "modernization", "transition", "healthcare"],
        created_by="Mary Womack",
    ),
    PlaybookLesson(
        id="L002",
        title="VA Interoperability Discriminator",
        category=LessonCategory.DISCRIMINATOR,
        content="""**Discriminator: Native FHIR R4 Implementation**

Unlike competitors who bolt on interoperability, our platform was built ground-up on FHIR R4 standards.

**Why It Matters:**
- 40% faster data exchange vs. legacy HL7 interfaces
- Native support for CDS Hooks and SMART on FHIR
- Pre-certified for VA Lighthouse API integration

**Proof Points:**
- First vendor certified on VA Lighthouse sandbox (2024)
- 15 production FHIR integrations across VA, DHA, IHS
- Zero failed interoperability tests in 3 years""",
        rating=4,
        uses=18,
        last_used="2026-01-10",
        source="EHRM Win",
        tags=["VA", "interoperability", "FHIR", "integration"],
        created_by="John Smith",
    ),
    PlaybookLesson(
        id="L003",
        title="SDVOSB Compliance Boilerplate",
        category=LessonCategory.BOILERPLATE,
        content="""rockITdata is a verified Service-Disabled Veteran-Owned Small Business (SDVOSB) and Woman-Owned Small Business (WOSB), registered in SAM.gov (UEI: [NUMBER]) and verified through the SBA VetCert program.

**Set-Aside Compliance:**
- Primary NAICS: 541512 (Computer Systems Design Services)
- Size Standard: $34M (compliant)
- VetCert ID: [NUMBER]
- WOSB Self-Certification: Active

**Subcontracting Approach:**
For this effort, rockITdata will perform at least [X]% of the work with our own employees, in full compliance with FAR 52.219-14 and 13 CFR 125.6.""",
        rating=5,
        uses=45,
        last_used="2026-01-14",
        source="Standard Library",
        tags=["compliance", "SDVOSB", "WOSB", "set-aside", "boilerplate"],
        created_by="Contracts Team",
    ),
    PlaybookLesson(
        id="L004",
        title="Key Personnel Resume Format",
        category=LessonCategory.TEMPLATE,
        content="""**[NAME], [TITLE]**

**Qualifications Summary**
[2-3 sentences highlighting directly relevant experience]

**Relevant Experience**

*[Contract Name] | [Client] | [Dates]*
- [Achievement with metric]
- [Achievement with metric]
- [Achievement with metric]

*[Contract Name] | [Client] | [Dates]*
- [Achievement with metric]
- [Achievement with metric]

**Education & Certifications**
- [Degree], [Institution], [Year]
- [Certification], [Year]

**Clearance:** [Level] (Current as of [Date])

---
*Format Notes:*
- Keep to 2 pages maximum
- Lead with most relevant experience
- Quantify achievements wherever possible
- Include clearance date to show currency""",
        rating=4,
        uses=31,
        last_used="2026-01-13",
        source="Best Practice",
        tags=["resume", "personnel", "format", "template"],
        created_by="HR Team",
    ),
    PlaybookLesson(
        id="L005",
        title="Transition Risk Mitigation Approach",
        category=LessonCategory.BEST_PRACTICE,
        content="""**Transition Risk Mitigation Framework**

**Phase 1: Knowledge Transfer (Days 1-30)**
- Conduct incumbent knowledge transfer sessions
- Document all processes, workflows, and tribal knowledge
- Establish baseline performance metrics

**Phase 2: Parallel Operations (Days 31-60)**
- Run parallel systems with real-time comparison
- Identify and resolve discrepancies immediately
- Train all staff on new systems/processes

**Phase 3: Cutover (Days 61-90)**
- Phased migration with rollback capability
- 24/7 war room support during transition
- Daily status reporting to Government PM

**Risk Triggers & Responses:**
| Risk | Trigger | Response |
|------|---------|----------|
| Data Loss | Any migration error | Immediate rollback, root cause analysis |
| Performance | >10% degradation | Scale resources, optimize queries |
| Staff | Key person departure | Cross-trained backup, knowledge base |""",
        rating=5,
        uses=15,
        last_used="2026-01-11",
        source="DHA MIDS Lessons Learned",
        tags=["transition", "risk", "mitigation", "methodology"],
        created_by="Mary Womack",
    ),
]

USERS_DATA: list[User] = [
    User(
        id="U001",
        name="Mary Womack",
        email="mary.womack@rockitdata.com",
        role="capture_lead",
        status="ACTIVE",
        last_login="2026-01-15 09:23",
        deals_count=4,
        avatar_initials="MW",
    ),
    User(
        id="U002",
        name="John Smith",
        email="john.smith@rockitdata.com",
        role="pm",
        status="ACTIVE",
        last_login="2026-01-15 08:45",
        deals_count=2,
        avatar_initials="JS",
    ),
    User(
        id="U003",
        name="Sarah Davis",
        email="sarah.davis@rockitdata.com",
        role="analyst",
        status="ACTIVE",
        last_login="2026-01-14 16:30",
        deals_count=3,
        avatar_initials="SD",
    ),
    User(
        id="U004",
        name="Mike Thompson",
        email="mike.thompson@rockitdata.com",
        role="finance",
        status="ACTIVE",
        last_login="2026-01-15 07:15",
        deals_count=5,
        avatar_initials="MT",
    ),
    User(
        id="U005",
        name="Lisa Chen",
        email="lisa.chen@rockitdata.com",
        role="contracts",
        status="ACTIVE",
        last_login="2026-01-14 14:20",
        deals_count=4,
        avatar_initials="LC",
    ),
    User(
        id="U006",
        name="External Partner",
        email="partner@triwest.com",
        role="partner",
        status="ACTIVE",
        last_login="2026-01-13 11:00",
        deals_count=1,
        avatar_initials="EP",
    ),
]


# =============================================================================
# DATABASE ACCESS FUNCTIONS
# =============================================================================

def get_deals() -> list[Deal]:
    """Get all deals."""
    return DEALS_DATA


def get_deal_by_id(deal_id: str) -> Optional[Deal]:
    """Get a deal by ID."""
    for deal in DEALS_DATA:
        if deal.id == deal_id:
            return deal
    return None


def get_artifacts(deal_id: Optional[str] = None) -> list[Artifact]:
    """Get artifacts, optionally filtered by deal."""
    if deal_id:
        return [a for a in ARTIFACTS_DATA if a.deal_id == deal_id or a.deal_id == "MULTI"]
    return ARTIFACTS_DATA


def get_requirements(deal_id: str) -> list[Requirement]:
    """Get requirements for a deal."""
    return [r for r in REQUIREMENTS_DATA if r.deal_id == deal_id]


def get_reviews(deal_id: Optional[str] = None) -> list[Review]:
    """Get reviews, optionally filtered by deal."""
    if deal_id:
        return [r for r in REVIEWS_DATA if r.deal_id == deal_id]
    return REVIEWS_DATA


def get_issues(deal_id: Optional[str] = None, status: Optional[str] = None) -> list[Issue]:
    """Get issues, optionally filtered."""
    issues = ISSUES_DATA
    if deal_id:
        issues = [i for i in issues if i.deal_id == deal_id]
    if status:
        issues = [i for i in issues if i.status.value == status]
    return issues


def get_partners() -> list[Partner]:
    """Get all partners."""
    return PARTNERS_DATA


def get_playbook_lessons(category: Optional[str] = None) -> list[PlaybookLesson]:
    """Get playbook lessons, optionally filtered by category."""
    if category and category != "all":
        return [l for l in PLAYBOOK_DATA if l.category.value == category]
    return PLAYBOOK_DATA


def get_users() -> list[User]:
    """Get all users."""
    return USERS_DATA


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    for user in USERS_DATA:
        if user.email == email:
            return user
    return None


# =============================================================================
# STATISTICS FUNCTIONS
# =============================================================================

def get_pipeline_stats() -> dict:
    """Get pipeline statistics."""
    deals = DEALS_DATA
    total_value = sum(d.value for d in deals)
    weighted_value = sum(d.value * d.p_win / 100 for d in deals)
    at_risk = len([d for d in deals if d.status == DealStatus.AT_RISK])
    
    return {
        "total_deals": len(deals),
        "total_value": total_value,
        "weighted_value": weighted_value,
        "at_risk_count": at_risk,
        "by_phase": {
            "P0": len([d for d in deals if d.phase == "P0"]),
            "P1": len([d for d in deals if d.phase == "P1"]),
            "P2": len([d for d in deals if d.phase == "P2"]),
            "P3": len([d for d in deals if d.phase == "P3"]),
            "P4": len([d for d in deals if d.phase == "P4"]),
        }
    }


def get_compliance_stats(deal_id: str) -> dict:
    """Get compliance statistics for a deal."""
    reqs = get_requirements(deal_id)
    if not reqs:
        return {"total": 0, "addressed": 0, "partial": 0, "not_started": 0, "coverage_pct": 0}
    
    addressed = len([r for r in reqs if r.status == RequirementStatus.ADDRESSED])
    partial = len([r for r in reqs if r.status == RequirementStatus.PARTIAL])
    not_started = len([r for r in reqs if r.status == RequirementStatus.NOT_STARTED])
    
    return {
        "total": len(reqs),
        "addressed": addressed,
        "partial": partial,
        "not_started": not_started,
        "coverage_pct": round((addressed / len(reqs)) * 100) if reqs else 0,
    }
