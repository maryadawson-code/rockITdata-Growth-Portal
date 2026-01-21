"""
rockITdata AI Portal - Main Application
========================================
A secure, role-based AI assistant portal for federal proposal development.

Author: rockITdata LLC
Version: 7.3 - Phase 1B: Full Integration
"""

import streamlit as st
from anthropic import Anthropic
from dataclasses import dataclass
from typing import Optional
import os

# =============================================================================
# SAFE MODULE IMPORTS
# =============================================================================

# Try to import optional modules (graceful degradation if not present)
try:
    from pipeline_view import show_pipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

try:
    from admin_dashboard import show_admin_dashboard
    ADMIN_DASHBOARD_AVAILABLE = True
except ImportError:
    ADMIN_DASHBOARD_AVAILABLE = False

try:
    from hubspot_dashboard import show_hubspot_dashboard
    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False

try:
    from database import init_database, log_audit_event, track_token_usage
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

try:
    from ultra_delight import (
        init_ultra_delight, 
        render_visor, 
        show_toast, 
        trigger_celebration,
        check_pending_celebration,
        render_progress_ring,
        render_animated_metric,
        show_ultra_delight_demo,
        set_visor_status,
        get_visor_status
    )
    ULTRA_DELIGHT_AVAILABLE = True
except ImportError:
    ULTRA_DELIGHT_AVAILABLE = False


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
# ROLE DEFINITIONS
# =============================================================================

ROLES = {
    "admin": {
        "name": "Administrator",
        "can_access_private": True,
        "can_access_admin": True,
        "can_access_pipeline": True,
        "can_access_hubspot": True,
    },
    "ceo": {
        "name": "CEO",
        "can_access_private": True,
        "can_access_admin": True,
        "can_access_pipeline": True,
        "can_access_hubspot": True,
    },
    "coo": {
        "name": "COO",
        "can_access_private": True,
        "can_access_admin": False,
        "can_access_pipeline": True,
        "can_access_hubspot": True,
    },
    "capture_lead": {
        "name": "Capture Lead",
        "can_access_private": True,
        "can_access_admin": False,
        "can_access_pipeline": True,
        "can_access_hubspot": True,
    },
    "proposal_manager": {
        "name": "Proposal Manager",
        "can_access_private": False,
        "can_access_admin": False,
        "can_access_pipeline": True,
        "can_access_hubspot": False,
    },
    "solution_architect": {
        "name": "Solution Architect",
        "can_access_private": False,
        "can_access_admin": False,
        "can_access_pipeline": True,
        "can_access_hubspot": False,
    },
    "writer": {
        "name": "Proposal Writer",
        "can_access_private": False,
        "can_access_admin": False,
        "can_access_pipeline": False,
        "can_access_hubspot": False,
    },
    "reviewer": {
        "name": "Reviewer",
        "can_access_private": False,
        "can_access_admin": False,
        "can_access_pipeline": False,
        "can_access_hubspot": False,
    },
    "partner": {
        "name": "Teaming Partner",
        "can_access_private": False,
        "can_access_admin": False,
        "can_access_pipeline": False,
        "can_access_hubspot": False,
    },
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

Always structure responses with clear headings, bullet points for requirements, and action items. Reference specific solicitation sections when applicable.

IMPORTANT: End every response with:
---
*AI GENERATED - REQUIRES HUMAN REVIEW*""",
        starters=[
            StarterPrompt(
                title="Draft Executive Summary",
                description="Create a compelling exec summary from your capture data",
                prompt_template="Help me draft an Executive Summary for [AGENCY] [CONTRACT NAME]. Our key differentiators are:\n\n1. \n2. \n3. ",
                icon="✨"
            ),
            StarterPrompt(
                title="Analyze PWS Requirements",
                description="Break down a PWS into actionable requirements",
                prompt_template="Please analyze this PWS and create a requirements matrix:\n\n[PASTE PWS TEXT HERE]",
                icon="🔍"
            ),
            StarterPrompt(
                title="Write Technical Approach",
                description="Draft a technical approach section",
                prompt_template="Help me write the technical approach for [TASK AREA]. Key requirements include:\n\n- ",
                icon="📋"
            ),
            StarterPrompt(
                title="Create Win Themes",
                description="Develop compelling win themes for your proposal",
                prompt_template="Help me develop 3-5 win themes for [CONTRACT NAME] against incumbent [INCUMBENT NAME]. Our strengths are:\n\n",
                icon="🎯"
            ),
        ]
    ),
    "compliance_checker": BotConfig(
        id="compliance_checker",
        name="Compliance Checker",
        icon="🛡️",
        tagline="Ensure your proposals meet every requirement",
        description="I review your proposal content against RFP requirements to identify gaps and ensure compliance with Section L/M criteria.",
        color="green",
        system_prompt="""You are a compliance expert for federal proposals at rockITdata. Your role is to ensure proposals meet all RFP requirements.

Your expertise includes:
- Reviewing Section L (instructions) and Section M (evaluation criteria)
- Creating compliance matrices
- Identifying missing requirements or gaps
- Checking for proper response formatting
- Verifying page limits and submission requirements
- Ensuring FAR/DFARS compliance for SDVOSB/WOSB contracts

When reviewing content, always:
1. Quote the specific requirement
2. Assess compliance status (Compliant/Partial/Non-Compliant/Missing)
3. Provide specific recommendations for gaps

Use a structured format with clear compliance ratings.

IMPORTANT: End every response with:
---
*AI GENERATED - REQUIRES HUMAN REVIEW*""",
        starters=[
            StarterPrompt(
                title="Check Section L Compliance",
                description="Verify your response meets submission requirements",
                prompt_template="Please check this section against Section L requirements:\n\nSECTION L REQUIREMENTS:\n[PASTE REQUIREMENTS]\n\nOUR RESPONSE:\n[PASTE RESPONSE]",
                icon="📋"
            ),
            StarterPrompt(
                title="Gap Analysis",
                description="Identify missing requirements in your draft",
                prompt_template="Perform a gap analysis on this draft against these requirements:\n\nREQUIREMENTS:\n[PASTE REQUIREMENTS]\n\nDRAFT:\n[PASTE DRAFT]",
                icon="🔍"
            ),
            StarterPrompt(
                title="Create Compliance Matrix",
                description="Build a compliance matrix from RFP sections",
                prompt_template="Create a compliance matrix from this RFP section:\n\n[PASTE RFP TEXT]",
                icon="📊"
            ),
        ]
    ),
    "win_theme_generator": BotConfig(
        id="win_theme_generator",
        name="Win Theme Generator",
        icon="🏆",
        tagline="Craft compelling discriminators that win",
        description="I help you develop powerful win themes and discriminators based on your competitive analysis and customer insights.",
        color="orange",
        system_prompt="""You are a capture strategist specializing in win theme development for federal proposals at rockITdata.

Your expertise includes:
- Developing compelling discriminators
- Creating customer-focused benefit statements
- Competitive positioning (Gold Team strategies)
- Ghost competitor analysis
- Price-to-win strategies
- SDVOSB/WOSB competitive advantages

Win Theme Framework:
1. FEATURE: What we offer
2. BENEFIT: Why it matters to the customer
3. PROOF: Evidence/past performance

Always make themes specific, measurable, and customer-outcome focused.

IMPORTANT: End every response with:
---
*AI GENERATED - REQUIRES HUMAN REVIEW*""",
        starters=[
            StarterPrompt(
                title="Develop Win Themes",
                description="Create 3-5 powerful win themes",
                prompt_template="Help me develop win themes for:\n\nContract: [NAME]\nCustomer: [AGENCY]\nIncumbent: [NAME]\nOur Strengths:\n- \n- \n-",
                icon="🎯"
            ),
            StarterPrompt(
                title="Ghost the Competition",
                description="Develop competitive positioning strategies",
                prompt_template="Help me ghost [COMPETITOR] for this opportunity. Their weaknesses are:\n\n1. \n2. \n3. ",
                icon="👻"
            ),
            StarterPrompt(
                title="Price-to-Win Analysis",
                description="Develop pricing strategy themes",
                prompt_template="Help me develop price-to-win themes for [CONTRACT]. Budget is approximately $[AMOUNT]. Incumbent is charging approximately $[AMOUNT].",
                icon="💰"
            ),
        ]
    ),
    "strategy_coach": BotConfig(
        id="strategy_coach",
        name="Strategy Coach",
        icon="🎓",
        tagline="Executive-level capture guidance",
        description="I provide strategic capture management advice, BD pipeline analysis, and Go/No-Go recommendations.",
        color="violet",
        system_prompt="""You are a senior capture management advisor for rockITdata executives (CEO, COO, Capture Leads).

Your expertise includes:
- Capture management best practices (Shipley methodology)
- BD pipeline health assessment
- Go/No-Go decision frameworks
- Resource allocation strategies
- Win probability (pWin) assessment
- Teaming and subcontracting strategies
- SDVOSB/WOSB mentor-protégé opportunities

Always provide strategic, executive-level guidance with clear recommendations and risk assessments.

Shipley Gate Process:
- Gate 1: Opportunity Qualification
- Blue Team: Strategy Review
- Kickoff: 48hr from RFP release
- Pink Team: 30% compliance review
- Red Team: 70% quality review
- Gold Team: 90% final review
- White Glove: Production/submission

IMPORTANT: End every response with:
---
*AI GENERATED - REQUIRES HUMAN REVIEW*""",
        starters=[
            StarterPrompt(
                title="Go/No-Go Analysis",
                description="Evaluate an opportunity for pursuit",
                prompt_template="Help me evaluate Go/No-Go for:\n\nOpportunity: [NAME]\nAgency: [AGENCY]\nValue: $[AMOUNT]\nIncumbent: [NAME]\nOur relevant experience:\n- ",
                icon="🚦"
            ),
            StarterPrompt(
                title="pWin Assessment",
                description="Calculate probability of win",
                prompt_template="Assess our pWin for [CONTRACT]:\n\nPositives:\n- \n- \n\nChallenges:\n- \n- \n\nCompetitor strengths:\n- ",
                icon="📈"
            ),
            StarterPrompt(
                title="Teaming Strategy",
                description="Develop optimal teaming approach",
                prompt_template="Help me develop a teaming strategy for [CONTRACT]. We need partners with:\n\n1. \n2. \n3. ",
                icon="🤝"
            ),
        ],
        is_private=True
    ),
    "black_hat_reviewer": BotConfig(
        id="black_hat_reviewer",
        name="Black Hat Reviewer",
        icon="🎩",
        tagline="See your proposal through competitor eyes",
        description="I review your proposal from a competitor's perspective, identifying vulnerabilities and counter-strategies.",
        color="gray",
        system_prompt="""You are a Black Hat reviewer simulating how competitors would evaluate and attack rockITdata's proposal.

Your role is to:
- Identify proposal weaknesses competitors will exploit
- Predict competitor discriminators and win themes
- Find gaps in technical approaches
- Assess price vulnerability
- Recommend defensive strategies

Be brutally honest but constructive. Your goal is to help the team strengthen the proposal before submission.

Framework:
1. VULNERABILITY: What weakness exists
2. COMPETITOR EXPLOIT: How they'll attack it
3. MITIGATION: How to address it

IMPORTANT: End every response with:
---
*AI GENERATED - REQUIRES HUMAN REVIEW*""",
        starters=[
            StarterPrompt(
                title="Black Hat Review",
                description="Review proposal from competitor perspective",
                prompt_template="Perform a Black Hat review of this section:\n\n[PASTE PROPOSAL SECTION]\n\nKnown competitors: [LIST COMPETITORS]",
                icon="🔍"
            ),
            StarterPrompt(
                title="Competitor Win Themes",
                description="Predict competitor strategies",
                prompt_template="Predict win themes for [COMPETITOR] on [CONTRACT]. Their known strengths are:\n\n- \n- ",
                icon="🎯"
            ),
            StarterPrompt(
                title="Defense Strategy",
                description="Develop counter-strategies",
                prompt_template="Help me develop defensive strategies against [COMPETITOR]. They will likely attack us on:\n\n1. \n2. ",
                icon="🛡️"
            ),
        ],
        is_private=True
    ),
}


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

def configure_page() -> None:
    """Configure the Streamlit page settings and styling."""
    st.set_page_config(
        page_title="rockITdata AI Portal",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown(f"""
        <style>
            /* ===== GLOBAL STYLES ===== */
            .stApp {{
                background-color: {COLORS['background']};
            }}
            
            /* ===== SIDEBAR ===== */
            [data-testid="stSidebar"] {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['border']};
            }}
            
            /* ===== PORTAL HEADER ===== */
            .portal-header {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 0;
                margin-bottom: 16px;
            }}
            
            .portal-logo {{
                font-size: 2rem;
            }}
            
            .portal-title {{
                font-size: 1.25rem;
                font-weight: 700;
                color: {COLORS['primary']};
                margin: 0;
            }}
            
            .portal-badge {{
                background: {COLORS['primary']};
                color: white;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .version-badge {{
                background: {COLORS['surface_alt']};
                color: {COLORS['text_secondary']};
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.65rem;
                font-weight: 500;
            }}
            
            /* ===== NAV SECTION ===== */
            .nav-section {{
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid {COLORS['border']};
            }}
            
            .nav-section-title {{
                font-size: 0.75rem;
                font-weight: 600;
                color: {COLORS['text_muted']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
            }}
            
            /* ===== BOT CARD (Zero State) ===== */
            .bot-header {{
                text-align: center;
                padding: 40px 20px;
                margin-bottom: 24px;
            }}
            
            .bot-icon {{
                font-size: 4rem;
                margin-bottom: 16px;
            }}
            
            .bot-name {{
                font-size: 1.75rem;
                font-weight: 700;
                color: {COLORS['text_primary']};
                margin: 0 0 8px 0;
            }}
            
            .bot-tagline {{
                font-size: 1.1rem;
                color: {COLORS['text_secondary']};
                margin: 0 0 16px 0;
            }}
            
            .bot-description {{
                color: {COLORS['text_secondary']};
                max-width: 500px;
                margin: 0 auto;
                line-height: 1.6;
            }}
            
            /* ===== STARTER CARDS ===== */
            .starter-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 16px;
                max-width: 800px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            
            .starter-card {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .starter-card:hover {{
                border-color: {COLORS['primary']};
                box-shadow: 0 4px 12px rgba(153, 0, 0, 0.1);
                transform: translateY(-2px);
            }}
            
            .starter-icon {{
                font-size: 1.5rem;
                margin-bottom: 8px;
            }}
            
            .starter-title {{
                font-weight: 600;
                color: {COLORS['text_primary']};
                margin: 0 0 4px 0;
            }}
            
            .starter-desc {{
                font-size: 0.875rem;
                color: {COLORS['text_secondary']};
                margin: 0;
            }}
            
            /* ===== CHAT MESSAGES ===== */
            [data-testid="stChatMessage"] {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
            }}
            
            /* ===== BUTTONS ===== */
            .stButton > button {{
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.2s ease;
            }}
            
            .stButton > button[kind="primary"] {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
            
            .stButton > button[kind="primary"]:hover {{
                background-color: {COLORS['primary_light']};
                border-color: {COLORS['primary']};
            }}
            
            /* ===== METRICS ===== */
            [data-testid="stMetric"] {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
            
            /* ===== TABS ===== */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                border-radius: 8px 8px 0 0;
                padding: 8px 16px;
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
    
    # Initialize Ultra-Delight animations
    if ULTRA_DELIGHT_AVAILABLE:
        init_ultra_delight()


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
        "current_view": "chat",  # chat, pipeline, admin, hubspot, delight_demo
        "visor_status": "idle",  # Ultra-Delight: idle, thinking, success, warning, error, celebrating
        "celebration_pending": None,  # Ultra-Delight: celebration data
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar() -> None:
    """Render the sidebar with navigation, bot selector, and user info."""
    with st.sidebar:
        # Header with Visor
        st.markdown(f"""
            <div class="portal-header">
                <div class="portal-logo">🚀</div>
                <div>
                    <p class="portal-title">rockITdata</p>
                </div>
                <span class="portal-badge">AI Portal</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Version badge and Visor status in same row
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<span class="version-badge">v7.3</span>', unsafe_allow_html=True)
        with col2:
            if ULTRA_DELIGHT_AVAILABLE:
                render_visor(st.session_state.get("visor_status", "idle"), show_label=False)
        
        # User info
        st.markdown(f"**👤 {st.session_state.user_name}** · {ROLES[st.session_state.user_role]['name']}")
        
        st.divider()
        
        # =============================================================
        # NAVIGATION SECTION
        # =============================================================
        current_role = ROLES[st.session_state.user_role]
        
        # Main Navigation
        st.markdown("**📍 Navigation**")
        
        # Chat Button (always available)
        chat_active = st.session_state.current_view == "chat"
        if st.button(
            "💬 AI Assistants",
            key="nav_chat",
            use_container_width=True,
            type="primary" if chat_active else "secondary"
        ):
            st.session_state.current_view = "chat"
            st.rerun()
        
        # Pipeline Button (if available and user has access)
        if PIPELINE_AVAILABLE and current_role.get("can_access_pipeline", False):
            pipeline_active = st.session_state.current_view == "pipeline"
            if st.button(
                "📊 Pipeline Board",
                key="nav_pipeline",
                use_container_width=True,
                type="primary" if pipeline_active else "secondary"
            ):
                st.session_state.current_view = "pipeline"
                st.rerun()
        
        # Integrations Section (Admin/Capture Lead only)
        if current_role.get("can_access_hubspot", False):
            st.divider()
            st.markdown("**🔗 Integrations**")
            
            if HUBSPOT_AVAILABLE:
                hubspot_active = st.session_state.current_view == "hubspot"
                if st.button(
                    "🟠 HubSpot CRM",
                    key="nav_hubspot",
                    use_container_width=True,
                    type="primary" if hubspot_active else "secondary"
                ):
                    st.session_state.current_view = "hubspot"
                    st.rerun()
        
        # Admin Section (Admin only)
        if current_role.get("can_access_admin", False):
            st.divider()
            st.markdown("**⚙️ Administration**")
            
            if ADMIN_DASHBOARD_AVAILABLE:
                admin_active = st.session_state.current_view == "admin"
                if st.button(
                    "📊 Admin Dashboard",
                    key="nav_admin",
                    use_container_width=True,
                    type="primary" if admin_active else "secondary"
                ):
                    st.session_state.current_view = "admin"
                    st.rerun()
            
            # Ultra-Delight Demo (Admin only)
            if ULTRA_DELIGHT_AVAILABLE:
                delight_active = st.session_state.current_view == "delight_demo"
                if st.button(
                    "✨ Ultra-Delight Demo",
                    key="nav_delight",
                    use_container_width=True,
                    type="primary" if delight_active else "secondary"
                ):
                    st.session_state.current_view = "delight_demo"
                    st.rerun()
        
        # =============================================================
        # BOT SELECTOR (only show in chat view)
        # =============================================================
        if st.session_state.current_view == "chat":
            st.divider()
            st.markdown("**🤖 Select Assistant**")
            
            user_can_access_private = current_role["can_access_private"]
            
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
                        st.session_state.messages = []
                        st.session_state.prefill_prompt = None
                        st.rerun()
            
            st.divider()
            
            # Clear Chat
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.prefill_prompt = None
                st.rerun()
        
        # =============================================================
        # DEMO SETTINGS (always at bottom)
        # =============================================================
        st.divider()
        st.markdown("**⚙️ Demo Settings**")
        new_role = st.selectbox(
            "Switch Role",
            options=list(ROLES.keys()),
            index=list(ROLES.keys()).index(st.session_state.user_role),
            format_func=lambda x: f"{ROLES[x]['name']} {'(Admin)' if ROLES[x].get('can_access_admin') else ''}"
        )
        if new_role != st.session_state.user_role:
            st.session_state.user_role = new_role
            # Reset view if user loses access
            if not ROLES[new_role].get("can_access_admin") and st.session_state.current_view == "admin":
                st.session_state.current_view = "chat"
            if not ROLES[new_role].get("can_access_pipeline") and st.session_state.current_view == "pipeline":
                st.session_state.current_view = "chat"
            if not ROLES[new_role].get("can_access_hubspot") and st.session_state.current_view == "hubspot":
                st.session_state.current_view = "chat"
            # If switching to a role without private access and currently viewing private bot
            if not ROLES[new_role]["can_access_private"] and BOTS[st.session_state.selected_bot].is_private:
                st.session_state.selected_bot = "proposal_writer"
            st.rerun()


# =============================================================================
# ZERO STATE COMPONENT
# =============================================================================

def render_zero_state(bot: BotConfig) -> None:
    """Render the zero state with bot info and starter prompts."""
    # Bot header
    st.markdown(f"""
        <div class="bot-header">
            <div class="bot-icon">{bot.icon}</div>
            <h1 class="bot-name">{bot.name}</h1>
            <p class="bot-tagline">{bot.tagline}</p>
            <p class="bot-description">{bot.description}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Starter prompts
    st.markdown("### 💡 Quick Start")
    
    cols = st.columns(2)
    for i, starter in enumerate(bot.starters):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"""
                    <div class="starter-card">
                        <div class="starter-icon">{starter.icon}</div>
                        <p class="starter-title">{starter.title}</p>
                        <p class="starter-desc">{starter.description}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Use this prompt", key=f"starter_{i}", use_container_width=True):
                    st.session_state.prefill_prompt = starter.prompt_template
                    st.session_state.show_prompt_editor = True
                    st.rerun()


# =============================================================================
# PROMPT EDITOR
# =============================================================================

def render_prompt_editor() -> Optional[str]:
    """Render the prompt editor and return the final prompt if submitted."""
    st.markdown("### ✏️ Edit Your Prompt")
    st.markdown("Customize the template below, then send to the assistant.")
    
    edited_prompt = st.text_area(
        "Your prompt",
        value=st.session_state.prefill_prompt,
        height=200,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.prefill_prompt = None
            st.session_state.show_prompt_editor = False
            st.rerun()
    with col2:
        if st.button("📤 Send to Assistant", type="primary", use_container_width=True):
            st.session_state.prefill_prompt = None
            st.session_state.show_prompt_editor = False
            return edited_prompt
    
    return None


# =============================================================================
# CHAT MESSAGES
# =============================================================================

def render_chat_messages() -> None:
    """Render the chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# =============================================================================
# AI RESPONSE
# =============================================================================

def get_ai_response(user_message: str, bot: BotConfig) -> str:
    """Get a response from the Anthropic API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        if ULTRA_DELIGHT_AVAILABLE:
            st.session_state.visor_status = "error"
        return "⚠️ **API Key Not Configured**\n\nPlease set the `ANTHROPIC_API_KEY` environment variable.\n\n---\n*AI GENERATED - REQUIRES HUMAN REVIEW*"
    
    try:
        # Set visor to thinking
        if ULTRA_DELIGHT_AVAILABLE:
            st.session_state.visor_status = "thinking"
        
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
        
        # Set visor to success
        if ULTRA_DELIGHT_AVAILABLE:
            st.session_state.visor_status = "success"
        
        # Track token usage if database available
        if DATABASE_AVAILABLE:
            try:
                track_token_usage(
                    bot_id=bot.id,
                    input_tokens=len(user_message.split()) * 2,  # Rough estimate
                    output_tokens=len(full_response.split()) * 2
                )
            except:
                pass
        
        return full_response
        
    except Exception as e:
        if ULTRA_DELIGHT_AVAILABLE:
            st.session_state.visor_status = "error"
        return f"⚠️ **Error communicating with AI**\n\n{str(e)}\n\n---\n*AI GENERATED - REQUIRES HUMAN REVIEW*"


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main() -> None:
    """Main application entry point."""
    configure_page()
    init_session_state()
    render_sidebar()
    
    # Route to appropriate view
    current_view = st.session_state.current_view
    
    # =============================================================
    # PIPELINE VIEW
    # =============================================================
    if current_view == "pipeline" and PIPELINE_AVAILABLE:
        show_pipeline()
        return
    
    # =============================================================
    # ADMIN DASHBOARD
    # =============================================================
    if current_view == "admin" and ADMIN_DASHBOARD_AVAILABLE:
        show_admin_dashboard()
        return
    
    # =============================================================
    # HUBSPOT DASHBOARD
    # =============================================================
    if current_view == "hubspot" and HUBSPOT_AVAILABLE:
        show_hubspot_dashboard()
        return
    
    # =============================================================
    # ULTRA-DELIGHT DEMO
    # =============================================================
    if current_view == "delight_demo" and ULTRA_DELIGHT_AVAILABLE:
        show_ultra_delight_demo()
        return
    
    # =============================================================
    # CHECK FOR PENDING CELEBRATIONS
    # =============================================================
    if ULTRA_DELIGHT_AVAILABLE:
        check_pending_celebration()
    
    # =============================================================
    # CHAT VIEW (default)
    # =============================================================
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
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            response = get_ai_response(user_input, current_bot)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()


if __name__ == "__main__":
    main()
