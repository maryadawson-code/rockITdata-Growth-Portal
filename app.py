"""
AMANDA™ Portal - Main Application
===================================
A secure, role-based AI assistant portal for federal proposal development.

Author: rockITdata LLC
Version: 2.0.0
"""

import streamlit as st
from anthropic import Anthropic
import os
from typing import Optional

from config import (
    BRAND, COLORS, ROLES, BOTS, GATES, PAGES,
    PHASE_COLORS, PHASE_NAMES, RoleType
)
from database import (
    get_deals, get_deal_by_id, get_artifacts, get_requirements,
    get_reviews, get_issues, get_partners, get_playbook_lessons,
    get_users, get_pipeline_stats, get_compliance_stats,
    DealStatus, DealPriority, ArtifactStatus, RequirementType,
    RequirementStatus, ReviewType, ReviewStatus, IssueSeverity,
    IssueStatus, PartnerType, PartnerStatus, TAStatus, LessonCategory
)
from demo_mode import get_demo_engine, DemoScenario
from onboarding import get_tour_for_role, get_general_tour, TourStep
from components import (
    inject_custom_css, render_page_header, render_metric_card,
    render_progress_bar, render_phase_navigator, render_demo_mode_banner,
    render_empty_state, format_currency, status_badge, render_badge
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{BRAND['product']} Portal | {BRAND['name']}",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state() -> None:
    """Initialize session state variables."""
    defaults = {
        "user_role": "capture_lead",
        "user_name": "Mary Womack",
        "current_page": "dashboard",
        "selected_deal": None,
        "selected_bot": "general",
        "messages": [],
        "demo_mode": True,  # Default to demo mode
        "show_prompt_editor": False,
        "prefill_prompt": None,
        # Tour state
        "tour_active": False,
        "tour_step": 0,
        "tour_completed": False,
        "show_tour_prompt": True,  # Show "Start Tour?" on first visit
        "role_tour_active": False,
        "role_tour_step": 0,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar() -> None:
    """Render the sidebar navigation."""
    with st.sidebar:
        # Logo and branding
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
                <div style="width: 40px; height: 40px; background: {COLORS['primary']}; 
                            border-radius: 10px; display: flex; align-items: center; 
                            justify-content: center; color: white; font-size: 1.25rem;">
                    🚀
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.125rem;">{BRAND['product']}</div>
                    <div style="font-size: 0.7rem; color: {COLORS['text_secondary']};">
                        {BRAND['tagline']}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # User info
        role_config = ROLES.get(st.session_state.user_role)
        st.markdown(f"""
            <div style="background: {COLORS['surface']}; padding: 12px; border-radius: 8px; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 36px; height: 36px; background: {COLORS['primary']}; 
                                border-radius: 50%; display: flex; align-items: center; 
                                justify-content: center; color: white; font-size: 0.875rem; font-weight: 600;">
                        {st.session_state.user_name[:2].upper()}
                    </div>
                    <div>
                        <div style="font-weight: 600; font-size: 0.875rem;">{st.session_state.user_name}</div>
                        <div style="font-size: 0.75rem; color: {COLORS['text_secondary']};">
                            {role_config.icon if role_config else ''} {role_config.name if role_config else 'User'}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("**Navigation**")
        
        for page_id, page_config in PAGES.items():
            # Check access for restricted pages
            if page_config.get("restricted"):
                role = ROLES.get(st.session_state.user_role)
                if not role or not role.can_config_system:
                    continue
            
            is_active = st.session_state.current_page == page_id
            
            if st.button(
                f"{page_config['icon']} {page_config['name']}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.divider()
        
        # Demo Mode Toggle
        st.markdown("**Demo Mode**")
        demo_mode = st.toggle(
            "Enable Demo Mode",
            value=st.session_state.demo_mode,
            help="Run with simulated responses (no API calls)"
        )
        if demo_mode != st.session_state.demo_mode:
            st.session_state.demo_mode = demo_mode
            demo_engine = get_demo_engine()
            if demo_mode:
                demo_engine.enable_demo_mode()
            else:
                demo_engine.disable_demo_mode()
            st.rerun()
        
        if st.session_state.demo_mode:
            st.info("🎬 Demo Mode: Responses are simulated")
        
        st.divider()
        
        # Guided Tours
        st.markdown("**Guided Tours**")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            if st.button("📖 General", use_container_width=True, help="Overview of all features"):
                st.session_state.tour_active = True
                st.session_state.tour_step = 0
                st.session_state.show_tour_prompt = False
                st.rerun()
        
        with col_t2:
            role_config = ROLES.get(st.session_state.user_role)
            role_label = role_config.name if role_config else "Role"
            if st.button(f"🎯 {role_label[:8]}", use_container_width=True, help=f"Tour for {role_label}"):
                st.session_state.role_tour_active = True
                st.session_state.role_tour_step = 0
                st.rerun()
        
        st.divider()
        
        # Role Switcher (for testing)
        st.markdown("**Role Switcher** (Testing)")
        role_options = {k: f"{v.icon} {v.name}" for k, v in ROLES.items() if v.type == RoleType.INTERNAL}
        role_keys = list(role_options.keys())
        current_index = role_keys.index(st.session_state.user_role) if st.session_state.user_role in role_keys else 0
        
        selected_role = st.selectbox(
            "Switch Role",
            options=role_keys,
            format_func=lambda x: role_options[x],
            index=current_index,
            key="role_switcher",
            label_visibility="collapsed",
        )
        
        if selected_role != st.session_state.user_role:
            st.session_state.user_role = selected_role
            # Clear any cached bot selections when role changes
            if "selected_bot" in st.session_state:
                # Reset to general bot if current bot not allowed for new role
                new_role_config = ROLES.get(selected_role)
                current_bot = BOTS.get(st.session_state.selected_bot)
                if current_bot and current_bot.is_private:
                    if selected_role not in current_bot.allowed_roles:
                        st.session_state.selected_bot = "general"
            st.rerun()
        
        # Show current permissions
        current_role = ROLES.get(st.session_state.user_role)
        if current_role:
            with st.expander("View Permissions"):
                st.caption(f"**Role:** {current_role.name}")
                st.caption(f"**Dashboard:** {'✅' if current_role.can_access_dashboard else '❌'}")
                st.caption(f"**War Room:** {'✅' if current_role.can_access_war_room else '❌'}")
                st.caption(f"**Pricing:** {'✅' if current_role.can_view_pricing else '❌'}")
                st.caption(f"**Strategy:** {'✅' if current_role.can_view_strategy else '❌'}")
                st.caption(f"**Admin:** {'✅' if current_role.can_config_system else '❌'}")


# =============================================================================
# PAGE: DASHBOARD
# =============================================================================

def render_dashboard_page() -> None:
    """Render the main dashboard page."""
    render_page_header("Command Center", "Executive overview of pipeline and operations", "📊")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Pipeline Stats
    stats = get_pipeline_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Pipeline",
            value=format_currency(stats["total_value"]),
            delta="+12% vs Q3"
        )
    
    with col2:
        st.metric(
            label="Weighted Value",
            value=format_currency(int(stats["weighted_value"])),
            delta="Based on pWin"
        )
    
    with col3:
        st.metric(
            label="Active Deals",
            value=str(stats["total_deals"]),
            delta=f"{stats['by_phase'].get('P3', 0)} in development"
        )
    
    with col4:
        st.metric(
            label="At Risk",
            value=str(stats["at_risk_count"]),
            delta="Needs attention",
            delta_color="inverse"
        )
    
    st.divider()
    
    # Two-column layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📈 Active Opportunities")
        
        deals = get_deals()
        for deal in deals[:5]:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{deal.name}**")
                    st.caption(f"{deal.customer} · {deal.solicitation_number or 'TBD'}")
                
                with col2:
                    st.markdown(f"**{format_currency(deal.value)}**")
                    st.caption("Value")
                
                with col3:
                    pwin_color = "green" if deal.p_win >= 70 else "orange" if deal.p_win >= 50 else "red"
                    st.markdown(f"**:{pwin_color}[{deal.p_win}%]**")
                    st.caption("pWin")
                
                with col4:
                    status_color = "green" if deal.status == DealStatus.ON_TRACK else "red" if deal.status == DealStatus.AT_RISK else "gray"
                    st.markdown(f":{status_color}[● {deal.status.value.replace('_', ' ')}]")
                    st.caption(f"{deal.phase} / {deal.stage}")
                
                st.divider()
    
    with col_right:
        st.markdown("### ⚠️ Open Issues")
        
        issues = get_issues(status="OPEN")
        if issues:
            for issue in issues[:5]:
                severity_icon = "🔴" if issue.severity == IssueSeverity.CRITICAL else "🟡" if issue.severity == IssueSeverity.MAJOR else "⚪"
                st.markdown(f"{severity_icon} **{issue.title[:40]}...**")
                st.caption(f"{issue.deal_name} · Due: {issue.due_date}")
        else:
            st.info("No open issues! 🎉")
        
        st.divider()
        
        st.markdown("### 📅 Upcoming Reviews")
        
        reviews = [r for r in get_reviews() if r.status == ReviewStatus.SCHEDULED or r.status == ReviewStatus.IN_PROGRESS]
        if reviews:
            for review in reviews[:3]:
                color = REVIEW_COLORS.get(review.review_type.value, "#gray")
                st.markdown(f"**{review.review_type.value} Team** - {review.deal_name}")
                st.caption(f"📅 {review.scheduled_date} · Lead: {review.lead}")
        else:
            st.info("No upcoming reviews scheduled")


# =============================================================================
# PAGE: DEALS PIPELINE
# =============================================================================

def render_deals_page() -> None:
    """Render the deals pipeline page."""
    render_page_header("Deals Pipeline", "Track opportunities through the Shipley lifecycle", "📈")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Search deals", placeholder="Search by name, customer...")
    
    with col2:
        phase_filter = st.selectbox("Phase", ["All", "P0", "P1", "P2", "P3", "P4"])
    
    with col3:
        status_filter = st.selectbox("Status", ["All", "On Track", "At Risk", "New"])
    
    with col4:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("➕ New Deal", type="primary"):
            st.toast("New deal form would open here")
    
    st.divider()
    
    # Deals table
    deals = get_deals()
    
    # Apply filters
    if search:
        deals = [d for d in deals if search.lower() in d.name.lower() or search.lower() in d.customer.lower()]
    if phase_filter != "All":
        deals = [d for d in deals if d.phase == phase_filter]
    if status_filter != "All":
        status_map = {"On Track": "ON_TRACK", "At Risk": "AT_RISK", "New": "NEW"}
        deals = [d for d in deals if d.status.value == status_map.get(status_filter)]
    
    if not deals:
        render_empty_state("📭", "No deals found", "Try adjusting your filters")
        return
    
    # Table header
    cols = st.columns([3, 2, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown("**Deal**")
    with cols[1]:
        st.markdown("**Customer**")
    with cols[2]:
        st.markdown("**Value**")
    with cols[3]:
        st.markdown("**pWin**")
    with cols[4]:
        st.markdown("**Phase**")
    with cols[5]:
        st.markdown("**Status**")
    with cols[6]:
        st.markdown("**Due**")
    
    st.divider()
    
    # Table rows
    for deal in deals:
        cols = st.columns([3, 2, 1, 1, 1, 1, 1])
        
        with cols[0]:
            if st.button(f"**{deal.name}**", key=f"deal_{deal.id}", help="Click to view details"):
                st.session_state.selected_deal = deal.id
                st.session_state.current_page = "workflows"
                st.rerun()
            st.caption(deal.id)
        
        with cols[1]:
            st.write(deal.customer)
        
        with cols[2]:
            st.write(format_currency(deal.value))
        
        with cols[3]:
            pwin_color = "green" if deal.p_win >= 70 else "orange" if deal.p_win >= 50 else "red"
            st.progress(deal.p_win / 100)
            st.caption(f"{deal.p_win}%")
        
        with cols[4]:
            phase_color = PHASE_COLORS.get(deal.phase, "#gray")
            st.markdown(f"<span style='background:{phase_color}; color:white; padding:2px 8px; border-radius:4px; font-size:0.75rem;'>{deal.phase}</span>", unsafe_allow_html=True)
            st.caption(deal.stage)
        
        with cols[5]:
            status_color = "🟢" if deal.status == DealStatus.ON_TRACK else "🔴" if deal.status == DealStatus.AT_RISK else "🔵"
            st.write(f"{status_color} {deal.status.value.replace('_', ' ')}")
        
        with cols[6]:
            st.write(deal.due_date)
        
        st.divider()


# =============================================================================
# PAGE: WORKFLOWS
# =============================================================================

def render_workflows_page() -> None:
    """Render the workflows/phase navigator page."""
    render_page_header("Workflows", "Phase Navigator & Gate Approvals", "🔀")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Deal selector
    deals = get_deals()
    deal_options = {d.id: f"{d.name} ({d.customer})" for d in deals}
    
    selected_id = st.selectbox(
        "Select Deal",
        options=list(deal_options.keys()),
        format_func=lambda x: deal_options[x],
        index=0 if not st.session_state.selected_deal else list(deal_options.keys()).index(st.session_state.selected_deal) if st.session_state.selected_deal in deal_options else 0,
    )
    
    deal = get_deal_by_id(selected_id)
    if not deal:
        render_empty_state("📭", "Deal not found")
        return
    
    st.divider()
    
    # Phase Navigator
    st.markdown("### Phase Navigator")
    render_phase_navigator(deal.phase, deal.stage)
    
    st.divider()
    
    # Gate Cards
    st.markdown("### Gate Status")
    
    phases = ["P0", "P1", "P2", "P3", "P4"]
    current_phase_idx = phases.index(deal.phase) if deal.phase in phases else 0
    
    cols = st.columns(2)
    
    for i, gate in enumerate(GATES):
        gate_phase_idx = phases.index(gate.phase) if gate.phase in phases else 0
        
        with cols[i % 2]:
            with st.container():
                # Determine gate status
                if gate_phase_idx < current_phase_idx:
                    status_icon = "✅"
                    status_text = "Passed"
                    status_color = "green"
                elif gate_phase_idx == current_phase_idx:
                    status_icon = "🔄"
                    status_text = "Current"
                    status_color = "orange"
                else:
                    status_icon = "⏳"
                    status_text = "Pending"
                    status_color = "gray"
                
                st.markdown(f"""
                    <div style="background: {COLORS['surface']}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {PHASE_COLORS.get(gate.phase, '#gray')};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>{gate.name}</strong>
                            <span style="color: {status_color};">{status_icon} {status_text}</span>
                        </div>
                        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.5rem;">
                            {gate.description}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show checklist for current/next gate
                if gate_phase_idx >= current_phase_idx and gate_phase_idx <= current_phase_idx + 1:
                    with st.expander("📋 Checklist"):
                        for item in gate.checklist:
                            checked = gate_phase_idx < current_phase_idx
                            st.checkbox(item, value=checked, disabled=True, key=f"gate_{gate.id}_{item}")
                        
                        st.caption(f"Approvers: {', '.join(gate.approvers)}")
                        
                        if gate_phase_idx == current_phase_idx:
                            st.button("Request Approval", type="primary", key=f"approve_{gate.id}")


# =============================================================================
# PAGE: ARTIFACTS
# =============================================================================

def render_artifacts_page() -> None:
    """Render the artifacts library page."""
    render_page_header("Artifacts Library", "Document management & version control", "📁")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Search artifacts", placeholder="Search by name...")
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "Draft", "In Review", "Approved"])
    
    with col3:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("📤 Upload", type="primary"):
            st.toast("Upload dialog would open here")
    
    st.divider()
    
    # Artifacts grid
    artifacts = get_artifacts()
    
    # Apply filters
    if search:
        artifacts = [a for a in artifacts if search.lower() in a.name.lower()]
    if status_filter != "All":
        status_map = {"Draft": "DRAFT", "In Review": "IN_REVIEW", "Approved": "APPROVED"}
        artifacts = [a for a in artifacts if a.status.value == status_map.get(status_filter)]
    
    if not artifacts:
        render_empty_state("📭", "No artifacts found", "Upload your first document to get started")
        return
    
    # Display as cards
    cols = st.columns(3)
    for i, artifact in enumerate(artifacts):
        with cols[i % 3]:
            with st.container():
                # Status color
                status_color = "green" if artifact.status == ArtifactStatus.APPROVED else "orange" if artifact.status == ArtifactStatus.IN_REVIEW else "gray"
                
                st.markdown(f"""
                    <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="font-weight: 600;">{artifact.name[:35]}{'...' if len(artifact.name) > 35 else ''}</div>
                            <span style="background: {'#D1FAE5' if status_color == 'green' else '#FEF3C7' if status_color == 'orange' else '#F3F4F6'}; 
                                         color: {'#065F46' if status_color == 'green' else '#92400E' if status_color == 'orange' else '#374151'};
                                         padding: 2px 8px; border-radius: 9999px; font-size: 0.7rem;">
                                {artifact.status.value.replace('_', ' ')}
                            </span>
                        </div>
                        <div style="font-size: 0.75rem; color: {COLORS['text_secondary']}; margin-top: 0.5rem;">
                            {artifact.deal_name} · {artifact.version}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Compliance meter (if applicable)
                if artifact.compliance_pct is not None:
                    st.progress(artifact.compliance_pct / 100)
                    st.caption(f"Compliance: {artifact.compliance_pct}%")
                
                # Actions
                col_a, col_b = st.columns(2)
                with col_a:
                    st.button("👁️ View", key=f"view_{artifact.id}", use_container_width=True)
                with col_b:
                    st.button("📥 Download", key=f"dl_{artifact.id}", use_container_width=True)


# =============================================================================
# PAGE: COMPLIANCE
# =============================================================================

def render_compliance_page() -> None:
    """Render the compliance matrix page."""
    render_page_header("Compliance Matrix", "Requirement tracking & evidence mapping", "🛡️")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Deal selector
    deals = get_deals()
    deal_options = {d.id: d.name for d in deals}
    selected_id = st.selectbox("Select Deal", options=list(deal_options.keys()), format_func=lambda x: deal_options[x])
    
    # Stats
    stats = get_compliance_stats(selected_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requirements", stats["total"])
    with col2:
        st.metric("Addressed", stats["addressed"], delta=f"{stats['coverage_pct']}%")
    with col3:
        st.metric("Partial", stats["partial"])
    with col4:
        st.metric("Not Started", stats["not_started"])
    
    # Coverage bar
    st.progress(stats["coverage_pct"] / 100 if stats["total"] > 0 else 0)
    st.caption(f"Overall Compliance Coverage: {stats['coverage_pct']}%")
    
    st.divider()
    
    # Requirements table
    requirements = get_requirements(selected_id)
    
    if not requirements:
        render_empty_state("📭", "No requirements found", "Import requirements from your RFP")
        return
    
    for req in requirements:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])
            
            with col1:
                st.code(req.section)
            
            with col2:
                st.write(req.text[:100] + "..." if len(req.text) > 100 else req.text)
            
            with col3:
                type_color = "red" if req.req_type == RequirementType.SHALL else "orange" if req.req_type == RequirementType.SHOULD else "blue"
                st.markdown(f":{type_color}[{req.req_type.value}]")
            
            with col4:
                status_icon = "✅" if req.status == RequirementStatus.ADDRESSED else "🟡" if req.status == RequirementStatus.PARTIAL else "⬜"
                st.write(f"{status_icon} {req.status.value.replace('_', ' ')}")
            
            with col5:
                st.write(f"📎 {req.evidence_count}")
            
            st.divider()


# =============================================================================
# PAGE: REVIEWS
# =============================================================================

def render_reviews_page() -> None:
    """Render the reviews and issues page."""
    render_page_header("Reviews & Issues", "Color team reviews and issue tracking", "👁️")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    tab1, tab2 = st.tabs(["📋 Reviews", "⚠️ Issues"])
    
    with tab1:
        reviews = get_reviews()
        
        if not reviews:
            render_empty_state("📭", "No reviews scheduled")
            return
        
        cols = st.columns(2)
        for i, review in enumerate(reviews):
            with cols[i % 2]:
                # Color based on review type
                color = REVIEW_COLORS.get(review.review_type.value, "#gray")
                
                st.markdown(f"""
                    <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 12px; 
                                padding: 1rem; margin-bottom: 1rem; border-left: 4px solid {color};">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>{review.review_type.value} Team Review</strong>
                            <span>{review.status.value.replace('_', ' ')}</span>
                        </div>
                        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">
                            {review.deal_name}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Findings", review.findings_count)
                with col_b:
                    st.metric("Critical", review.critical_count)
                with col_c:
                    st.metric("Resolved", review.resolved_count)
                
                st.caption(f"📅 {review.scheduled_date} · Lead: {review.lead}")
                st.divider()
    
    with tab2:
        issues = get_issues()
        
        if not issues:
            render_empty_state("🎉", "No issues!", "All caught up")
            return
        
        for issue in issues:
            severity_icon = "🔴" if issue.severity == IssueSeverity.CRITICAL else "🟡" if issue.severity == IssueSeverity.MAJOR else "⚪"
            status_icon = "✅" if issue.status == IssueStatus.RESOLVED else "🔄" if issue.status == IssueStatus.IN_PROGRESS else "⬜"
            
            with st.expander(f"{severity_icon} {issue.title}"):
                st.write(issue.description)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"**Deal:** {issue.deal_name}")
                with col2:
                    st.caption(f"**Assignee:** {issue.assignee}")
                with col3:
                    st.caption(f"**Due:** {issue.due_date}")
                
                st.write(f"**Status:** {status_icon} {issue.status.value.replace('_', ' ')}")
                
                if issue.resolution:
                    st.success(f"**Resolution:** {issue.resolution}")


# =============================================================================
# PAGE: PARTNERS
# =============================================================================

def render_partners_page() -> None:
    """Render the partners management page."""
    render_page_header("Partner Management", "Teaming agreements, workshare, and collaboration", "🤝")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Actions
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add Partner", type="primary"):
            st.toast("Add partner form would open here")
    
    st.divider()
    
    partners = get_partners()
    
    if not partners:
        render_empty_state("📭", "No partners added", "Add your first teaming partner")
        return
    
    cols = st.columns(2)
    for i, partner in enumerate(partners):
        with cols[i % 2]:
            # Risk color
            risk_color = "green" if partner.risk_level == "LOW" else "orange" if partner.risk_level == "MEDIUM" else "red"
            
            with st.container():
                st.markdown(f"""
                    <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div style="font-weight: 600; font-size: 1.125rem;">{partner.name}</div>
                                <div style="font-size: 0.75rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                                    {partner.partner_type.value.replace('_', ' ')} · {partner.status.value}
                                </div>
                            </div>
                            <span style="color: {risk_color};">● {partner.risk_level} Risk</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Workshare
                st.progress(partner.workshare_pct / 100)
                st.caption(f"Workshare: {partner.workshare_pct}%")
                
                # Details
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption(f"**TA Status:** {partner.ta_status.value.replace('_', ' ')}")
                with col_b:
                    st.caption(f"**Contact:** {partner.contact_name}")
                
                # Associated deals
                st.caption(f"**Deals:** {', '.join(partner.deals)}")
                
                # Actions
                col_x, col_y = st.columns(2)
                with col_x:
                    st.button("💬 Message", key=f"msg_{partner.id}", use_container_width=True)
                with col_y:
                    st.button("📋 View Portal", key=f"portal_{partner.id}", use_container_width=True)
                
                st.divider()


# =============================================================================
# PAGE: PLAYBOOK
# =============================================================================

def render_playbook_page() -> None:
    """Render the playbook/learning engine page."""
    render_page_header("Playbook", "Learning engine & golden examples", "📖")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Category filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        categories = ["all", "WIN_THEME", "DISCRIMINATOR", "BOILERPLATE", "TEMPLATE", "BEST_PRACTICE"]
        category_labels = {
            "all": "All", "WIN_THEME": "Win Themes", "DISCRIMINATOR": "Discriminators",
            "BOILERPLATE": "Boilerplate", "TEMPLATE": "Templates", "BEST_PRACTICE": "Best Practices"
        }
        
        selected_category = st.radio(
            "Category",
            options=categories,
            format_func=lambda x: category_labels[x],
            horizontal=True,
            label_visibility="collapsed",
        )
    
    with col2:
        if st.button("➕ Add Lesson", type="primary"):
            st.toast("Add lesson form would open here")
    
    st.divider()
    
    lessons = get_playbook_lessons(selected_category if selected_category != "all" else None)
    
    if not lessons:
        render_empty_state("📭", "No lessons found", "Add your first golden example")
        return
    
    for lesson in lessons:
        with st.expander(f"⭐ {lesson.title}"):
            # Rating stars
            stars = "⭐" * lesson.rating + "☆" * (5 - lesson.rating)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.caption(f"**Category:** {lesson.category.value.replace('_', ' ')}")
            with col2:
                st.caption(f"**Uses:** {lesson.uses}")
            with col3:
                st.caption(f"**Rating:** {stars}")
            
            st.divider()
            
            st.markdown(lesson.content)
            
            st.divider()
            
            # Tags
            st.caption(f"**Tags:** {', '.join(lesson.tags)}")
            st.caption(f"**Source:** {lesson.source} · Last used: {lesson.last_used}")
            
            # Actions
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("📋 Use This", key=f"use_{lesson.id}", use_container_width=True)
            with col_b:
                st.button("✏️ Edit", key=f"edit_{lesson.id}", use_container_width=True)


# =============================================================================
# PAGE: AI CHAT
# =============================================================================

def render_chat_page() -> None:
    """Render the AI chat page."""
    render_page_header("AI Assistant", "Chat with AMANDA's AI assistants", "💬")
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    # Get current role and filter bots
    current_role = st.session_state.user_role
    role_config = ROLES.get(current_role)
    
    # Filter bots based on role permissions
    available_bots = {}
    for bot_id, bot in BOTS.items():
        if bot.is_private:
            # Private bot - only show if role is in allowed_roles
            if current_role in bot.allowed_roles:
                available_bots[bot_id] = bot
        else:
            # Public bot - show to everyone
            available_bots[bot_id] = bot
    
    # Ensure selected bot is valid for current role
    if st.session_state.selected_bot not in available_bots:
        st.session_state.selected_bot = "general"
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        bot_options = {k: f"{v.icon} {v.name}" for k, v in available_bots.items()}
        
        # Find current index
        bot_keys = list(bot_options.keys())
        current_bot_index = bot_keys.index(st.session_state.selected_bot) if st.session_state.selected_bot in bot_keys else 0
        
        selected_bot = st.selectbox(
            "Select Assistant",
            options=bot_keys,
            format_func=lambda x: bot_options[x],
            index=current_bot_index,
            key="bot_selector",
        )
        
        if selected_bot != st.session_state.selected_bot:
            st.session_state.selected_bot = selected_bot
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    bot = BOTS[st.session_state.selected_bot]
    
    # Bot info with access level indicator
    access_badge = '<span style="background: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">🔒 Private</span>' if bot.is_private else '<span style="background: #D1FAE5; color: #065F46; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">Public</span>'
    
    st.markdown(f"""
        <div style="background: {COLORS['surface']}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <strong>{bot.icon} {bot.name}</strong>
            {access_badge}
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                {bot.description}
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; margin-top: 0.5rem;">
                Available to: {', '.join(bot.allowed_roles) if bot.is_private else 'All users'}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Starter prompts (if no messages)
    if not st.session_state.messages and bot.starters:
        st.markdown("### Quick Start")
        cols = st.columns(len(bot.starters))
        for i, starter in enumerate(bot.starters):
            with cols[i]:
                if st.button(f"{starter.icon} {starter.title}", key=f"starter_{i}", use_container_width=True):
                    if starter.prompt_template:
                        st.session_state.prefill_prompt = starter.prompt_template
                        st.session_state.show_prompt_editor = True
                        st.rerun()
    
    # Prompt editor
    if st.session_state.show_prompt_editor and st.session_state.prefill_prompt:
        st.markdown("### ✏️ Customize Your Prompt")
        edited_prompt = st.text_area(
            "Edit the template:",
            value=st.session_state.prefill_prompt,
            height=150,
            label_visibility="collapsed",
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Cancel"):
                st.session_state.prefill_prompt = None
                st.session_state.show_prompt_editor = False
                st.rerun()
        with col2:
            if st.button("Send →", type="primary"):
                st.session_state.messages.append({"role": "user", "content": edited_prompt})
                st.session_state.prefill_prompt = None
                st.session_state.show_prompt_editor = False
                
                # Get response
                with st.chat_message("assistant"):
                    response = get_ai_response(edited_prompt, bot)
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Chat input
    if not st.session_state.show_prompt_editor:
        user_input = st.chat_input(f"Message {bot.name}...")
        
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            with st.chat_message("assistant"):
                response = get_ai_response(user_input, bot)
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()


def get_ai_response(user_message: str, bot) -> str:
    """Get AI response (demo or real API)."""
    if st.session_state.demo_mode:
        # Use demo engine
        demo_engine = get_demo_engine()
        response_parts = []
        
        with st.spinner("Thinking..."):
            for chunk in demo_engine.get_demo_response(user_message, bot.id):
                response_parts.append(chunk)
        
        return "".join(response_parts)
    
    else:
        # Real API call - check Streamlit secrets first, then env var
        api_key = st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, 'secrets') else None
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            return "⚠️ **API Key Not Configured**\n\nPlease set the `ANTHROPIC_API_KEY` environment variable or enable Demo Mode."
        
        try:
            client = Anthropic(api_key=api_key)
            
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            messages.append({"role": "user", "content": user_message})
            
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
# PAGE: ADMIN
# =============================================================================

def render_admin_page() -> None:
    """Render the admin settings page."""
    render_page_header("Admin Settings", "User management, system configuration & demo controls", "⚙️")
    
    # Access check
    role_config = ROLES.get(st.session_state.user_role)
    if not role_config or not role_config.can_config_system:
        st.error("🚫 Access Denied. Admin privileges required.")
        return
    
    if st.session_state.demo_mode:
        render_demo_mode_banner()
    
    tab1, tab2, tab3 = st.tabs(["👥 Users", "🎬 Demo Scenarios", "🔗 Integrations"])
    
    with tab1:
        users = get_users()
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("➕ Add User", type="primary"):
                st.toast("Add user form would open here")
        
        st.divider()
        
        for user in users:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{user.name}**")
                st.caption(user.email)
            
            with col2:
                role = ROLES.get(user.role)
                st.write(f"{role.icon if role else ''} {role.name if role else user.role}")
            
            with col3:
                status_color = "🟢" if user.status == "ACTIVE" else "🔴"
                st.write(f"{status_color} {user.status}")
            
            with col4:
                st.caption(user.last_login)
            
            with col5:
                st.button("✏️", key=f"edit_user_{user.id}")
            
            st.divider()
    
    with tab2:
        st.markdown("### 🎬 Demo Scenarios")
        st.info("Run pre-configured scenarios to demonstrate AMANDA's capabilities without using API credits.")
        
        demo_engine = get_demo_engine()
        scenarios = demo_engine.get_scenarios()
        
        cols = st.columns(3)
        for i, scenario in enumerate(scenarios):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                        <div style="background: {COLORS['surface']}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                            <strong>{scenario.name}</strong>
                            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.5rem;">
                                {scenario.description}
                            </div>
                            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; margin-top: 0.5rem;">
                                {len(scenario.interactions)} interactions
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("▶️ Run", key=f"run_{scenario.id}", use_container_width=True):
                        demo_engine.enable_demo_mode()
                        first_interaction = demo_engine.start_scenario(scenario.id)
                        
                        if first_interaction:
                            st.session_state.selected_bot = scenario.bot_id
                            st.session_state.messages = []
                            st.session_state.demo_mode = True
                            st.session_state.current_page = "chat"
                            st.session_state.prefill_prompt = first_interaction["user"]
                            st.session_state.show_prompt_editor = True
                            st.rerun()
    
    with tab3:
        st.markdown("### 🔗 Integrations")
        
        integrations = [
            {"name": "SharePoint", "icon": "📁", "status": "Connected", "last_sync": "2 min ago"},
            {"name": "HubSpot CRM", "icon": "🔶", "status": "Connected", "last_sync": "5 min ago"},
            {"name": "Azure AD (SSO)", "icon": "🔐", "status": "Connected", "last_sync": "Active"},
            {"name": "Anthropic API", "icon": "🤖", "status": "Connected" if (st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, 'secrets') else None) or os.getenv("ANTHROPIC_API_KEY") else "Not Configured", "last_sync": "claude-sonnet-4-20250514"},
        ]
        
        cols = st.columns(2)
        for i, integration in enumerate(integrations):
            with cols[i % 2]:
                status_color = "🟢" if integration["status"] == "Connected" else "🔴"
                
                st.markdown(f"""
                    <div style="background: white; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 1.5rem;">{integration['icon']}</span>
                                <strong style="margin-left: 8px;">{integration['name']}</strong>
                            </div>
                            <span>{status_color} {integration['status']}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: {COLORS['text_secondary']}; margin-top: 0.5rem;">
                            {integration['last_sync']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.button("⚙️ Configure", key=f"config_{integration['name']}", use_container_width=True)


# =============================================================================
# ONBOARDING TOUR SYSTEM
# =============================================================================

def render_tour_welcome_prompt() -> None:
    """Show initial welcome prompt asking if user wants a tour."""
    if not st.session_state.show_tour_prompt:
        return
    
    st.markdown("""
        <style>
        .tour-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 9998;
        }
        .tour-modal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25);
            z-index: 9999;
            max-width: 500px;
            width: 90%;
        }
        .tour-modal h2 {
            margin: 0 0 1rem 0;
            color: #1E293B;
        }
        .tour-modal p {
            color: #64748B;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Modal container
    modal = st.container()
    with modal:
        st.markdown("---")
        st.markdown(f"""
        ### 👋 Welcome to AMANDA™!
        
        This appears to be your first visit. Would you like a quick guided tour?
        
        **The tour covers:**
        - Dashboard overview
        - AI Chat assistants  
        - Deals pipeline
        - Demo Mode features
        - Role-based permissions
        
        *Takes about 2 minutes*
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Yes, show me around!", type="primary", use_container_width=True):
                st.session_state.show_tour_prompt = False
                st.session_state.tour_active = True
                st.session_state.tour_step = 0
                st.rerun()
        
        with col2:
            if st.button("⏭️ Skip for now", use_container_width=True):
                st.session_state.show_tour_prompt = False
                st.rerun()
        
        with col3:
            if st.button("🚫 Don't show again", use_container_width=True):
                st.session_state.show_tour_prompt = False
                st.session_state.tour_completed = True
                st.rerun()
        
        st.markdown("---")


def render_tour_modal() -> None:
    """Render the current tour step as a modal dialog."""
    if not st.session_state.tour_active:
        return
    
    tour = get_general_tour()
    current_step = st.session_state.tour_step
    
    if current_step >= len(tour):
        st.session_state.tour_active = False
        st.session_state.tour_completed = True
        st.rerun()
        return
    
    step = tour[current_step]
    total_steps = len(tour)
    progress = (current_step + 1) / total_steps
    
    # Tour modal
    st.markdown("---")
    
    # Progress indicator
    st.progress(progress)
    st.caption(f"Step {current_step + 1} of {total_steps}")
    
    # Step content
    st.markdown(f"### {step.title}")
    st.markdown(step.content)
    
    # Tip box
    if step.tip:
        st.info(f"💡 **Tip:** {step.tip}")
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if current_step > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.tour_step -= 1
                st.rerun()
    
    with col2:
        # Go to related page button
        if step.page != "dashboard" and step.page != st.session_state.current_page:
            if st.button(f"📍 Go to {step.page.title()}", use_container_width=True):
                st.session_state.current_page = step.page
                st.rerun()
    
    with col3:
        if current_step < total_steps - 1:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.tour_step += 1
                st.rerun()
        else:
            if st.button("✅ Finish Tour", type="primary", use_container_width=True):
                st.session_state.tour_active = False
                st.session_state.tour_completed = True
                st.rerun()
    
    with col4:
        if st.button("✖ Exit Tour", use_container_width=True):
            st.session_state.tour_active = False
            st.rerun()
    
    st.markdown("---")


def render_role_tour_modal() -> None:
    """Render role-specific tour steps."""
    if not st.session_state.role_tour_active:
        return
    
    tour = get_tour_for_role(st.session_state.user_role)
    current_step = st.session_state.role_tour_step
    
    if current_step >= len(tour):
        st.session_state.role_tour_active = False
        st.rerun()
        return
    
    step = tour[current_step]
    total_steps = len(tour)
    progress = (current_step + 1) / total_steps
    
    role_config = ROLES.get(st.session_state.user_role)
    role_name = role_config.name if role_config else "User"
    
    # Tour modal
    st.markdown("---")
    st.markdown(f"**🎯 {role_name} Tour**")
    
    # Progress indicator
    st.progress(progress)
    st.caption(f"Step {current_step + 1} of {total_steps}")
    
    # Step content
    st.markdown(f"### {step.title}")
    st.markdown(step.content)
    
    # Tip box
    if step.tip:
        st.info(f"💡 **Tip:** {step.tip}")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_step > 0:
            if st.button("← Back", key="role_prev", use_container_width=True):
                st.session_state.role_tour_step -= 1
                st.rerun()
    
    with col2:
        if current_step < total_steps - 1:
            if st.button("Continue →", key="role_next", type="primary", use_container_width=True):
                st.session_state.role_tour_step += 1
                st.rerun()
        else:
            if st.button("✅ Done", key="role_done", type="primary", use_container_width=True):
                st.session_state.role_tour_active = False
                st.rerun()
    
    with col3:
        if st.button("✖ Skip", key="role_skip", use_container_width=True):
            st.session_state.role_tour_active = False
            st.rerun()
    
    st.markdown("---")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main() -> None:
    """Main application entry point."""
    inject_custom_css()
    init_session_state()
    render_sidebar()
    
    # Show welcome tour prompt for first-time visitors
    if st.session_state.show_tour_prompt and st.session_state.demo_mode:
        render_tour_welcome_prompt()
    
    # Show active tour modal
    if st.session_state.tour_active:
        render_tour_modal()
    
    # Show role-specific tour modal
    if st.session_state.role_tour_active:
        render_role_tour_modal()
    
    # Route to appropriate page
    page = st.session_state.current_page
    
    if page == "dashboard":
        render_dashboard_page()
    elif page == "deals":
        render_deals_page()
    elif page == "workflows":
        render_workflows_page()
    elif page == "artifacts":
        render_artifacts_page()
    elif page == "compliance":
        render_compliance_page()
    elif page == "reviews":
        render_reviews_page()
    elif page == "partners":
        render_partners_page()
    elif page == "playbook":
        render_playbook_page()
    elif page == "chat":
        render_chat_page()
    elif page == "admin":
        render_admin_page()
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()
