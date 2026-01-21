"""
rockITdata AI Portal - Main Application
========================================
A secure, role-based AI assistant portal for federal proposal development.

Author: rockITdata LLC
Version: 7.3 (Phase 1B - HubSpot Integration)
"""

import streamlit as st
from anthropic import Anthropic
from dataclasses import dataclass
from typing import Optional
import os

# =============================================================================
# HUBSPOT INTEGRATION (Phase 1B)
# =============================================================================

try:
    from hubspot_dashboard import render_hubspot_dashboard, init_hubspot_state
    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False
    def render_hubspot_dashboard():
        st.error("⚠️ HubSpot module not found. Ensure `hubspot_dashboard.py` is in your project.")
    def init_hubspot_state():
        pass

# =============================================================================
# ADMIN DASHBOARD
# =============================================================================

try:
    from admin_dashboard import render_admin_dashboard, init_admin_state
    from database import initialize as init_db, log_token_usage
    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False
    def render_admin_dashboard():
        st.error("⚠️ Admin module not found. Ensure `admin_dashboard.py` and `database.py` are in your project.")
    def init_admin_state():
        pass
    def init_db():
        pass
    def log_token_usage(*args, **kwargs):
        pass

# =============================================================================
# CONFIGURATION
# =============================================================================

# Brand colors
ROCKIT_RED = "#990000"
ROCKIT_RED_LIGHT = "#CC3333"
ROCKIT_DARK = "#1a1a2e"

# Color palette for light mode
COLORS = {
    "primary": ROCKIT_RED,
    "primary_light": "#FEE2E2",
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
    "blue": "#3B82F6",
    "green": "#10B981",
    "violet": "#8B5CF6",
    "orange": "#F97316",
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class StarterPrompt:
    """A clickable starter prompt for the zero state."""
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
    starters: list[StarterPrompt]
    is_private: bool = False


# =============================================================================
# BOT CONFIGURATIONS
# =============================================================================

BOTS: dict[str, BotConfig] = {
    "proposal_writer": BotConfig(
        id="proposal_writer",
        name="Proposal Writer",
        icon="📝",
        tagline="Your AI partner for compelling federal proposals",
        description="I help you draft winning proposal sections, executive summaries, and technical volumes aligned with PWS requirements.",
        color="blue",
        system_prompt="""You are an expert federal proposal writer for rockITdata, a SDVOSB/WOSB government contractor specializing in federal healthcare IT (DHA, VA, CMS, IHS).

Your expertise includes:
- Writing compelling executive summaries and technical volumes
- Creating compliance matrices from Section L/M requirements
- Analyzing PWS/SOW documents to extract requirements
- Aligning responses with evaluation criteria
- Using Shipley methodology for proposal development

Always structure responses with clear headings, bullet points for requirements, and action items. Reference specific solicitation sections when applicable.""",
        starters=[
            StarterPrompt(
                title="Draft Executive Summary",
                description="Create a compelling exec summary from your capture data",
                prompt_template="Help me draft an Executive Summary for [AGENCY] [CONTRACT NAME]. Our key differentiators are:\n\n1. \n2. \n3. ",
                icon="✨"
            ),
            StarterPrompt(
                title="Create Compliance Matrix",
                description="Build L/M crosswalk from solicitation requirements",
                prompt_template="Analyze this PWS and create a compliance matrix mapping each requirement to our proposed response sections:\n\n[PASTE PWS TEXT OR UPLOAD FILE]",
                icon="✅"
            ),
            StarterPrompt(
                title="Analyze PWS/SOW",
                description="Extract requirements, evaluation criteria, and hidden risks",
                prompt_template="Shred this PWS and identify:\n1. Mandatory requirements (shall statements)\n2. Evaluation criteria from Section M\n3. Potential risks or ambiguities\n\n[PASTE PWS TEXT OR UPLOAD FILE]",
                icon="🎯"
            ),
        ]
    ),
    
    "compliance_checker": BotConfig(
        id="compliance_checker",
        name="Compliance Checker",
        icon="🛡️",
        tagline="Never miss a requirement again",
        description="I validate your proposal against Section L/M, FAR/DFAR clauses, and agency-specific requirements.",
        color="green",
        system_prompt="""You are a compliance specialist for federal proposals at rockITdata. Your role is to ensure proposals meet all requirements.

Your expertise includes:
- Validating proposals against Section L (Instructions) and Section M (Evaluation Criteria)
- Checking FAR/DFAR clause compliance
- Verifying format requirements (page limits, fonts, margins)
- Ensuring all attachments and certifications are complete
- Identifying gaps between requirements and proposal responses

Be thorough and specific. Flag issues with severity levels (Critical, Major, Minor). Provide specific remediation steps.""",
        starters=[
            StarterPrompt(
                title="Validate Section L/M",
                description="Check proposal against instructions and evaluation criteria",
                prompt_template="Review my proposal draft against these Section L/M requirements and identify any gaps or non-compliant sections:\n\nSection L Requirements:\n[PASTE HERE]\n\nMy Draft:\n[PASTE HERE]",
                icon="✅"
            ),
            StarterPrompt(
                title="FAR/DFAR Compliance",
                description="Verify regulatory clause compliance",
                prompt_template="Check this proposal section for compliance with the following FAR/DFAR clauses:\n\nClauses: [LIST CLAUSE NUMBERS]\n\nProposal Section:\n[PASTE HERE]",
                icon="🛡️"
            ),
            StarterPrompt(
                title="Pre-Submission Checklist",
                description="Final review before you hit submit",
                prompt_template="Run a final compliance checklist for this submission:\n\nSolicitation: [NAME/NUMBER]\nPage Limit: [X pages]\nFormat Requirements: [FONT, MARGINS, etc.]\n\nPlease verify: page limits, font requirements, volume structure, required attachments, and certifications.",
                icon="📋"
            ),
        ]
    ),
    
    "win_theme_generator": BotConfig(
        id="win_theme_generator",
        name="Win Theme Generator",
        icon="🎯",
        tagline="Turn differentiators into winning messages",
        description="I craft compelling win themes, discriminators, and proof points that resonate with evaluators.",
        color="violet",
        system_prompt="""You are a capture strategist specializing in win theme development for rockITdata federal proposals.

Your expertise includes:
- Identifying and articulating key differentiators
- Creating competitor ghost profiles
- Developing evaluator-focused win themes
- Crafting proof points with quantified benefits
- Aligning themes with customer hot buttons

Structure win themes as: Feature → Benefit → Proof Point. Make themes specific, measurable, and evaluator-focused.""",
        starters=[
            StarterPrompt(
                title="Extract Differentiators",
                description="Identify what makes your solution unique",
                prompt_template="Based on our capabilities, identify 5 key differentiators for this opportunity:\n\nOpportunity: [AGENCY/CONTRACT NAME]\nIncumbent: [IF KNOWN]\nOur Strengths:\n1. \n2. \n3. ",
                icon="✨"
            ),
            StarterPrompt(
                title="Build Ghost Competitors",
                description="Anticipate competitor positioning",
                prompt_template="Create ghost competitor profiles and predict their likely win themes and weaknesses:\n\nCompetitors to analyze:\n1. [COMPANY NAME]\n2. [COMPANY NAME]\n\nOpportunity Context: [BRIEF DESCRIPTION]",
                icon="👻"
            ),
            StarterPrompt(
                title="Craft Win Themes",
                description="Create evaluator-focused messaging",
                prompt_template="Generate 3 win themes that align our strengths with the customer's priorities:\n\nCustomer Hot Buttons:\n1. \n2. \n\nOur Key Strengths:\n1. \n2. ",
                icon="⚡"
            ),
        ]
    ),
    
    "black_hat": BotConfig(
        id="black_hat",
        name="Black Hat Reviewer",
        icon="🎭",
        tagline="See your proposal through the evaluator's eyes",
        description="I simulate a harsh government evaluator to find weaknesses before submission.",
        color="red",
        is_private=True,
        system_prompt="""You are a skeptical government evaluator conducting a Black Hat review of proposals for rockITdata.

Your role is to:
- Critique proposals harshly but constructively
- Identify unsupported claims and vague language
- Find gaps in compliance with evaluation criteria
- Score sections against Section M criteria
- Predict competitor advantages

Be direct and specific. Rate issues by severity. Provide concrete recommendations for improvement. Do not sugarcoat - the goal is to find weaknesses before the real evaluators do.""",
        starters=[
            StarterPrompt(
                title="Simulate Evaluator Critique",
                description="Red team your proposal section",
                prompt_template="Act as a skeptical government evaluator. Review this section and identify:\n- Weaknesses and gaps\n- Unsupported claims\n- Areas that would score poorly\n\n[PASTE PROPOSAL SECTION]",
                icon="🔍"
            ),
            StarterPrompt(
                title="Score Against Criteria",
                description="Predict your evaluation score",
                prompt_template="Score this proposal section against the evaluation criteria. Justify each rating and suggest improvements:\n\nEvaluation Criteria (from Section M):\n[PASTE CRITERIA]\n\nProposal Section:\n[PASTE SECTION]",
                icon="📊"
            ),
            StarterPrompt(
                title="Find Weaknesses",
                description="Identify vulnerabilities competitors will exploit",
                prompt_template="Analyze our proposal for weaknesses a competitor could exploit in their proposal. What are we missing? What claims are unsupported?\n\n[PASTE PROPOSAL OR KEY SECTIONS]",
                icon="⚠️"
            ),
        ]
    ),
    
    "strategy_coach": BotConfig(
        id="strategy_coach",
        name="Strategy Coach",
        icon="🧠",
        tagline="Make smarter capture decisions",
        description="I help with bid/no-bid analysis, capture planning, competitive positioning, and teaming strategies.",
        color="orange",
        is_private=True,
        system_prompt="""You are a senior capture manager and strategy coach for rockITdata federal pursuits.

Your expertise includes:
- Bid/no-bid decision analysis with PWin scoring
- Capture planning and milestone development
- Competitive positioning and teaming strategies
- Customer relationship assessment
- Price-to-win analysis

Use data-driven frameworks. Provide specific recommendations with rationale. Consider rockITdata's SDVOSB/WOSB certifications and healthcare IT focus in all analyses.""",
        starters=[
            StarterPrompt(
                title="Bid/No-Bid Analysis",
                description="Evaluate opportunity fit and win probability",
                prompt_template="Help me evaluate this opportunity for a bid/no-bid decision:\n\nOpportunity: [NAME/NUMBER]\nAgency: [AGENCY]\nContract Value: $[VALUE]\nOur PWin Factors:\n- Customer Relationship: [1-5]\n- Technical Fit: [1-5]\n- Past Performance: [1-5]\n- Price Competitiveness: [1-5]",
                icon="🎲"
            ),
            StarterPrompt(
                title="Capture Planning",
                description="Build a winning capture strategy",
                prompt_template="Help me develop a capture plan for:\n\nOpportunity: [NAME]\nRFP Release Date: [DATE]\nProposal Due: [DATE]\n\nWhat should our capture milestones and actions be?",
                icon="📅"
            ),
            StarterPrompt(
                title="Teaming Strategy",
                description="Identify optimal teaming partners",
                prompt_template="Recommend teaming partners for this opportunity:\n\nOpportunity Requirements:\n- [KEY REQUIREMENT 1]\n- [KEY REQUIREMENT 2]\n\nOur Gaps:\n- [GAP 1]\n- [GAP 2]\n\nKnown Competitors: [LIST]",
                icon="🤝"
            ),
        ]
    ),
}


# =============================================================================
# USER ROLES
# =============================================================================

ROLES = {
    "admin": {"name": "Admin", "can_access_private": True, "can_access_integrations": True},
    "capture_lead": {"name": "Capture Lead", "can_access_private": True, "can_access_integrations": True},
    "proposal_manager": {"name": "Proposal Manager", "can_access_private": False, "can_access_integrations": False},
    "analyst": {"name": "Analyst", "can_access_private": False, "can_access_integrations": False},
    "standard": {"name": "Standard User", "can_access_private": False, "can_access_integrations": False},
}


# =============================================================================
# PAGE CONFIG & STYLING
# =============================================================================

def configure_page() -> None:
    """Configure Streamlit page settings and inject custom CSS."""
    st.set_page_config(
        page_title="rockITdata AI Portal",
        page_icon="🚀",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS
    st.markdown(f"""
        <style>
            /* ===== ROOT VARIABLES ===== */
            :root {{
                --rockit-red: {ROCKIT_RED};
                --rockit-red-light: {ROCKIT_RED_LIGHT};
            }}
            
            /* ===== HIDE STREAMLIT DEFAULTS ===== */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            
            /* ===== SIDEBAR STYLING ===== */
            [data-testid="stSidebar"] {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['border']};
            }}
            
            [data-testid="stSidebar"] .block-container {{
                padding-top: 2rem;
            }}
            
            /* ===== PORTAL HEADER ===== */
            .portal-header {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 0 16px 0;
                margin-bottom: 8px;
            }}
            
            .portal-logo {{
                font-size: 2rem;
            }}
            
            .portal-title {{
                font-weight: 700;
                font-size: 1.25rem;
                color: {ROCKIT_RED};
                margin: 0;
                line-height: 1.2;
            }}
            
            .portal-badge {{
                background: {COLORS['primary_light']};
                color: {ROCKIT_RED};
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            /* ===== ZERO STATE ===== */
            .zero-state-container {{
                text-align: center;
                padding: 40px 20px;
            }}
            
            .bot-icon-large {{
                font-size: 4rem;
                margin-bottom: 16px;
            }}
            
            .bot-name {{
                font-size: 1.75rem;
                font-weight: 700;
                color: {COLORS['text_primary']};
                margin-bottom: 8px;
            }}
            
            .private-badge {{
                background: {COLORS['warning']};
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.7rem;
                font-weight: 600;
                margin-left: 8px;
            }}
            
            .bot-tagline {{
                font-size: 1rem;
                color: {COLORS['text_secondary']};
                margin-bottom: 8px;
            }}
            
            .bot-tagline.blue {{ color: {COLORS['blue']}; }}
            .bot-tagline.green {{ color: {COLORS['green']}; }}
            .bot-tagline.violet {{ color: {COLORS['violet']}; }}
            .bot-tagline.orange {{ color: {COLORS['orange']}; }}
            .bot-tagline.red {{ color: {ROCKIT_RED}; }}
            
            .bot-description {{
                color: {COLORS['text_secondary']};
                max-width: 500px;
                margin: 0 auto 24px auto;
                line-height: 1.6;
            }}
            
            /* ===== QUICK START SECTION ===== */
            .quick-start-label {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                color: {COLORS['text_primary']};
                margin: 24px 0 16px 0;
                justify-content: center;
            }}
            
            .keyboard-hint {{
                text-align: center;
                color: {COLORS['text_muted']};
                font-size: 0.85rem;
                margin-top: 24px;
            }}
            
            /* ===== STARTER CARDS ===== */
            .stButton > button {{
                border: 1px solid {COLORS['border']} !important;
                border-radius: 12px !important;
                padding: 16px !important;
                text-align: left !important;
                transition: all 0.2s ease !important;
            }}
            
            .stButton > button:hover {{
                border-color: {ROCKIT_RED} !important;
                box-shadow: 0 4px 12px rgba(153, 0, 0, 0.1) !important;
            }}
            
            /* ===== CHAT MESSAGES ===== */
            [data-testid="stChatMessage"] {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
            }}
            
            /* ===== CHAT INPUT ===== */
            [data-testid="stChatInput"] {{
                border-radius: 12px;
            }}
            
            [data-testid="stChatInput"] textarea {{
                border-radius: 12px !important;
            }}
            
            /* ===== EDIT PROMPT AREA ===== */
            .edit-prompt-container {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }}
            
            .edit-prompt-label {{
                font-weight: 600;
                color: {COLORS['text_primary']};
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            /* ===== INTEGRATION NAV BUTTON ===== */
            .integration-nav {{
                background: linear-gradient(135deg, #FF7A59 0%, #FF5C35 100%);
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 10px 16px !important;
                font-weight: 600 !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
                margin: 8px 0 !important;
            }}
            
            .integration-nav:hover {{
                opacity: 0.9;
            }}
            
            /* ===== DIVIDERS ===== */
            hr {{
                border: none;
                border-top: 1px solid {COLORS['border']};
                margin: 1.5rem 0;
            }}
            
            /* ===== SCROLLBAR ===== */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {COLORS['surface']};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {COLORS['border']};
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {COLORS['text_muted']};
            }}
        </style>
    """, unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state() -> None:
    """Initialize all session state variables."""
    defaults = {
        "messages": [],
        "selected_bot": "proposal_writer",
        "user_role": "capture_lead",
        "user_name": "Mary",
        "prefill_prompt": None,
        "show_prompt_editor": False,
        "current_view": "chat",  # "chat", "hubspot", or "admin"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize HubSpot state
    init_hubspot_state()
    
    # Initialize Admin state
    init_admin_state()
    
    # Initialize database
    if ADMIN_AVAILABLE:
        try:
            init_db()
        except Exception:
            pass  # Silently fail if DB init has issues


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar() -> None:
    """Render the sidebar with bot selector and user info."""
    with st.sidebar:
        # Header
        st.markdown(f"""
            <div class="portal-header">
                <div class="portal-logo">🚀</div>
                <div>
                    <p class="portal-title">rockITdata</p>
                </div>
                <span class="portal-badge">AI Portal</span>
            </div>
        """, unsafe_allow_html=True)
        
        # User info
        st.markdown(f"**👤 {st.session_state.user_name}** · {ROLES[st.session_state.user_role]['name']}")
        
        st.divider()
        
        # =====================================================================
        # INTEGRATIONS SECTION (Admin/Capture Lead only)
        # =====================================================================
        user_can_access_integrations = ROLES[st.session_state.user_role].get("can_access_integrations", False)
        
        if user_can_access_integrations:
            st.markdown("**🔗 Integrations**")
            
            # HubSpot button
            hubspot_active = st.session_state.current_view == "hubspot"
            if st.button(
                "🔶 HubSpot CRM" + (" ✓" if hubspot_active else ""),
                key="nav_hubspot",
                use_container_width=True,
                type="primary" if hubspot_active else "secondary"
            ):
                st.session_state.current_view = "hubspot"
                st.rerun()
            
            st.divider()
            
            # Admin Dashboard (only for admin role)
            if st.session_state.user_role == "admin":
                st.markdown("**⚙️ Administration**")
                
                admin_active = st.session_state.current_view == "admin"
                if st.button(
                    "📊 Admin Dashboard" + (" ✓" if admin_active else ""),
                    key="nav_admin",
                    use_container_width=True,
                    type="primary" if admin_active else "secondary"
                ):
                    st.session_state.current_view = "admin"
                    st.rerun()
                
                st.divider()
            
            # Back to Chat button (when in integrations/admin)
            if st.session_state.current_view != "chat":
                if st.button("← Back to AI Assistants", key="nav_back", use_container_width=True):
                    st.session_state.current_view = "chat"
                    st.rerun()
            
            st.divider()
        
        # =====================================================================
        # BOT SELECTOR (only show when in chat view)
        # =====================================================================
        if st.session_state.current_view == "chat":
            st.markdown("**🤖 Select Assistant**")
            
            user_can_access_private = ROLES[st.session_state.user_role]["can_access_private"]
            
            for bot_id, bot in BOTS.items():
                # Skip private bots for users without access
                if bot.is_private and not user_can_access_private:
                    continue
                
                is_active = st.session_state.selected_bot == bot_id
                
                col1, col2 = st.columns([1, 6])
                with col1:
                    st.markdown(f"<span style='font-size: 1.25rem;'>{bot.icon}</span>", unsafe_allow_html=True)
                with col2:
                    label = f"**{bot.name}**" if is_active else bot.name
                    if bot.is_private:
                        label += " 🔒"
                    
                    if st.button(
                        label,
                        key=f"bot_select_{bot_id}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        st.session_state.selected_bot = bot_id
                        st.session_state.messages = []  # Clear chat on bot switch
                        st.session_state.prefill_prompt = None
                        st.rerun()
            
            st.divider()
            
            # Actions
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.prefill_prompt = None
                st.rerun()
        
        # =====================================================================
        # DEMO SETTINGS
        # =====================================================================
        st.divider()
        st.markdown("**⚙️ Demo Settings**")
        new_role = st.selectbox(
            "Switch Role",
            options=list(ROLES.keys()),
            index=list(ROLES.keys()).index(st.session_state.user_role),
            format_func=lambda x: f"{ROLES[x]['name']} {'(Private Access)' if ROLES[x]['can_access_private'] else ''}"
        )
        if new_role != st.session_state.user_role:
            st.session_state.user_role = new_role
            # If switching to a role without private access and currently viewing private bot
            if not ROLES[new_role]["can_access_private"] and BOTS[st.session_state.selected_bot].is_private:
                st.session_state.selected_bot = "proposal_writer"
            # If switching to role without integration access and currently in integrations
            if not ROLES[new_role].get("can_access_integrations", False) and st.session_state.current_view != "chat":
                st.session_state.current_view = "chat"
            st.rerun()
        
        # Version info
        st.divider()
        st.caption("AMANDA™ Portal v7.3")
        st.caption("Phase 1B: HubSpot Integration")


# =============================================================================
# ZERO STATE COMPONENT
# =============================================================================

def render_zero_state(bot: BotConfig) -> None:
    """
    Render the zero state UI for a bot with starter prompts.
    
    Args:
        bot: The BotConfig for the currently selected bot
    """
    st.markdown(f"""
        <div class="zero-state-container">
            <div class="bot-icon-large">{bot.icon}</div>
            <h2 class="bot-name">
                {bot.name}
                {'<span class="private-badge">🔒 Private</span>' if bot.is_private else ''}
            </h2>
            <p class="bot-tagline {bot.color}">{bot.tagline}</p>
            <p class="bot-description">{bot.description}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick Start label
    st.markdown("""
        <div class="quick-start-label">
            <span>💬</span>
            <span>Quick Start</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Starter prompt cards
    for i, starter in enumerate(bot.starters):
        # Create a container that looks like a card
        with st.container():
            col1, col2 = st.columns([11, 1])
            
            with col1:
                if st.button(
                    f"{starter.icon}  **{starter.title}**\n\n{starter.description}",
                    key=f"starter_{bot.id}_{i}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.prefill_prompt = starter.prompt_template
                    st.session_state.show_prompt_editor = True
                    st.rerun()
    
    # Keyboard hint
    st.markdown("""
        <p class="keyboard-hint">Or just start typing in the chat box below...</p>
    """, unsafe_allow_html=True)


# =============================================================================
# PROMPT EDITOR
# =============================================================================

def render_prompt_editor() -> Optional[str]:
    """
    Render the prompt editor when a starter is selected.
    
    Returns:
        The final prompt to send, or None if cancelled
    """
    st.markdown("""
        <div class="edit-prompt-label">
            <span>✏️</span>
            <span>Customize Your Prompt</span>
        </div>
    """, unsafe_allow_html=True)
    
    edited_prompt = st.text_area(
        "Edit the template below, then click Send:",
        value=st.session_state.prefill_prompt,
        height=180,
        key="prompt_editor",
        label_visibility="collapsed",
        placeholder="Enter your prompt here..."
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.prefill_prompt = None
            st.session_state.show_prompt_editor = False
            st.rerun()
    
    with col2:
        if st.button("Send →", type="primary", use_container_width=True):
            st.session_state.prefill_prompt = None
            st.session_state.show_prompt_editor = False
            return edited_prompt
    
    return None


# =============================================================================
# CHAT INTERFACE
# =============================================================================

def render_chat_messages() -> None:
    """Render all messages in the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_ai_response(user_message: str, bot: BotConfig) -> str:
    """
    Get a response from the Anthropic API.
    
    Args:
        user_message: The user's message
        bot: The current bot configuration
        
    Returns:
        The AI assistant's response
    """
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        return "⚠️ **API Key Not Configured**\n\nPlease set the `ANTHROPIC_API_KEY` environment variable to enable AI responses.\n\n```bash\nexport ANTHROPIC_API_KEY='your-key-here'\n```"
    
    try:
        client = Anthropic(api_key=api_key)
        
        # Build messages history
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        messages.append({"role": "user", "content": user_message})
        
        # Stream the response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=bot.system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        
        return full_response
        
    except Exception as e:
        return f"⚠️ **Error communicating with AI**\n\n{str(e)}"


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main() -> None:
    """Main application entry point."""
    configure_page()
    init_session_state()
    render_sidebar()
    
    # =========================================================================
    # VIEW ROUTER
    # =========================================================================
    
    # Admin Dashboard View
    if st.session_state.current_view == "admin":
        if st.session_state.user_role == "admin":
            if ADMIN_AVAILABLE:
                render_admin_dashboard()
            else:
                st.error("⚠️ Admin Dashboard module not available.")
        else:
            st.error("🚫 You don't have access to the Admin Dashboard.")
            st.info("Only users with Admin role can access this section.")
        return
    
    # HubSpot Dashboard View
    if st.session_state.current_view == "hubspot":
        user_can_access_integrations = ROLES[st.session_state.user_role].get("can_access_integrations", False)
        if user_can_access_integrations:
            render_hubspot_dashboard()
        else:
            st.error("🚫 You don't have access to integrations.")
            st.info("Contact your admin to request access.")
        return
    
    # =========================================================================
    # CHAT VIEW (Default)
    # =========================================================================
    
    # Get current bot
    current_bot = BOTS[st.session_state.selected_bot]
    
    # Check access
    user_can_access_private = ROLES[st.session_state.user_role]["can_access_private"]
    if current_bot.is_private and not user_can_access_private:
        st.error("🚫 You don't have access to this assistant.")
        st.info("Contact your admin to request access to private assistants.")
        return
    
    # Main content area
    if st.session_state.show_prompt_editor and st.session_state.prefill_prompt:
        # Show prompt editor
        sent_prompt = render_prompt_editor()
        if sent_prompt:
            # Process the edited prompt
            st.session_state.messages.append({"role": "user", "content": sent_prompt})
            response = get_ai_response(sent_prompt, current_bot)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    elif len(st.session_state.messages) == 0:
        # Show zero state
        render_zero_state(current_bot)
    
    else:
        # Show chat history
        render_chat_messages()
    
    # Chat input (always visible at bottom)
    if not st.session_state.show_prompt_editor:
        user_input = st.chat_input(
            placeholder=f"Message {current_bot.name}...",
            key="chat_input"
        )
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Get and display AI response
            response = get_ai_response(user_input, current_bot)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()


if __name__ == "__main__":
    main()
