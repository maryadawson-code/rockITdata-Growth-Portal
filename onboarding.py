"""
AMANDA™ Portal Onboarding Tours
================================
Role-based guided walkthroughs for new users.

Author: rockITdata LLC
Version: 2.0.0
"""

from dataclasses import dataclass
from typing import Optional

# =============================================================================
# TOUR STEP DEFINITIONS
# =============================================================================

@dataclass
class TourStep:
    """A single step in the onboarding tour."""
    id: str
    title: str
    content: str
    page: str  # Which page this step relates to
    highlight: str  # What to highlight (for future use)
    tip: Optional[str] = None


# =============================================================================
# GENERAL TOUR (All Users)
# =============================================================================

GENERAL_TOUR: list[TourStep] = [
    TourStep(
        id="welcome",
        title="Welcome to AMANDA™",
        content="""
**AMANDA™** (Putting Answers at Your Fingertips) is your AI-powered proposal development assistant.

This quick tour will show you the key features. It takes about 2 minutes.

**What you can do here:**
- Track opportunities through the Shipley lifecycle
- Chat with specialized AI assistants
- Manage compliance requirements
- Collaborate with your team
        """,
        page="dashboard",
        highlight="none",
        tip="You can replay this tour anytime from the sidebar."
    ),
    TourStep(
        id="dashboard",
        title="Dashboard: Your Command Center",
        content="""
The **Dashboard** gives you an executive overview of your pipeline:

- **Pipeline Stats** – Total value, weighted value, active deals
- **Active Opportunities** – Quick view of all deals with pWin and status
- **Open Issues** – Critical items needing attention
- **Upcoming Reviews** – Scheduled color team reviews

This is your daily starting point.
        """,
        page="dashboard",
        highlight="dashboard",
        tip="Click any deal name to jump directly to its details."
    ),
    TourStep(
        id="deals",
        title="Deals Pipeline",
        content="""
The **Deals Pipeline** tracks all opportunities through the Shipley phases:

- **P0** – Qualification (Should we pursue?)
- **P1** – Capture Planning (Strategy & teaming)
- **P2** – Kickoff & Shredding (RFP analysis)
- **P3** – Proposal Development (Writing & reviews)
- **P4** – Final QA (Gold team & submission)

Each deal shows value, pWin probability, and current status.
        """,
        page="deals",
        highlight="deals",
        tip="Use filters to focus on specific phases or at-risk deals."
    ),
    TourStep(
        id="ai_chat",
        title="AI Chat: Your Smart Assistants",
        content="""
**AI Chat** connects you with 7 specialized assistants:

- **Capture Assistant** – Win themes & competitive intel
- **Proposal Writer** – Draft compelling content
- **Compliance Checker** – Validate against Section L/M
- **Red Team Reviewer** – Harsh but constructive critique
- **Pricing Analyst** – BOE & rate analysis
- **Contracts Advisor** – T&Cs and FAR/DFARS
- **General Assistant** – Any other questions

Select an assistant from the dropdown and use Quick Start prompts to begin.
        """,
        page="chat",
        highlight="chat",
        tip="Some assistants are private based on your role. Check the access badge."
    ),
    TourStep(
        id="demo_mode",
        title="Demo Mode",
        content="""
You're currently in **Demo Mode**, which means:

✓ All features work normally
✓ AI responses are simulated (no API costs)
✓ Sample data represents realistic scenarios
✓ You can explore freely without breaking anything

Toggle Demo Mode on/off in the sidebar. When off, you'll get live AI responses (requires API key).
        """,
        page="dashboard",
        highlight="sidebar",
        tip="Try running a Demo Scenario from Admin → Demo tab for a guided interaction."
    ),
    TourStep(
        id="role_switcher",
        title="Role Switcher",
        content="""
Use the **Role Switcher** in the sidebar to see how AMANDA™ looks for different users:

- **Capture Lead** – Full access including strategy bots
- **Proposal Manager** – Execution-focused view
- **Finance** – Includes pricing tools
- **Analyst** – Writing and compliance focus
- **HR** – Personnel and resume tools

Different roles see different AI assistants and features.
        """,
        page="dashboard",
        highlight="role_switcher",
        tip="Switch roles now to see how permissions change!"
    ),
    TourStep(
        id="tour_complete",
        title="You're All Set!",
        content="""
**That's the basics!** Here's what to explore next:

1. **Dashboard** – Check the pipeline overview
2. **AI Chat** – Try a Quick Start prompt
3. **Deals** – Click into CCN Next Gen to see details
4. **Workflows** – See the phase navigator in action

**Need help?** The General Assistant is always available.

**Have feedback?** We'd love to hear it – reply to the review email.
        """,
        page="dashboard",
        highlight="none",
        tip="Click 'Finish Tour' to start exploring!"
    ),
]


# =============================================================================
# ROLE-SPECIFIC TOURS
# =============================================================================

CAPTURE_LEAD_TOUR: list[TourStep] = [
    TourStep(
        id="capture_welcome",
        title="Capture Lead View",
        content="""
As a **Capture Lead**, you have full access to AMANDA™'s strategic tools:

- **Capture Assistant** – Your primary AI for win themes and competitive analysis
- **Strategy Views** – Full access to sensitive competitive intel
- **Gate Approvals** – Authority to approve capture gates (G1-G2)
- **Partner Management** – Lead teaming decisions

Let me show you the key tools for your role.
        """,
        page="dashboard",
        highlight="none"
    ),
    TourStep(
        id="capture_assistant",
        title="Your Capture Assistant",
        content="""
The **Capture Assistant** is your strategic partner for:

- **Win Theme Development** – Create evaluator-focused messaging
- **Ghost Competitors** – Predict competitor positioning
- **pWin Assessment** – Evaluate probability of win
- **Discriminator Analysis** – Identify what sets you apart

Go to AI Chat and select "Capture Assistant" to try the Quick Start prompts.
        """,
        page="chat",
        highlight="capture_bot",
        tip="This is a PRIVATE assistant – only Capture Leads, COO, and Admins can see it."
    ),
    TourStep(
        id="capture_partners",
        title="Partner Management",
        content="""
As Capture Lead, you drive **teaming strategy**:

- **Partners Page** – View all teaming partners and their status
- **Workshare** – Track percentage allocations
- **TA Status** – Monitor Teaming Agreement progress
- **Risk Levels** – Flag high-risk partners early

Build your winning team from the Partners page.
        """,
        page="partners",
        highlight="partners"
    ),
]

PROPOSAL_MANAGER_TOUR: list[TourStep] = [
    TourStep(
        id="pm_welcome",
        title="Proposal Manager View",
        content="""
As a **Proposal Manager**, you're the execution engine:

- **Workflows** – Manage phase progression and gate approvals
- **Reviews** – Coordinate color team reviews
- **Compliance** – Ensure nothing falls through the cracks
- **Artifacts** – Track all deliverables and versions

Let me show you your key tools.
        """,
        page="dashboard",
        highlight="none"
    ),
    TourStep(
        id="pm_workflows",
        title="Workflow Management",
        content="""
The **Workflows** page is your control center:

- **Phase Navigator** – Visual P0→P4 progression
- **Gate Checklists** – Track what's done and what's pending
- **Approvers** – See who needs to sign off
- **Request Approval** – Trigger gate reviews

Keep proposals moving forward on schedule.
        """,
        page="workflows",
        highlight="workflows"
    ),
    TourStep(
        id="pm_reviews",
        title="Color Team Reviews",
        content="""
Manage the review cycle from the **Reviews** page:

- **Blue Team** – Early strategy review
- **Pink Team** – First draft review
- **Red Team** – Formal compliance/quality review
- **Gold Team** – Final executive review

Track findings, assign issues, and monitor resolution.
        """,
        page="reviews",
        highlight="reviews"
    ),
]

FINANCE_TOUR: list[TourStep] = [
    TourStep(
        id="finance_welcome",
        title="Finance View",
        content="""
As **Finance**, you have access to pricing tools:

- **Pricing Analyst AI** – BOE development and rate analysis
- **Deal Values** – Full visibility into pipeline dollars
- **Margin Protection** – Tools to flag pricing risks

Let me show you the pricing capabilities.
        """,
        page="dashboard",
        highlight="none"
    ),
    TourStep(
        id="finance_pricing",
        title="Pricing Analyst Assistant",
        content="""
The **Pricing Analyst** is your AI for:

- **BOE Development** – Build Basis of Estimates
- **Rate Analysis** – Verify labor rates against market
- **Wrap Rates** – Calculate fully-loaded costs
- **Price-to-Win** – Competitive pricing strategy

Go to AI Chat and select "Pricing Analyst" to get started.
        """,
        page="chat",
        highlight="pricing_bot",
        tip="This is a PRIVATE assistant – only Finance, Capture Lead, COO, and Admins can see it."
    ),
]

ANALYST_TOUR: list[TourStep] = [
    TourStep(
        id="analyst_welcome",
        title="Analyst/Writer View",
        content="""
As an **Analyst/Writer**, you create winning content:

- **Proposal Writer AI** – Draft compelling sections
- **Compliance Checker AI** – Validate against requirements
- **Artifacts** – Access templates and past performance
- **Playbook** – Golden examples and best practices

Let me show you the writing tools.
        """,
        page="dashboard",
        highlight="none"
    ),
    TourStep(
        id="analyst_writing",
        title="Proposal Writer Assistant",
        content="""
The **Proposal Writer** helps you:

- **Draft Executive Summaries** – Compelling openings
- **Write Technical Sections** – Clear, compliant content
- **Past Performance** – Structure PP narratives
- **Feature-Benefit-Proof** – Winning format

Use the Quick Start prompts to begin drafting.
        """,
        page="chat",
        highlight="drafting_bot"
    ),
    TourStep(
        id="analyst_playbook",
        title="The Playbook",
        content="""
The **Playbook** is your library of golden examples:

- **Win Themes** – Proven messaging that won
- **Discriminators** – What sets us apart
- **Boilerplate** – Approved standard language
- **Templates** – Resume formats, section outlines

Use these as starting points – don't reinvent the wheel!
        """,
        page="playbook",
        highlight="playbook"
    ),
]


# =============================================================================
# TOUR REGISTRY
# =============================================================================

ROLE_TOURS: dict[str, list[TourStep]] = {
    "admin": GENERAL_TOUR,
    "coo": GENERAL_TOUR,
    "capture_lead": CAPTURE_LEAD_TOUR,
    "pm": PROPOSAL_MANAGER_TOUR,
    "finance": FINANCE_TOUR,
    "contracts": GENERAL_TOUR,
    "hr": GENERAL_TOUR,
    "analyst": ANALYST_TOUR,
    "partner": GENERAL_TOUR,
    "vendor": GENERAL_TOUR,
    "consultant": GENERAL_TOUR,
}


def get_tour_for_role(role: str) -> list[TourStep]:
    """Get the appropriate tour for a user role."""
    return ROLE_TOURS.get(role, GENERAL_TOUR)


def get_general_tour() -> list[TourStep]:
    """Get the general tour for all users."""
    return GENERAL_TOUR
