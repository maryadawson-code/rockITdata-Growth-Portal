"""
AMANDA™ Portal Configuration
=============================
Brand constants, role definitions, and system configuration.

Author: rockITdata LLC
Version: 2.0.0
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

# =============================================================================
# BRAND CONSTANTS
# =============================================================================

BRAND = {
    "name": "rockITdata",
    "product": "AMANDA™",
    "tagline": "Driven by Innovation, Built on Trust",
    "full_name": "Putting Answers at Your Fingertips™",
}

COLORS = {
    "primary": "#990000",
    "primary_light": "#B31B1B",
    "primary_dark": "#7A0000",
    "background": "#FFFFFF",
    "surface": "#F8FAFC",
    "surface_alt": "#F1F5F9",
    "border": "#E2E8F0",
    "text_primary": "#1E293B",
    "text_secondary": "#64748B",
    "text_muted": "#94A3B8",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6",
}

PHASE_COLORS = {
    "P0": "#6B7280",  # Gray
    "P1": "#3B82F6",  # Blue
    "P2": "#8B5CF6",  # Purple
    "P3": "#F59E0B",  # Amber
    "P4": "#10B981",  # Green
}

PHASE_NAMES = {
    "P0": "Qualification",
    "P1": "Capture Planning",
    "P2": "Kickoff & Shredding",
    "P3": "Proposal Development",
    "P4": "Final QA",
}

REVIEW_COLORS = {
    "BLUE": "#06B6D4",
    "PINK": "#EC4899",
    "RED": "#EF4444",
    "GOLD": "#F59E0B",
}

# =============================================================================
# ROLE DEFINITIONS (11 Roles per v5 FINAL spec)
# =============================================================================

class RoleType(Enum):
    INTERNAL = "Internal"
    EXTERNAL = "External"


@dataclass
class RoleConfig:
    """Configuration for a user role."""
    id: str
    name: str
    type: RoleType
    icon: str
    description: str
    can_access_dashboard: bool = False
    can_access_war_room: bool = False
    can_approve_gates: bool = False
    can_view_pricing: bool = False
    can_view_strategy: bool = False
    can_config_system: bool = False
    can_manage_partners: bool = False
    trigger_stages: list = field(default_factory=list)


ROLES: dict[str, RoleConfig] = {
    "admin": RoleConfig(
        id="admin",
        name="Admin",
        type=RoleType.INTERNAL,
        icon="👩‍💼",
        description="System owner with full access",
        can_access_dashboard=True,
        can_access_war_room=True,
        can_approve_gates=True,
        can_view_pricing=True,
        can_view_strategy=True,
        can_config_system=True,
        can_manage_partners=True,
        trigger_stages=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    ),
    "coo": RoleConfig(
        id="coo",
        name="COO/President",
        type=RoleType.INTERNAL,
        icon="👨‍💼",
        description="Executive oversight, portfolio management",
        can_access_dashboard=True,
        can_access_war_room=True,
        can_approve_gates=True,
        can_view_pricing=True,
        can_view_strategy=True,
        trigger_stages=[1, 7, 8],
    ),
    "capture_lead": RoleConfig(
        id="capture_lead",
        name="Capture Lead",
        type=RoleType.INTERNAL,
        icon="🎯",
        description="Strategy, partners, gate ownership",
        can_access_dashboard=True,
        can_access_war_room=True,
        can_approve_gates=True,
        can_view_pricing=True,
        can_view_strategy=True,
        can_manage_partners=True,
        trigger_stages=[1, 2, 3, 6],
    ),
    "pm": RoleConfig(
        id="pm",
        name="Proposal Manager",
        type=RoleType.INTERNAL,
        icon="📋",
        description="Execution, team coordination, schedule",
        can_access_war_room=True,
        can_approve_gates=True,
        trigger_stages=[3, 4, 5, 6, 7, 8, 9],
    ),
    "finance": RoleConfig(
        id="finance",
        name="Finance",
        type=RoleType.INTERNAL,
        icon="💰",
        description="Pricing, margins, rate verification",
        can_access_dashboard=True,
        can_access_war_room=True,
        can_approve_gates=True,
        can_view_pricing=True,
        trigger_stages=[5, 7],
    ),
    "contracts": RoleConfig(
        id="contracts",
        name="Contracts",
        type=RoleType.INTERNAL,
        icon="📜",
        description="T&Cs, FAR/DFARS compliance, risk",
        can_access_war_room=True,
        can_approve_gates=True,
        trigger_stages=[4, 5, 7, 8],
    ),
    "hr": RoleConfig(
        id="hr",
        name="HR",
        type=RoleType.INTERNAL,
        icon="👤",
        description="Personnel, resumes, clearances",
        trigger_stages=[3, 4],
    ),
    "analyst": RoleConfig(
        id="analyst",
        name="Analyst/Writer",
        type=RoleType.INTERNAL,
        icon="✍️",
        description="Content creation, section writing",
        can_access_war_room=True,
        trigger_stages=[3, 4, 5, 6],
    ),
    "partner": RoleConfig(
        id="partner",
        name="Partner (Service)",
        type=RoleType.EXTERNAL,
        icon="🤝",
        description="Teaming partner providing services",
        trigger_stages=[4, 5, 6],
    ),
    "vendor": RoleConfig(
        id="vendor",
        name="Vendor (Product)",
        type=RoleType.EXTERNAL,
        icon="📦",
        description="Product vendor providing goods",
        trigger_stages=[4, 5],
    ),
    "consultant": RoleConfig(
        id="consultant",
        name="Consultant",
        type=RoleType.EXTERNAL,
        icon="🎓",
        description="Subject matter expert",
        trigger_stages=[5, 6],
    ),
}

# =============================================================================
# AI ASSISTANT CONFIGURATIONS
# =============================================================================

@dataclass
class StarterPrompt:
    """A clickable starter prompt."""
    title: str
    description: str
    prompt_template: str
    icon: str


@dataclass
class BotConfig:
    """Configuration for an AI assistant bot."""
    id: str
    name: str
    icon: str
    tagline: str
    description: str
    color: str
    system_prompt: str
    starters: list[StarterPrompt] = field(default_factory=list)
    is_private: bool = False
    allowed_roles: list[str] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)


BOTS: dict[str, BotConfig] = {
    "capture": BotConfig(
        id="capture",
        name="Capture Assistant",
        icon="🎯",
        tagline="Win strategy & competitive intelligence",
        description="Develop win themes, analyze competitors, craft discriminators.",
        color="purple",
        is_private=True,
        allowed_roles=["admin", "coo", "capture_lead"],
        phases=["P0", "P1"],
        system_prompt="""You are a Capture Strategy expert for rockITdata, a SDVOSB/WOSB federal contractor specializing in healthcare IT.

Your expertise includes:
- Developing compelling win themes and discriminators
- Competitive intelligence and ghost competitor analysis
- Customer hot button identification
- pWin assessment and improvement strategies
- Teaming strategy and partner selection

Structure responses with:
1. Strategic Assessment
2. Recommended Actions
3. Risk Factors
4. Success Metrics

Always tie recommendations to specific evaluation criteria when known.""",
        starters=[
            StarterPrompt(
                title="Develop Win Themes",
                description="Create evaluator-focused messaging",
                prompt_template="Help me develop 3 compelling win themes for [OPPORTUNITY NAME].\n\nCustomer: [AGENCY]\nKey Hot Buttons:\n1. \n2. \n\nOur Strengths:\n1. \n2. ",
                icon="🏆"
            ),
            StarterPrompt(
                title="Ghost Competitors",
                description="Predict competitor positioning",
                prompt_template="Create ghost profiles for likely competitors on [OPPORTUNITY]:\n\nCompetitors: [LIST]\n\nIdentify their probable win themes, weaknesses, and how we counter.",
                icon="👻"
            ),
            StarterPrompt(
                title="pWin Assessment",
                description="Evaluate probability of win",
                prompt_template="Assess our pWin for [OPPORTUNITY]:\n\nCustomer Relationship: [1-5]\nSolution Fit: [1-5]\nPrice Competitiveness: [1-5]\nPast Performance: [1-5]\n\nProvide improvement recommendations.",
                icon="📊"
            ),
        ]
    ),
    "drafting": BotConfig(
        id="drafting",
        name="Proposal Writer",
        icon="📝",
        tagline="Compelling federal proposal content",
        description="Draft sections, executive summaries, and technical volumes.",
        color="blue",
        allowed_roles=["admin", "coo", "capture_lead", "pm", "analyst", "hr"],
        phases=["P2", "P3", "P4"],
        system_prompt="""You are an expert federal proposal writer for rockITdata, a SDVOSB/WOSB government contractor.

Your expertise includes:
- Writing compelling executive summaries and technical volumes
- Aligning responses with PWS/SOW requirements
- Using Shipley methodology for proposal development
- Creating clear, compliant, and compelling content
- Incorporating win themes and discriminators

Always:
- Reference specific solicitation sections
- Include proof points with metrics
- Use active voice and action verbs
- Follow the Feature → Benefit → Proof structure""",
        starters=[
            StarterPrompt(
                title="Draft Executive Summary",
                description="Create compelling exec summary",
                prompt_template="Draft an Executive Summary for [AGENCY] [CONTRACT].\n\nWin Themes:\n1. \n2. \n\nKey Discriminators:\n1. \n2. ",
                icon="✨"
            ),
            StarterPrompt(
                title="Write Technical Section",
                description="Draft a technical approach section",
                prompt_template="Write the technical approach for [SECTION TITLE].\n\nRequirement: [PASTE L/M TEXT]\n\nOur Solution: [BRIEF DESCRIPTION]",
                icon="📄"
            ),
            StarterPrompt(
                title="Past Performance Write-up",
                description="Create compelling PP narrative",
                prompt_template="Write a past performance narrative for [CONTRACT NAME].\n\nClient: [AGENCY]\nValue: $[X]M\nKey Achievements:\n1. \n2. ",
                icon="🏅"
            ),
        ]
    ),
    "compliance": BotConfig(
        id="compliance",
        name="Compliance Checker",
        icon="🛡️",
        tagline="Never miss a requirement",
        description="Validate against Section L/M and FAR/DFARS.",
        color="green",
        allowed_roles=["admin", "coo", "capture_lead", "pm", "contracts", "analyst"],
        phases=["P2", "P3", "P4"],
        system_prompt="""You are a Compliance Specialist for federal proposals at rockITdata.

Your expertise includes:
- Validating against Section L (Instructions) and Section M (Evaluation Criteria)
- FAR/DFARS clause compliance verification
- Format requirements (page limits, fonts, margins)
- Identifying gaps between requirements and responses

Flag issues with severity:
- 🔴 CRITICAL: Will result in non-compliance/rejection
- 🟡 MAJOR: Significant weakness, needs attention
- 🟢 MINOR: Polish item, nice to have

Always provide specific remediation steps.""",
        starters=[
            StarterPrompt(
                title="Validate Section L/M",
                description="Check against instructions",
                prompt_template="Review this draft against Section L/M:\n\nRequirements:\n[PASTE L/M]\n\nDraft:\n[PASTE DRAFT]",
                icon="✅"
            ),
            StarterPrompt(
                title="Shred RFP",
                description="Extract all requirements",
                prompt_template="Shred this PWS and create a requirements matrix:\n\n[PASTE PWS TEXT]\n\nIdentify all SHALL, SHOULD, and MAY statements.",
                icon="🎯"
            ),
            StarterPrompt(
                title="Pre-Submission Check",
                description="Final compliance review",
                prompt_template="Run final compliance check:\n\nPage Limit: [X]\nFont: [X]\nMargins: [X]\n\nVolumes to check: [LIST]",
                icon="📋"
            ),
        ]
    ),
    "red_team": BotConfig(
        id="red_team",
        name="Red Team Reviewer",
        icon="🎭",
        tagline="Evaluator's perspective",
        description="Harsh but constructive proposal critique.",
        color="red",
        is_private=True,
        allowed_roles=["admin", "coo", "capture_lead", "pm"],
        phases=["P3"],
        system_prompt="""You are a skeptical government evaluator conducting a Red Team review.

Your role is to:
- Critique proposals harshly but constructively
- Identify unsupported claims and vague language
- Find gaps in evaluation criteria compliance
- Score sections using SSEB methodology
- Provide specific, actionable improvement recommendations

Rate each section:
- Outstanding (Blue): Exceeds requirements, no weaknesses
- Good (Purple): Meets requirements, minor weaknesses
- Acceptable (Green): Meets minimum, moderate weaknesses
- Marginal (Yellow): Barely acceptable, significant weaknesses
- Unacceptable (Red): Fails to meet requirements

Be direct. Government evaluators have hundreds of proposals to review.""",
        starters=[
            StarterPrompt(
                title="Red Team Review",
                description="Full section critique",
                prompt_template="Red Team this section:\n\nEvaluation Criteria:\n[PASTE M SECTION]\n\nDraft Section:\n[PASTE DRAFT]",
                icon="🔴"
            ),
            StarterPrompt(
                title="Score Proposal",
                description="SSEB-style scoring",
                prompt_template="Score this proposal section using SSEB methodology:\n\n[PASTE SECTION]\n\nProvide strengths, weaknesses, and overall color rating.",
                icon="📊"
            ),
        ]
    ),
    "pricing": BotConfig(
        id="pricing",
        name="Pricing Analyst",
        icon="💵",
        tagline="Cost modeling & margin protection",
        description="BOE development, rate analysis, pricing strategy.",
        color="emerald",
        is_private=True,
        allowed_roles=["admin", "coo", "capture_lead", "finance"],
        phases=["P2", "P3", "P4"],
        system_prompt="""You are a Pricing Analyst for federal proposals at rockITdata.

Your expertise includes:
- Basis of Estimate (BOE) development
- Labor category mapping and rate analysis
- Wrap rate calculations
- Margin modeling and protection
- Price-to-win strategies
- Cost realism analysis

Always flag:
- Rates outside approved ranges
- Margin below targets
- Unsubstantiated estimates
- Compliance with pricing instructions""",
        starters=[
            StarterPrompt(
                title="Build BOE",
                description="Create Basis of Estimate",
                prompt_template="Help build a BOE for [TASK/CLIN]:\n\nScope: [DESCRIPTION]\nDuration: [X months]\nLabor Categories: [LIST]",
                icon="📊"
            ),
            StarterPrompt(
                title="Rate Analysis",
                description="Verify labor rates",
                prompt_template="Analyze these proposed rates against market:\n\n[PASTE RATE TABLE]\n\nContract Type: [FFP/T&M/CPFF]",
                icon="💰"
            ),
        ]
    ),
    "contracts": BotConfig(
        id="contracts",
        name="Contracts Advisor",
        icon="📜",
        tagline="FAR/DFARS compliance & risk",
        description="T&C review, clause analysis, contract risk.",
        color="slate",
        is_private=True,
        allowed_roles=["admin", "contracts"],
        phases=["P1", "P2", "P3", "P4"],
        system_prompt="""You are a Contracts Specialist for federal proposals at rockITdata.

Your expertise includes:
- FAR/DFARS clause interpretation
- Terms and conditions review
- Contract type implications (FFP, T&M, CPFF, IDIQ)
- Teaming Agreement review
- NDA and IP protection
- Set-aside compliance (SDVOSB, WOSB, 8(a))

Flag risks with impact levels and recommend mitigations.
Always cite specific FAR/DFARS references.""",
        starters=[
            StarterPrompt(
                title="Review T&Cs",
                description="Analyze contract terms",
                prompt_template="Review these T&Cs for risk:\n\n[PASTE TERMS]\n\nHighlight unusual or high-risk clauses.",
                icon="⚠️"
            ),
            StarterPrompt(
                title="FAR Compliance",
                description="Check clause compliance",
                prompt_template="Verify compliance with these FAR clauses:\n\n[LIST CLAUSES]\n\nContract Type: [X]\nSet-Aside: [X]",
                icon="📋"
            ),
        ]
    ),
    "general": BotConfig(
        id="general",
        name="General Assistant",
        icon="💬",
        tagline="Your AI helper for any task",
        description="General-purpose assistant for any question.",
        color="gray",
        allowed_roles=list(ROLES.keys()),
        phases=["P0", "P1", "P2", "P3", "P4"],
        system_prompt="""You are AMANDA™ (Putting Answers at Your Fingertips), the AI assistant for rockITdata's proposal operations.

You help with:
- General questions about proposals and capture
- Federal contracting guidance
- Document formatting and editing
- Research and analysis
- Any other task to support the team

Be helpful, professional, and concise. If a specialized assistant would be better suited for the task, recommend it.""",
        starters=[
            StarterPrompt(
                title="Ask Anything",
                description="General question",
                prompt_template="",
                icon="💬"
            ),
        ]
    ),
}

# =============================================================================
# GATE DEFINITIONS
# =============================================================================

@dataclass
class GateConfig:
    """Configuration for a workflow gate."""
    id: str
    name: str
    phase: str
    description: str
    approvers: list[str]
    checklist: list[str]


GATES: list[GateConfig] = [
    GateConfig(
        id="G1",
        name="Gate 1: Bid/No-Bid",
        phase="P0",
        description="Executive decision to pursue opportunity",
        approvers=["coo", "capture_lead"],
        checklist=["pWin Analysis Complete", "Resource Availability Confirmed", "Strategic Fit Verified", "Customer Relationship Assessed"],
    ),
    GateConfig(
        id="G2",
        name="Gate 2: Capture Complete",
        phase="P1",
        description="Capture strategy finalized, ready for kickoff",
        approvers=["capture_lead", "pm"],
        checklist=["Win Strategy Documented", "Teaming Partners Confirmed", "Customer Intel Compiled", "Competitive Analysis Done"],
    ),
    GateConfig(
        id="G3",
        name="Gate 3: Kickoff Ready",
        phase="P2",
        description="Team assembled, schedule locked, compliance matrix ready",
        approvers=["pm", "contracts"],
        checklist=["RFP Shredded", "Compliance Matrix Complete", "Section Assignments Made", "Schedule Locked"],
    ),
    GateConfig(
        id="G4",
        name="Gate 4: Development Complete",
        phase="P3",
        description="All volumes drafted, color team reviews complete",
        approvers=["pm", "capture_lead"],
        checklist=["Pink Team Complete", "Red Team Complete", "All Critical Issues Resolved", "Final Drafts Ready"],
    ),
    GateConfig(
        id="G5",
        name="Gate 5: Submission Ready",
        phase="P4",
        description="Gold team passed, package complete, ready to submit",
        approvers=["coo", "contracts", "pm"],
        checklist=["Gold Team Passed", "Final Compliance Check", "Package Assembled", "Submission Method Confirmed"],
    ),
]

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

PAGES = {
    "dashboard": {"name": "Dashboard", "icon": "📊", "restricted": False},
    "deals": {"name": "Deals Pipeline", "icon": "📈", "restricted": False},
    "workflows": {"name": "Workflows", "icon": "🔀", "restricted": False},
    "artifacts": {"name": "Artifacts", "icon": "📁", "restricted": False},
    "compliance": {"name": "Compliance", "icon": "🛡️", "restricted": False},
    "reviews": {"name": "Reviews", "icon": "👁️", "restricted": False},
    "partners": {"name": "Partners", "icon": "🤝", "restricted": False},
    "playbook": {"name": "Playbook", "icon": "📖", "restricted": False},
    "chat": {"name": "AI Chat", "icon": "💬", "restricted": False},
    "admin": {"name": "Admin", "icon": "⚙️", "restricted": True},
}
