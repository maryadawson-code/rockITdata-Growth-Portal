"""
Pipeline View Module for AMANDA Portal
Visual deal board with Shipley methodology stages
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# ============================================================================
# SHIPLEY STAGE CONFIGURATION
# ============================================================================

SHIPLEY_STAGES = [
    {"id": "gate1", "name": "Gate 1", "subtitle": "Qualify", "color": "#64748b", "icon": "🎯", "order": 1},
    {"id": "blue", "name": "Blue Team", "subtitle": "Strategy", "color": "#3b82f6", "icon": "👥", "order": 2},
    {"id": "kickoff", "name": "Kickoff", "subtitle": "48hr RFP", "color": "#6366f1", "icon": "🚀", "order": 3},
    {"id": "pink", "name": "Pink Team", "subtitle": "30% Draft", "color": "#ec4899", "icon": "📝", "order": 4},
    {"id": "red", "name": "Red Team", "subtitle": "70% Review", "color": "#ef4444", "icon": "🔴", "order": 5},
    {"id": "gold", "name": "Gold Team", "subtitle": "90% Final", "color": "#f59e0b", "icon": "🏆", "order": 6},
    {"id": "whiteglove", "name": "White Glove", "subtitle": "Production", "color": "#a855f7", "icon": "✨", "order": 7},
    {"id": "submitted", "name": "Submitted", "subtitle": "Complete", "color": "#22c55e", "icon": "✅", "order": 8},
]

PRIORITY_CONFIG = {
    "P-0": {"label": "Must Win", "color": "#dc2626", "bg": "#fef2f2", "border": "#fecaca"},
    "P-1": {"label": "Strategic", "color": "#d97706", "bg": "#fffbeb", "border": "#fde68a"},
    "P-2": {"label": "Gap Filler", "color": "#2563eb", "bg": "#eff6ff", "border": "#bfdbfe"},
}

GATE_STATUS_OPTIONS = ["GO", "CONDITIONAL GO", "PAUSE", "NO-GO"]

# ============================================================================
# SAMPLE DATA (Replace with database queries in production)
# ============================================================================

def get_sample_deals() -> List[Dict[str, Any]]:
    """Return sample deal data for demonstration."""
    return [
        {
            "id": 1, 
            "name": "VA EHR Modernization", 
            "client": "Dept of Veterans Affairs",
            "solicitation": "36C10X24R0001",
            "value": 45000000, 
            "pwin": 75, 
            "stage": "red", 
            "priority": "P-0",
            "gate_status": "GO",
            "due_date": (datetime.now() + timedelta(days=26)).strftime("%Y-%m-%d"),
            "capture_lead": "Sarah Chen",
            "proposal_manager": "Mike Rodriguez",
            "compliance": 92,
            "created_at": "2024-11-15",
            "naics": "541512",
            "set_aside": "SDVOSB"
        },
        {
            "id": 2, 
            "name": "DHA Telehealth Platform", 
            "client": "Defense Health Agency",
            "solicitation": "HT0015-24-R-0042",
            "value": 28000000, 
            "pwin": 60, 
            "stage": "pink", 
            "priority": "P-1",
            "gate_status": "GO",
            "due_date": (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d"),
            "capture_lead": "Mike Rodriguez",
            "proposal_manager": "Sarah Chen",
            "compliance": 78,
            "created_at": "2024-12-01",
            "naics": "541519",
            "set_aside": "8(a)"
        },
        {
            "id": 3, 
            "name": "CMS Data Analytics", 
            "client": "Centers for Medicare",
            "solicitation": "75FCMC24R0089",
            "value": 15000000, 
            "pwin": 45, 
            "stage": "blue", 
            "priority": "P-1",
            "gate_status": "CONDITIONAL GO",
            "due_date": (datetime.now() + timedelta(days=80)).strftime("%Y-%m-%d"),
            "capture_lead": "Sarah Chen",
            "proposal_manager": "James Wilson",
            "compliance": 65,
            "created_at": "2024-12-10",
            "naics": "541512",
            "set_aside": "Small Business"
        },
        {
            "id": 4, 
            "name": "FDA Cloud Migration", 
            "client": "Food & Drug Admin",
            "solicitation": "FDA-SOL-1234567",
            "value": 8500000, 
            "pwin": 80, 
            "stage": "gold", 
            "priority": "P-0",
            "gate_status": "GO",
            "due_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "capture_lead": "James Wilson",
            "proposal_manager": "Maria Santos",
            "compliance": 98,
            "created_at": "2024-10-20",
            "naics": "541519",
            "set_aside": "WOSB"
        },
        {
            "id": 5, 
            "name": "IHS Patient Portal", 
            "client": "Indian Health Service",
            "solicitation": "IHS-RFP-2024-0156",
            "value": 12000000, 
            "pwin": 55, 
            "stage": "kickoff", 
            "priority": "P-2",
            "gate_status": "GO",
            "due_date": (datetime.now() + timedelta(days=59)).strftime("%Y-%m-%d"),
            "capture_lead": "Maria Santos",
            "proposal_manager": "Sarah Chen",
            "compliance": 45,
            "created_at": "2025-01-05",
            "naics": "541511",
            "set_aside": "Indian Economic Enterprise"
        },
        {
            "id": 6, 
            "name": "NIH Research Platform", 
            "client": "National Institutes of Health",
            "solicitation": "NIHOD2024000789",
            "value": 22000000, 
            "pwin": 70, 
            "stage": "gate1", 
            "priority": "P-1",
            "gate_status": "GO",
            "due_date": (datetime.now() + timedelta(days=100)).strftime("%Y-%m-%d"),
            "capture_lead": "Mike Rodriguez",
            "proposal_manager": "James Wilson",
            "compliance": 30,
            "created_at": "2025-01-10",
            "naics": "541715",
            "set_aside": "Full & Open"
        },
        {
            "id": 7, 
            "name": "SAMHSA Mental Health", 
            "client": "SAMHSA",
            "solicitation": "SAMHSA-2024-MH-001",
            "value": 9000000, 
            "pwin": 85, 
            "stage": "whiteglove", 
            "priority": "P-0",
            "gate_status": "GO",
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "capture_lead": "Sarah Chen",
            "proposal_manager": "Maria Santos",
            "compliance": 100,
            "created_at": "2024-09-15",
            "naics": "541611",
            "set_aside": "SDVOSB"
        },
        {
            "id": 8, 
            "name": "CDC Surveillance System", 
            "client": "CDC",
            "solicitation": "CDC-RFP-2025-0023",
            "value": 35000000, 
            "pwin": 40, 
            "stage": "gate1", 
            "priority": "P-2",
            "gate_status": "PAUSE",
            "due_date": (datetime.now() + timedelta(days=150)).strftime("%Y-%m-%d"),
            "capture_lead": "James Wilson",
            "proposal_manager": "Mike Rodriguez",
            "compliance": 15,
            "created_at": "2025-01-15",
            "naics": "541512",
            "set_aside": "Small Business"
        },
        {
            "id": 9, 
            "name": "ACF Case Management", 
            "client": "Admin for Children & Families",
            "solicitation": "ACF-OTPS-2024-0089",
            "value": 6000000, 
            "pwin": 90, 
            "stage": "submitted", 
            "priority": "P-1",
            "gate_status": "GO",
            "due_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "capture_lead": "Maria Santos",
            "proposal_manager": "Sarah Chen",
            "compliance": 100,
            "created_at": "2024-08-01",
            "naics": "541611",
            "set_aside": "WOSB"
        },
    ]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_currency(value: float) -> str:
    """Format value as currency string."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def days_until(date_str: str) -> int:
    """Calculate days until a date."""
    try:
        due_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return (due_date - today).days
    except:
        return 999


def get_pwin_color(pwin: int) -> str:
    """Get color based on pWin value."""
    if pwin >= 70:
        return "#22c55e"  # Green
    elif pwin >= 50:
        return "#f59e0b"  # Amber
    return "#ef4444"  # Red


def get_compliance_color(compliance: int) -> str:
    """Get color based on compliance percentage."""
    if compliance >= 95:
        return "#22c55e"  # Green
    elif compliance >= 70:
        return "#f59e0b"  # Amber
    return "#ef4444"  # Red


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_stats_bar(deals: List[Dict]) -> None:
    """Render the top statistics bar."""
    total_value = sum(d["value"] for d in deals)
    avg_pwin = round(sum(d["pwin"] for d in deals) / len(deals)) if deals else 0
    urgent_count = sum(1 for d in deals if days_until(d["due_date"]) <= 7)
    p0_count = sum(1 for d in deals if d["priority"] == "P-0")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Pipeline Value",
            value=format_currency(total_value),
            delta=f"{len(deals)} opportunities"
        )
    
    with col2:
        st.metric(
            label="📈 Avg Win Probability",
            value=f"{avg_pwin}%",
            delta="Weighted average"
        )
    
    with col3:
        st.metric(
            label="⚠️ Due This Week",
            value=urgent_count,
            delta="Urgent attention" if urgent_count > 0 else "All clear",
            delta_color="inverse" if urgent_count > 0 else "normal"
        )
    
    with col4:
        st.metric(
            label="🎯 Must-Win (P-0)",
            value=p0_count,
            delta="Top priority"
        )


def render_deal_card(deal: Dict, stage_color: str) -> None:
    """Render a single deal card."""
    priority_config = PRIORITY_CONFIG.get(deal["priority"], PRIORITY_CONFIG["P-2"])
    days = days_until(deal["due_date"])
    is_urgent = days <= 7
    
    # Card container with custom styling
    card_style = f"""
    <div style="
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s;
    ">
        <!-- Header -->
        <div style="margin-bottom: 12px;">
            <div style="font-weight: 600; color: #111827; font-size: 14px; margin-bottom: 4px;">
                {deal['name']}
            </div>
            <div style="font-size: 12px; color: #6b7280;">
                {deal['client']}
            </div>
        </div>
        
        <!-- Priority & Value -->
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="
                background: {priority_config['bg']};
                color: {priority_config['color']};
                border: 1px solid {priority_config['border']};
                padding: 2px 8px;
                border-radius: 9999px;
                font-size: 11px;
                font-weight: 500;
            ">{deal['priority']}</span>
            <span style="font-weight: 600; color: #111827; font-size: 14px;">
                {format_currency(deal['value'])}
            </span>
        </div>
        
        <!-- Stats -->
        <div style="display: flex; gap: 16px; font-size: 12px; color: #6b7280; margin-bottom: 12px;">
            <span style="color: {get_pwin_color(deal['pwin'])}; font-weight: 500;">
                📈 {deal['pwin']}% pWin
            </span>
            <span style="color: {'#ef4444' if is_urgent else '#6b7280'}; font-weight: {'600' if is_urgent else '400'};">
                📅 {days}d {'⚠️' if is_urgent else ''}
            </span>
        </div>
        
        <!-- Compliance Bar -->
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
                <span style="color: #6b7280;">Compliance</span>
                <span style="color: {get_compliance_color(deal['compliance'])}; font-weight: 500;">
                    {deal['compliance']}%
                </span>
            </div>
            <div style="height: 6px; background: #f3f4f6; border-radius: 9999px; overflow: hidden;">
                <div style="
                    height: 100%;
                    width: {deal['compliance']}%;
                    background: {get_compliance_color(deal['compliance'])};
                    border-radius: 9999px;
                "></div>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid #f3f4f6;
            font-size: 12px;
        ">
            <span style="color: #6b7280;">
                👤 {deal['capture_lead'].split()[0]}
            </span>
            <span style="
                background: {stage_color};
                width: 8px;
                height: 8px;
                border-radius: 50%;
            "></span>
        </div>
    </div>
    """
    
    st.markdown(card_style, unsafe_allow_html=True)
    
    # Add view button
    if st.button(f"📋 View Details", key=f"view_{deal['id']}", use_container_width=True):
        st.session_state.selected_deal = deal


def render_stage_column(stage: Dict, deals: List[Dict]) -> None:
    """Render a single stage column with its deals."""
    total_value = sum(d["value"] for d in deals)
    
    # Column header
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    ">
        <div style="
            width: 40px;
            height: 40px;
            background: {stage['color']};
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        ">{stage['icon']}</div>
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-weight: 600; color: #111827;">{stage['name']}</span>
                <span style="
                    background: #e5e7eb;
                    color: #374151;
                    padding: 2px 8px;
                    border-radius: 9999px;
                    font-size: 12px;
                    font-weight: 500;
                ">{len(deals)}</span>
            </div>
            <div style="font-size: 12px; color: #6b7280;">{stage['subtitle']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pipeline value for this stage
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
        border: 1px solid #e5e7eb;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; color: #6b7280;">Pipeline Value</span>
            <span style="font-weight: 700; color: #111827;">{format_currency(total_value)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Deal cards
    for deal in deals:
        render_deal_card(deal, stage["color"])
    
    # Empty state
    if not deals:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 32px 16px;
            color: #9ca3af;
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">📄</div>
            <div style="font-size: 14px;">No deals in this stage</div>
        </div>
        """, unsafe_allow_html=True)


def render_deal_detail_modal(deal: Dict) -> None:
    """Render deal detail in an expander (modal simulation)."""
    if not deal:
        return
    
    stage = next((s for s in SHIPLEY_STAGES if s["id"] == deal["stage"]), SHIPLEY_STAGES[0])
    priority_config = PRIORITY_CONFIG.get(deal["priority"], PRIORITY_CONFIG["P-2"])
    days = days_until(deal["due_date"])
    
    st.markdown("---")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {stage['color']} 0%, {stage['color']}dd 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; opacity: 0.9;">
            <span style="font-size: 20px;">{stage['icon']}</span>
            <span>{stage['name']} • {stage['subtitle']}</span>
        </div>
        <h2 style="margin: 0 0 8px 0; font-size: 24px;">{deal['name']}</h2>
        <p style="margin: 0; opacity: 0.9;">{deal['client']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Contract Value", format_currency(deal['value']))
    with col2:
        st.metric("📈 Win Probability", f"{deal['pwin']}%")
    with col3:
        st.metric("📅 Days to Submit", f"{days}d")
    with col4:
        st.metric("✅ Compliance", f"{deal['compliance']}%")
    
    st.markdown("---")
    
    # Details in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Opportunity Details")
        st.markdown(f"""
        | Field | Value |
        |-------|-------|
        | **Priority** | {deal['priority']} - {priority_config['label']} |
        | **Gate Status** | {deal.get('gate_status', 'GO')} |
        | **Solicitation** | {deal.get('solicitation', 'N/A')} |
        | **NAICS** | {deal.get('naics', 'N/A')} |
        | **Set-Aside** | {deal.get('set_aside', 'N/A')} |
        | **Due Date** | {deal['due_date']} |
        """)
    
    with col2:
        st.markdown("#### Team")
        st.markdown(f"""
        | Role | Assigned |
        |------|----------|
        | **Capture Lead** | {deal['capture_lead']} |
        | **Proposal Manager** | {deal.get('proposal_manager', 'TBD')} |
        """)
        
        st.markdown("#### Compliance Progress")
        compliance = deal['compliance']
        st.progress(compliance / 100)
        if compliance < 95:
            st.warning(f"⚠️ Below 95% threshold. Review compliance items before advancing.")
    
    # Actions
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🤖 Open in AMANDA", use_container_width=True, type="primary"):
            st.session_state.current_view = "chat"
            st.session_state.selected_deal = None
            st.rerun()
    with col2:
        if st.button("✏️ Edit Deal", use_container_width=True):
            st.info("Edit functionality coming soon")
    with col3:
        stage_names = [s["name"] for s in SHIPLEY_STAGES]
        current_idx = next((i for i, s in enumerate(SHIPLEY_STAGES) if s["id"] == deal["stage"]), 0)
        new_stage = st.selectbox("Move to Stage", stage_names, index=current_idx, key="move_stage")
    with col4:
        if st.button("❌ Close", use_container_width=True):
            st.session_state.selected_deal = None
            st.rerun()


# ============================================================================
# MAIN PIPELINE VIEW
# ============================================================================

def render_pipeline_view() -> None:
    """Main entry point for the Pipeline View."""
    
    # Initialize session state
    if "selected_deal" not in st.session_state:
        st.session_state.selected_deal = None
    if "pipeline_filter_priority" not in st.session_state:
        st.session_state.pipeline_filter_priority = "All"
    if "pipeline_search" not in st.session_state:
        st.session_state.pipeline_search = ""
    
    # Load deals (replace with database query in production)
    all_deals = get_sample_deals()
    
    # Apply filters
    filtered_deals = all_deals
    
    # Priority filter
    if st.session_state.pipeline_filter_priority != "All":
        filtered_deals = [d for d in filtered_deals if d["priority"] == st.session_state.pipeline_filter_priority]
    
    # Search filter
    if st.session_state.pipeline_search:
        search_lower = st.session_state.pipeline_search.lower()
        filtered_deals = [
            d for d in filtered_deals 
            if search_lower in d["name"].lower() or search_lower in d["client"].lower()
        ]
    
    # ========== HEADER ==========
    st.markdown("""
    <h1 style="margin-bottom: 4px;">📊 Pipeline Board</h1>
    <p style="color: #6b7280; margin-bottom: 24px;">Shipley Methodology • Track opportunities through proposal lifecycle</p>
    """, unsafe_allow_html=True)
    
    # ========== STATS BAR ==========
    render_stats_bar(filtered_deals)
    
    st.markdown("---")
    
    # ========== FILTERS ==========
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.session_state.pipeline_search = st.text_input(
            "🔍 Search",
            value=st.session_state.pipeline_search,
            placeholder="Search opportunities...",
            label_visibility="collapsed"
        )
    
    with col2:
        priority_options = ["All", "P-0", "P-1", "P-2"]
        st.session_state.pipeline_filter_priority = st.selectbox(
            "Priority Filter",
            priority_options,
            index=priority_options.index(st.session_state.pipeline_filter_priority),
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("➕ New Opportunity", use_container_width=True, type="primary"):
            st.info("New opportunity form coming soon")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== DEAL DETAIL (if selected) ==========
    if st.session_state.selected_deal:
        render_deal_detail_modal(st.session_state.selected_deal)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== BOARD ==========
    # Group deals by stage
    deals_by_stage = {stage["id"]: [] for stage in SHIPLEY_STAGES}
    for deal in filtered_deals:
        if deal["stage"] in deals_by_stage:
            deals_by_stage[deal["stage"]].append(deal)
    
    # Create columns for each stage
    # Using tabs for better mobile experience
    stage_tabs = st.tabs([f"{s['icon']} {s['name']} ({len(deals_by_stage[s['id']])})" for s in SHIPLEY_STAGES])
    
    for i, (tab, stage) in enumerate(zip(stage_tabs, SHIPLEY_STAGES)):
        with tab:
            stage_deals = deals_by_stage[stage["id"]]
            
            # Stage header
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {stage['color']}22 0%, {stage['color']}11 100%);
                border-left: 4px solid {stage['color']};
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 16px;
            ">
                <div style="font-weight: 600; color: #111827;">{stage['name']}</div>
                <div style="font-size: 13px; color: #6b7280;">{stage['subtitle']}</div>
                <div style="font-size: 14px; font-weight: 600; color: {stage['color']}; margin-top: 8px;">
                    {format_currency(sum(d['value'] for d in stage_deals))} pipeline value
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if stage_deals:
                # Sort by priority then due date
                stage_deals.sort(key=lambda d: (
                    {"P-0": 0, "P-1": 1, "P-2": 2}.get(d["priority"], 3),
                    d["due_date"]
                ))
                
                for deal in stage_deals:
                    render_deal_card(deal, stage["color"])
            else:
                st.info("No opportunities in this stage")


# ============================================================================
# EXPORT FOR APP.PY
# ============================================================================

def show_pipeline():
    """Entry point called from app.py"""
    render_pipeline_view()


if __name__ == "__main__":
    # For testing standalone
    st.set_page_config(page_title="Pipeline Board", layout="wide")
    render_pipeline_view()
