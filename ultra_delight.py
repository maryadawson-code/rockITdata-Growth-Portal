"""
Ultra-Delight Module for AMANDA Portal
Premium animations and interactions
"""

import streamlit as st
from typing import Optional, Literal
import time

# ============================================================================
# CSS ANIMATIONS
# ============================================================================

ULTRA_DELIGHT_CSS = """
<style>
/* ===== AURORA CELEBRATION ===== */
@keyframes aurora-wave {
    0%, 100% { transform: translateX(-25%) skewX(-5deg); opacity: 0.3; }
    50% { transform: translateX(25%) skewX(5deg); opacity: 0.6; }
}

@keyframes confetti-fall {
    0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
    100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
}

@keyframes celebration-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }
    50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.8); }
}

.aurora-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #1a1a2e 0%, #4a1942 50%, #1a1a2e 100%);
    z-index: 9998;
}

.aurora-wave {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, 
        rgba(34, 197, 94, 0.2) 0%, 
        rgba(59, 130, 246, 0.2) 33%, 
        rgba(168, 85, 247, 0.2) 66%, 
        rgba(236, 72, 153, 0.2) 100%);
    animation: aurora-wave 8s ease-in-out infinite;
}

.celebration-card {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 48px;
    text-align: center;
    z-index: 9999;
    border: 1px solid rgba(255, 255, 255, 0.2);
    animation: celebration-pulse 2s ease-in-out infinite;
}

.trophy-icon {
    width: 96px;
    height: 96px;
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px;
    font-size: 48px;
    animation: glow-pulse 2s ease-in-out infinite;
}

.confetti {
    position: fixed;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    animation: confetti-fall 3s ease-in forwards;
    z-index: 9999;
}

/* ===== VISOR INDICATOR ===== */
@keyframes visor-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
}

@keyframes visor-thinking {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}

.visor-container {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: #f8fafc;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
}

.visor-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    position: relative;
}

.visor-dot::before {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 4px;
    height: 4px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 50%;
}

.visor-idle { background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%); }
.visor-thinking { 
    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); 
    animation: visor-thinking 1.5s ease-in-out infinite;
}
.visor-success { 
    background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%); 
    animation: visor-pulse 2s ease-in-out infinite;
}
.visor-warning { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.visor-error { background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); }
.visor-celebrating { 
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%); 
    animation: visor-pulse 0.5s ease-in-out infinite;
}

.visor-label {
    font-size: 12px;
    font-weight: 500;
    color: #64748b;
}

/* ===== TOAST NOTIFICATIONS ===== */
@keyframes toast-slide-in {
    0% { transform: translateX(100%); opacity: 0; }
    100% { transform: translateX(0); opacity: 1; }
}

@keyframes toast-slide-out {
    0% { transform: translateX(0); opacity: 1; }
    100% { transform: translateX(100%); opacity: 0; }
}

.toast-container {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 9999;
    animation: toast-slide-in 0.3s ease-out;
}

.toast {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    border-left: 4px solid;
    min-width: 300px;
}

.toast-success { border-color: #22c55e; }
.toast-info { border-color: #3b82f6; }
.toast-warning { border-color: #f59e0b; }
.toast-error { border-color: #ef4444; }
.toast-celebration { border-color: #a855f7; }

.toast-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.toast-success .toast-icon { background: #dcfce7; }
.toast-info .toast-icon { background: #dbeafe; }
.toast-warning .toast-icon { background: #fef3c7; }
.toast-error .toast-icon { background: #fee2e2; }
.toast-celebration .toast-icon { background: #f3e8ff; }

.toast-message {
    font-size: 14px;
    font-weight: 500;
    color: #1e293b;
}

/* ===== PROGRESS RING ===== */
.progress-ring-container {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.progress-ring-text {
    position: absolute;
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
}

/* ===== SKELETON LOADING ===== */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.skeleton {
    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
}

.skeleton-text {
    height: 16px;
    margin-bottom: 8px;
}

.skeleton-title {
    height: 24px;
    width: 60%;
    margin-bottom: 12px;
}

.skeleton-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
}

/* ===== RIPPLE EFFECT ===== */
@keyframes ripple {
    0% { transform: scale(0); opacity: 0.5; }
    100% { transform: scale(4); opacity: 0; }
}

.ripple-button {
    position: relative;
    overflow: hidden;
}

.ripple-button::after {
    content: '';
    position: absolute;
    width: 100px;
    height: 100px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: scale(0);
    pointer-events: none;
}

.ripple-button:active::after {
    animation: ripple 0.6s ease-out;
}

/* ===== SMOOTH TRANSITIONS ===== */
.fade-in {
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}

.scale-in {
    animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
    0% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1); }
}

/* ===== CARD HOVER EFFECTS ===== */
.hover-lift {
    transition: all 0.2s ease;
}

.hover-lift:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* ===== GRADIENT TEXT ===== */
.gradient-text {
    background: linear-gradient(135deg, #990000 0%, #cc3333 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-text-gold {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-text-success {
    background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
</style>
"""


# ============================================================================
# VISOR COMPONENT
# ============================================================================

def render_visor(
    status: Literal["idle", "thinking", "success", "warning", "error", "celebrating"] = "idle",
    show_label: bool = True
) -> None:
    """
    Render a reactive visor status indicator.
    
    Args:
        status: Current status (idle, thinking, success, warning, error, celebrating)
        show_label: Whether to show the status label
    """
    status_config = {
        "idle": {"label": "Ready", "icon": "⚪"},
        "thinking": {"label": "Processing...", "icon": "🔵"},
        "success": {"label": "Complete", "icon": "🟢"},
        "warning": {"label": "Attention", "icon": "🟡"},
        "error": {"label": "Error", "icon": "🔴"},
        "celebrating": {"label": "Celebrating!", "icon": "🟣"},
    }
    
    config = status_config.get(status, status_config["idle"])
    
    label_html = f'<span class="visor-label">{config["label"]}</span>' if show_label else ''
    
    st.markdown(f"""
        <div class="visor-container">
            <div class="visor-dot visor-{status}"></div>
            {label_html}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# TOAST NOTIFICATIONS
# ============================================================================

def show_toast(
    message: str,
    type: Literal["success", "info", "warning", "error", "celebration"] = "info",
    duration: int = 4
) -> None:
    """
    Show a toast notification.
    
    Args:
        message: The message to display
        type: Type of toast (success, info, warning, error, celebration)
        duration: How long to show (seconds) - note: Streamlit will rerun
    """
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✕",
        "celebration": "🎉",
    }
    
    icon = icons.get(type, "ℹ")
    
    toast_html = f"""
        <div class="toast-container">
            <div class="toast toast-{type}">
                <div class="toast-icon">{icon}</div>
                <div class="toast-message">{message}</div>
            </div>
        </div>
    """
    
    # Use a placeholder that can be cleared
    placeholder = st.empty()
    placeholder.markdown(toast_html, unsafe_allow_html=True)
    
    # Store in session state for potential clearing
    if "active_toasts" not in st.session_state:
        st.session_state.active_toasts = []
    st.session_state.active_toasts.append(placeholder)


# ============================================================================
# AURORA CELEBRATION
# ============================================================================

def show_aurora_celebration(
    deal_name: str,
    deal_value: str,
    days_in_pipeline: int = 0,
    team_size: int = 0,
    final_pwin: int = 0
) -> None:
    """
    Show the Aurora celebration for a won deal.
    
    Args:
        deal_name: Name of the won deal
        deal_value: Formatted value string (e.g., "$45M")
        days_in_pipeline: Number of days the deal was in pipeline
        team_size: Number of team members involved
        final_pwin: Final win probability percentage
    """
    # Generate confetti elements
    confetti_colors = ["#990000", "#FFD700", "#22c55e", "#3b82f6", "#a855f7"]
    confetti_html = ""
    
    import random
    for i in range(30):
        color = random.choice(confetti_colors)
        left = random.randint(0, 100)
        delay = random.uniform(0, 2)
        size = random.randint(8, 16)
        confetti_html += f"""
            <div class="confetti" style="
                left: {left}%;
                background: {color};
                width: {size}px;
                height: {size}px;
                animation-delay: {delay}s;
            "></div>
        """
    
    celebration_html = f"""
        <div class="aurora-bg">
            <div class="aurora-wave"></div>
            <div class="aurora-wave" style="animation-delay: 2s; animation-direction: reverse;"></div>
            {confetti_html}
        </div>
        <div class="celebration-card">
            <div class="trophy-icon">🏆</div>
            <h1 style="color: white; font-size: 36px; margin: 0 0 8px 0;">🎉 DEAL WON!</h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 24px; margin: 0 0 8px 0; font-weight: 600;">
                {deal_name}
            </p>
            <p class="gradient-text-success" style="font-size: 48px; font-weight: 700; margin: 0 0 24px 0;">
                {deal_value}
            </p>
            <div style="display: flex; justify-content: center; gap: 32px; margin-bottom: 32px;">
                <div style="text-align: center;">
                    <div style="color: white; font-size: 28px; font-weight: 700;">{days_in_pipeline}</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Days in Pipeline</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: white; font-size: 28px; font-weight: 700;">{team_size}</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Team Members</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: white; font-size: 28px; font-weight: 700;">{final_pwin}%</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 12px;">Final pWin</div>
                </div>
            </div>
        </div>
    """
    
    st.markdown(celebration_html, unsafe_allow_html=True)


# ============================================================================
# PROGRESS RING
# ============================================================================

def render_progress_ring(
    progress: int,
    size: int = 120,
    stroke_width: int = 8,
    color: str = "#990000",
    label: str = ""
) -> None:
    """
    Render an animated circular progress indicator.
    
    Args:
        progress: Progress percentage (0-100)
        size: Size of the ring in pixels
        stroke_width: Width of the progress stroke
        color: Color of the progress stroke
        label: Optional label below the percentage
    """
    radius = (size - stroke_width) / 2
    circumference = radius * 2 * 3.14159
    offset = circumference - (progress / 100) * circumference
    
    label_html = f'<div style="font-size: 12px; color: #64748b; margin-top: 4px;">{label}</div>' if label else ''
    
    st.markdown(f"""
        <div class="progress-ring-container" style="width: {size}px; height: {size}px;">
            <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
                <circle
                    cx="{size/2}"
                    cy="{size/2}"
                    r="{radius}"
                    fill="none"
                    stroke="#e5e7eb"
                    stroke-width="{stroke_width}"
                />
                <circle
                    cx="{size/2}"
                    cy="{size/2}"
                    r="{radius}"
                    fill="none"
                    stroke="{color}"
                    stroke-width="{stroke_width}"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    stroke-linecap="round"
                    style="transition: stroke-dashoffset 1s ease-out;"
                />
            </svg>
            <div class="progress-ring-text" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #1e293b;">{progress}%</div>
                {label_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# SKELETON LOADING
# ============================================================================

def render_skeleton_card() -> None:
    """Render a skeleton loading card with shimmer effect."""
    st.markdown("""
        <div class="skeleton-card">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text" style="width: 80%;"></div>
            <div class="skeleton skeleton-text" style="width: 60%;"></div>
            <div style="display: flex; gap: 8px; margin-top: 12px;">
                <div class="skeleton" style="width: 60px; height: 24px; border-radius: 12px;"></div>
                <div class="skeleton" style="width: 80px; height: 24px; border-radius: 12px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_skeleton_text(lines: int = 3, widths: list = None) -> None:
    """Render skeleton text lines with shimmer effect."""
    if widths is None:
        widths = [100, 80, 60][:lines]
    
    lines_html = ""
    for i, width in enumerate(widths):
        lines_html += f'<div class="skeleton skeleton-text" style="width: {width}%;"></div>'
    
    st.markdown(f"<div>{lines_html}</div>", unsafe_allow_html=True)


# ============================================================================
# ANIMATED METRIC CARD
# ============================================================================

def render_animated_metric(
    label: str,
    value: str,
    delta: str = None,
    delta_color: str = "normal",
    icon: str = None
) -> None:
    """
    Render an animated metric card with optional icon and delta.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator
        delta_color: Color for delta (normal, inverse, off)
        icon: Optional emoji icon
    """
    delta_html = ""
    if delta:
        color = "#22c55e" if delta_color == "normal" else "#ef4444" if delta_color == "inverse" else "#64748b"
        delta_html = f'<div style="font-size: 12px; color: {color}; margin-top: 4px;">{delta}</div>'
    
    icon_html = f'<span style="font-size: 24px; margin-right: 8px;">{icon}</span>' if icon else ''
    
    st.markdown(f"""
        <div class="hover-lift fade-in" style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                {icon_html}
                <span style="font-size: 14px; color: #64748b;">{label}</span>
            </div>
            <div style="font-size: 28px; font-weight: 700; color: #1e293b;">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_ultra_delight() -> None:
    """Initialize Ultra-Delight CSS styles. Call this once at app start."""
    st.markdown(ULTRA_DELIGHT_CSS, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE HELPERS
# ============================================================================

def trigger_celebration(deal_name: str, deal_value: str, **kwargs) -> None:
    """Store celebration data in session state to trigger on next render."""
    st.session_state.celebration_pending = {
        "deal_name": deal_name,
        "deal_value": deal_value,
        **kwargs
    }


def check_pending_celebration() -> None:
    """Check for and render any pending celebrations."""
    if st.session_state.get("celebration_pending"):
        data = st.session_state.celebration_pending
        show_aurora_celebration(**data)
        
        # Add close button
        if st.button("🚀 Continue Winning", key="close_celebration"):
            st.session_state.celebration_pending = None
            st.rerun()


def set_visor_status(status: str) -> None:
    """Set the visor status in session state."""
    st.session_state.visor_status = status


def get_visor_status() -> str:
    """Get the current visor status from session state."""
    return st.session_state.get("visor_status", "idle")


# ============================================================================
# DEMO PAGE
# ============================================================================

def show_ultra_delight_demo() -> None:
    """Show a demo page of all Ultra-Delight components."""
    init_ultra_delight()
    
    st.markdown("""
        <h1 class="gradient-text" style="font-size: 32px; margin-bottom: 8px;">
            ✨ Ultra-Delight Components
        </h1>
        <p style="color: #64748b; margin-bottom: 32px;">
            Premium animations and interactions for AMANDA Portal
        </p>
    """, unsafe_allow_html=True)
    
    # Check for pending celebrations
    check_pending_celebration()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔮 Visor Status")
        status = st.selectbox(
            "Select status",
            ["idle", "thinking", "success", "warning", "error", "celebrating"]
        )
        render_visor(status)
        
        st.markdown("---")
        
        st.markdown("### 📊 Progress Ring")
        progress = st.slider("Progress", 0, 100, 75)
        render_progress_ring(progress, label="Compliance")
        
    with col2:
        st.markdown("### 🔔 Toast Notifications")
        toast_type = st.selectbox(
            "Toast type",
            ["success", "info", "warning", "error", "celebration"]
        )
        if st.button("Show Toast"):
            messages = {
                "success": "Proposal saved successfully!",
                "info": "AI is analyzing your document...",
                "warning": "Compliance below 95% threshold",
                "error": "Failed to connect to server",
                "celebration": "You hit 100% compliance! 🎉",
            }
            show_toast(messages[toast_type], toast_type)
        
        st.markdown("---")
        
        st.markdown("### 🎆 Aurora Celebration")
        if st.button("🏆 Trigger Deal Won!", type="primary"):
            trigger_celebration(
                deal_name="VA EHR Modernization",
                deal_value="$45,000,000",
                days_in_pipeline=247,
                team_size=12,
                final_pwin=89
            )
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 💀 Skeleton Loading")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_skeleton_card()
    with col2:
        render_skeleton_card()
    with col3:
        render_skeleton_card()
    
    st.markdown("---")
    
    st.markdown("### 📈 Animated Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_animated_metric("Pipeline Value", "$180.5M", "+$12.5M this month", icon="💰")
    with col2:
        render_animated_metric("Win Rate", "68%", "+5% vs last quarter", icon="🎯")
    with col3:
        render_animated_metric("Active Deals", "24", "3 due this week", delta_color="inverse", icon="📋")
    with col4:
        render_animated_metric("Team Members", "18", "2 new this month", icon="👥")


if __name__ == "__main__":
    st.set_page_config(page_title="Ultra-Delight Demo", layout="wide")
    show_ultra_delight_demo()
