"""
AMANDA™ Portal UI Components
=============================
Reusable Streamlit components for consistent UI.

Author: rockITdata LLC
Version: 2.0.0
"""

import streamlit as st
from typing import Optional, Callable
from config import COLORS, PHASE_COLORS, PHASE_NAMES, REVIEW_COLORS, BRAND


# =============================================================================
# CSS STYLES
# =============================================================================

def inject_custom_css() -> None:
    """Inject custom CSS for the portal."""
    st.markdown(f"""
    <style>
        /* Brand Colors */
        :root {{
            --brand-primary: {COLORS['primary']};
            --brand-primary-light: {COLORS['primary_light']};
            --brand-surface: {COLORS['surface']};
            --brand-border: {COLORS['border']};
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Header styling */
        .main-header {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            color: white;
        }}
        
        .main-header h1 {{
            margin: 0;
            font-size: 1.75rem;
            font-weight: 700;
        }}
        
        .main-header p {{
            margin: 0.25rem 0 0 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        
        /* Card styling */
        .metric-card {{
            background: white;
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .metric-card .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin: 0.5rem 0;
        }}
        
        .metric-card .metric-label {{
            font-size: 0.875rem;
            color: {COLORS['text_secondary']};
        }}
        
        .metric-card .metric-delta {{
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }}
        
        .metric-delta.positive {{ color: {COLORS['success']}; }}
        .metric-delta.negative {{ color: {COLORS['error']}; }}
        
        /* Status badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .badge-success {{ background: #D1FAE5; color: #065F46; }}
        .badge-warning {{ background: #FEF3C7; color: #92400E; }}
        .badge-danger {{ background: #FEE2E2; color: #991B1B; }}
        .badge-info {{ background: #DBEAFE; color: #1E40AF; }}
        .badge-default {{ background: #F3F4F6; color: #374151; }}
        
        /* Progress bar */
        .progress-container {{
            width: 100%;
            background: {COLORS['surface']};
            border-radius: 9999px;
            height: 8px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            border-radius: 9999px;
            transition: width 0.3s ease;
        }}
        
        .progress-brand {{ background: {COLORS['primary']}; }}
        .progress-success {{ background: {COLORS['success']}; }}
        .progress-warning {{ background: {COLORS['warning']}; }}
        .progress-danger {{ background: {COLORS['error']}; }}
        
        /* Table styling */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .data-table th {{
            background: {COLORS['surface']};
            padding: 0.75rem 1rem;
            text-align: left;
            font-size: 0.75rem;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid {COLORS['border']};
        }}
        
        .data-table td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid {COLORS['border']};
            font-size: 0.875rem;
            color: {COLORS['text_primary']};
        }}
        
        .data-table tr:hover td {{
            background: {COLORS['surface']};
        }}
        
        /* Phase navigator */
        .phase-dot {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.875rem;
        }}
        
        .phase-dot.active {{
            background: {COLORS['primary']};
            color: white;
            box-shadow: 0 0 0 4px rgba(153, 0, 0, 0.2);
        }}
        
        .phase-dot.complete {{
            background: {COLORS['success']};
            color: white;
        }}
        
        .phase-dot.pending {{
            background: {COLORS['surface']};
            color: {COLORS['text_secondary']};
            border: 2px solid {COLORS['border']};
        }}
        
        /* Sidebar navigation */
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 0.25rem;
        }}
        
        .nav-item:hover {{
            background: {COLORS['surface']};
        }}
        
        .nav-item.active {{
            background: {COLORS['primary']};
            color: white;
        }}
        
        /* Demo mode banner */
        .demo-banner {{
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
            border: 1px solid #F59E0B;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .demo-banner-text {{
            font-size: 0.875rem;
            color: #92400E;
            font-weight: 500;
        }}
        
        /* Chat styling */
        .chat-message {{
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}
        
        .chat-message.user {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
        }}
        
        .chat-message.assistant {{
            background: white;
            border: 1px solid {COLORS['border']};
            border-left: 4px solid {COLORS['primary']};
        }}
        
        /* Starter cards */
        .starter-card {{
            background: white;
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .starter-card:hover {{
            border-color: {COLORS['primary']};
            box-shadow: 0 4px 12px rgba(153, 0, 0, 0.1);
        }}
        
        /* Issue severity indicators */
        .severity-critical {{ color: {COLORS['error']}; }}
        .severity-major {{ color: {COLORS['warning']}; }}
        .severity-minor {{ color: {COLORS['text_secondary']}; }}
        
        /* Custom scrollbar */
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
# HEADER COMPONENTS
# =============================================================================

def render_page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a styled page header."""
    st.markdown(f"""
        <div class="main-header">
            <h1>{icon} {title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, action_label: str = "", action_callback: Callable = None) -> None:
    """Render a section header with optional action button."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {title}")
    if action_label and action_callback:
        with col2:
            if st.button(action_label, key=f"section_action_{title}"):
                action_callback()


# =============================================================================
# METRIC COMPONENTS
# =============================================================================

def render_metric_card(
    label: str, 
    value: str, 
    delta: str = "", 
    delta_positive: bool = True,
    icon: str = ""
) -> None:
    """Render a styled metric card."""
    delta_class = "positive" if delta_positive else "negative"
    delta_prefix = "+" if delta_positive and delta else ""
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta {delta_class}">{delta_prefix}{delta}</div>' if delta else ''}
        </div>
    """, unsafe_allow_html=True)


def render_metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards."""
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            render_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta", ""),
                delta_positive=metric.get("delta_positive", True),
                icon=metric.get("icon", ""),
            )


# =============================================================================
# BADGE COMPONENTS
# =============================================================================

def render_badge(text: str, variant: str = "default") -> str:
    """Return HTML for a status badge."""
    return f'<span class="badge badge-{variant}">{text}</span>'


def status_badge(status: str) -> str:
    """Get badge HTML for a status value."""
    status_variants = {
        "ON_TRACK": ("success", "On Track"),
        "AT_RISK": ("danger", "At Risk"),
        "NEW": ("info", "New"),
        "DELAYED": ("warning", "Delayed"),
        "ACTIVE": ("success", "Active"),
        "INACTIVE": ("default", "Inactive"),
        "DRAFT": ("default", "Draft"),
        "IN_REVIEW": ("warning", "In Review"),
        "APPROVED": ("success", "Approved"),
        "COMPLETED": ("success", "Completed"),
        "IN_PROGRESS": ("warning", "In Progress"),
        "SCHEDULED": ("info", "Scheduled"),
        "OPEN": ("danger", "Open"),
        "RESOLVED": ("success", "Resolved"),
        "CRITICAL": ("danger", "Critical"),
        "MAJOR": ("warning", "Major"),
        "MINOR": ("default", "Minor"),
    }
    
    variant, label = status_variants.get(status, ("default", status))
    return render_badge(label, variant)


# =============================================================================
# PROGRESS COMPONENTS
# =============================================================================

def render_progress_bar(value: int, max_value: int = 100, variant: str = "brand") -> None:
    """Render a styled progress bar."""
    percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0
    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar progress-{variant}" style="width: {percentage}%"></div>
        </div>
    """, unsafe_allow_html=True)


def render_progress_with_label(
    label: str, 
    value: int, 
    max_value: int = 100, 
    variant: str = "brand",
    show_percentage: bool = True
) -> None:
    """Render a progress bar with label."""
    percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{label}**")
        render_progress_bar(value, max_value, variant)
    with col2:
        if show_percentage:
            st.markdown(f"**{percentage:.0f}%**")


# =============================================================================
# PHASE NAVIGATOR
# =============================================================================

def render_phase_navigator(current_phase: str, current_stage: str = "") -> None:
    """Render the Shipley phase navigator."""
    phases = ["P0", "P1", "P2", "P3", "P4"]
    current_idx = phases.index(current_phase) if current_phase in phases else 0
    
    cols = st.columns(len(phases) * 2 - 1)
    
    for i, phase in enumerate(phases):
        col_idx = i * 2
        with cols[col_idx]:
            if i < current_idx:
                # Completed phase
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="phase-dot complete">✓</div>
                        <div style="margin-top: 8px; font-size: 0.75rem; color: {COLORS['text_secondary']};">
                            {PHASE_NAMES[phase]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            elif i == current_idx:
                # Current phase
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="phase-dot active">{phase}</div>
                        <div style="margin-top: 8px; font-size: 0.75rem; font-weight: 600; color: {COLORS['primary']};">
                            {PHASE_NAMES[phase]}
                        </div>
                        {f'<div style="margin-top: 4px;"><span class="badge badge-warning">{current_stage}</span></div>' if current_stage else ''}
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Future phase
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="phase-dot pending">{phase}</div>
                        <div style="margin-top: 8px; font-size: 0.75rem; color: {COLORS['text_muted']};">
                            {PHASE_NAMES[phase]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Add connector line between phases
        if i < len(phases) - 1:
            with cols[col_idx + 1]:
                line_color = COLORS['success'] if i < current_idx else COLORS['border']
                st.markdown(f"""
                    <div style="height: 48px; display: flex; align-items: center;">
                        <div style="height: 4px; width: 100%; background: {line_color}; border-radius: 2px;"></div>
                    </div>
                """, unsafe_allow_html=True)


# =============================================================================
# DEMO MODE BANNER
# =============================================================================

def render_demo_mode_banner() -> None:
    """Render the demo mode indicator banner."""
    st.markdown("""
        <div class="demo-banner">
            <span>🎬</span>
            <span class="demo-banner-text">Demo Mode Active — Responses are simulated (no API calls)</span>
        </div>
    """, unsafe_allow_html=True)


# =============================================================================
# EMPTY STATE
# =============================================================================

def render_empty_state(
    icon: str = "📭", 
    title: str = "No data found", 
    message: str = "",
    action_label: str = "",
    action_callback: Callable = None
) -> None:
    """Render an empty state placeholder."""
    st.markdown(f"""
        <div style="text-align: center; padding: 3rem; color: {COLORS['text_secondary']};">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">{title}</div>
            {f'<div style="margin-top: 0.5rem;">{message}</div>' if message else ''}
        </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, type="primary"):
                action_callback()


# =============================================================================
# DATA DISPLAY
# =============================================================================

def format_currency(value: int) -> str:
    """Format a number as currency."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.0f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,}"


def format_date(date_str: str) -> str:
    """Format a date string for display."""
    # Simple pass-through for now; can add formatting logic
    return date_str


# =============================================================================
# LOADING STATE
# =============================================================================

def render_loading(message: str = "Loading...") -> None:
    """Render a loading indicator."""
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem; color: {COLORS['text_secondary']};">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⏳</div>
            <div>{message}</div>
        </div>
    """, unsafe_allow_html=True)
