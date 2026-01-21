"""
AMANDA Portal Admin Dashboard
==============================
Comprehensive admin control panel for user management, token tracking,
audit logs, and system configuration.

Author: rockITdata LLC
Version: 7.3
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import io

# Import database module
try:
    from database import (
        initialize as init_db,
        get_all_users,
        get_user_by_id,
        create_user,
        update_user,
        delete_user,
        reset_password,
        get_audit_logs,
        get_audit_log_count,
        get_token_usage_summary,
        get_monthly_token_usage,
        get_config,
        set_config,
        get_all_config,
        bulk_import_users,
        log_audit,
        User,
    )
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Import HubSpot status (optional)
try:
    from hubspot_connector import get_hubspot_client
    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False


# =============================================================================
# CONSTANTS
# =============================================================================

ROLES = {
    "admin": {"name": "Admin", "color": "#990000", "icon": "👑"},
    "exec": {"name": "Executive", "color": "#7C3AED", "icon": "📊"},
    "capture_lead": {"name": "Capture Lead", "color": "#2563EB", "icon": "🎯"},
    "proposal_manager": {"name": "Proposal Manager", "color": "#0891B2", "icon": "📋"},
    "solution_architect": {"name": "Solution Architect", "color": "#059669", "icon": "🏗️"},
    "analyst": {"name": "Analyst", "color": "#D97706", "icon": "🔍"},
    "finance": {"name": "Finance", "color": "#DC2626", "icon": "💰"},
    "contracts": {"name": "Contracts", "color": "#4F46E5", "icon": "📝"},
    "hr": {"name": "HR/Staffing", "color": "#DB2777", "icon": "👥"},
    "partner": {"name": "Partner", "color": "#6B7280", "icon": "🤝"},
    "standard": {"name": "Standard User", "color": "#9CA3AF", "icon": "👤"},
}

SEVERITY_COLORS = {
    "info": "#3B82F6",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "critical": "#DC2626",
}


# =============================================================================
# STYLING
# =============================================================================

ADMIN_STYLES = """
<style>
.admin-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid #E2E8F0;
}

.admin-title {
    font-size: 28px;
    font-weight: 700;
    color: #1E293B;
    margin: 0;
}

.admin-subtitle {
    color: #64748B;
    font-size: 14px;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.stat-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #1E293B;
}

.stat-value.green { color: #059669; }
.stat-value.red { color: #990000; }
.stat-value.blue { color: #2563EB; }
.stat-value.orange { color: #D97706; }

.stat-label {
    font-size: 12px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

.user-row {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-bottom: 8px;
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #F1F5F9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-right: 12px;
}

.user-info {
    flex: 1;
}

.user-name {
    font-weight: 600;
    color: #1E293B;
}

.user-email {
    font-size: 13px;
    color: #64748B;
}

.role-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
}

.audit-row {
    padding: 12px;
    border-left: 3px solid;
    background: #F8FAFC;
    margin-bottom: 8px;
    border-radius: 0 8px 8px 0;
}

.audit-action {
    font-weight: 600;
    color: #1E293B;
}

.audit-time {
    font-size: 12px;
    color: #64748B;
}

.audit-details {
    font-size: 13px;
    color: #475569;
    margin-top: 4px;
}

.integration-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.integration-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.integration-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 500;
}

.status-connected {
    background: #DCFCE7;
    color: #166534;
}

.status-disconnected {
    background: #FEE2E2;
    color: #991B1B;
}

.status-pending {
    background: #FEF3C7;
    color: #92400E;
}

.token-meter {
    background: #F1F5F9;
    border-radius: 8px;
    height: 24px;
    overflow: hidden;
    position: relative;
}

.token-meter-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.3s ease;
}

.token-meter-label {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 12px;
    font-weight: 600;
    color: #1E293B;
}
</style>
"""


# =============================================================================
# SESSION STATE
# =============================================================================

def init_admin_state() -> None:
    """Initialize admin dashboard session state."""
    defaults = {
        "admin_tab": "overview",
        "edit_user_id": None,
        "show_create_user": False,
        "show_bulk_import": False,
        "audit_page": 0,
        "audit_filter_action": None,
        "audit_filter_severity": None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# OVERVIEW TAB
# =============================================================================

def render_overview_tab() -> None:
    """Render the overview/dashboard tab."""
    
    # Get stats
    users = get_all_users(include_inactive=True)
    active_users = [u for u in users if u.is_active]
    token_summary = get_token_usage_summary(days=30)
    monthly_budget = int(get_config("token_budget_monthly", "100000"))
    
    # Stats grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Users",
            value=len(active_users),
            delta=f"{len(users) - len(active_users)} inactive"
        )
    
    with col2:
        st.metric(
            label="Token Usage (30d)",
            value=f"{token_summary['total_tokens']:,}",
            delta=f"${token_summary['total_cost_usd']:.2f}"
        )
    
    with col3:
        usage_pct = (token_summary['total_tokens'] / monthly_budget * 100) if monthly_budget > 0 else 0
        st.metric(
            label="Budget Used",
            value=f"{usage_pct:.1f}%",
            delta=f"{monthly_budget - token_summary['total_tokens']:,} remaining"
        )
    
    with col4:
        recent_logs = get_audit_log_count(severity="warning") + get_audit_log_count(severity="error")
        st.metric(
            label="Alerts (30d)",
            value=recent_logs,
            delta="warnings + errors"
        )
    
    st.divider()
    
    # Two column layout
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🔗 Integration Status")
        
        # HubSpot status
        hubspot_connected = False
        if HUBSPOT_AVAILABLE:
            client = get_hubspot_client() if 'get_hubspot_client' in dir() else None
            if client:
                status = client.test_connection()
                hubspot_connected = status.get("connected", False)
        
        st.markdown(f"""
        <div class="integration-card">
            <div class="integration-icon" style="background: #FFF1ED;">🔶</div>
            <div style="flex: 1;">
                <strong>HubSpot CRM</strong>
                <p style="margin: 0; font-size: 13px; color: #64748B;">Pipeline sync & deal tracking</p>
            </div>
            <span class="integration-status {'status-connected' if hubspot_connected else 'status-disconnected'}">
                {'✓ Connected' if hubspot_connected else '✗ Disconnected'}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # SharePoint status (placeholder)
        st.markdown("""
        <div class="integration-card">
            <div class="integration-icon" style="background: #E0F2FE;">📁</div>
            <div style="flex: 1;">
                <strong>SharePoint</strong>
                <p style="margin: 0; font-size: 13px; color: #64748B;">Document library sync</p>
            </div>
            <span class="integration-status status-pending">
                ⏳ Pending Consent
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # Anthropic API status
        api_key_set = bool(st.secrets.get("ANTHROPIC_API_KEY", "")) if hasattr(st, 'secrets') else False
        st.markdown(f"""
        <div class="integration-card">
            <div class="integration-icon" style="background: #FEF3C7;">🤖</div>
            <div style="flex: 1;">
                <strong>Anthropic API</strong>
                <p style="margin: 0; font-size: 13px; color: #64748B;">AI assistant backend</p>
            </div>
            <span class="integration-status {'status-connected' if api_key_set else 'status-disconnected'}">
                {'✓ Configured' if api_key_set else '✗ Not Set'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.subheader("📊 Token Usage by Bot")
        
        if token_summary['by_bot']:
            bot_df = pd.DataFrame(token_summary['by_bot'])
            bot_df.columns = ['Bot', 'Tokens', 'Cost ($)', 'Requests']
            bot_df['Tokens'] = bot_df['Tokens'].apply(lambda x: f"{x:,}")
            bot_df['Cost ($)'] = bot_df['Cost ($)'].apply(lambda x: f"${x:.2f}")
            st.dataframe(bot_df, use_container_width=True, hide_index=True)
        else:
            st.info("No token usage data yet.")
    
    st.divider()
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    recent_logs = get_audit_logs(limit=10)
    
    if recent_logs:
        for log in recent_logs:
            severity_color = SEVERITY_COLORS.get(log.severity, "#6B7280")
            timestamp = datetime.fromisoformat(log.timestamp) if log.timestamp else datetime.utcnow()
            time_ago = datetime.utcnow() - timestamp
            
            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600}h ago"
            elif time_ago.seconds > 60:
                time_str = f"{time_ago.seconds // 60}m ago"
            else:
                time_str = "Just now"
            
            st.markdown(f"""
            <div class="audit-row" style="border-color: {severity_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="audit-action">{log.action.replace('_', ' ').title()}</span>
                    <span class="audit-time">{time_str}</span>
                </div>
                <div class="audit-details">
                    {log.user_email or 'System'} 
                    {f'• {log.resource_type}:{log.resource_id}' if log.resource_type else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity.")


# =============================================================================
# USER MANAGEMENT TAB
# =============================================================================

def render_user_management_tab() -> None:
    """Render the user management tab."""
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("➕ Create User", type="primary", use_container_width=True):
            st.session_state.show_create_user = True
            st.session_state.edit_user_id = None
    
    with col2:
        if st.button("📤 Bulk Import", use_container_width=True):
            st.session_state.show_bulk_import = True
    
    # Create user form
    if st.session_state.show_create_user:
        render_user_form()
        return
    
    # Bulk import form
    if st.session_state.show_bulk_import:
        render_bulk_import()
        return
    
    # Edit user form
    if st.session_state.edit_user_id:
        render_user_form(user_id=st.session_state.edit_user_id)
        return
    
    st.divider()
    
    # User list
    users = get_all_users(include_inactive=True)
    
    # Filter
    col1, col2 = st.columns([2, 4])
    with col1:
        filter_role = st.selectbox(
            "Filter by Role",
            options=["All"] + list(ROLES.keys()),
            format_func=lambda x: "All Roles" if x == "All" else ROLES.get(x, {}).get("name", x)
        )
    
    if filter_role != "All":
        users = [u for u in users if u.role == filter_role]
    
    # User table
    st.markdown(f"**{len(users)} users**")
    
    for user in users:
        role_info = ROLES.get(user.role, {"name": user.role, "color": "#6B7280", "icon": "👤"})
        
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
        
        with col1:
            status_icon = "✓" if user.is_active else "✗"
            st.markdown(f"**{user.display_name}** {status_icon}")
            st.caption(user.email)
        
        with col2:
            st.markdown(f"""
            <span class="role-badge" style="background: {role_info['color']}20; color: {role_info['color']};">
                {role_info['icon']} {role_info['name']}
            </span>
            """, unsafe_allow_html=True)
        
        with col3:
            st.caption(user.company or "—")
        
        with col4:
            if st.button("✏️", key=f"edit_{user.id}", help="Edit user"):
                st.session_state.edit_user_id = user.id
                st.rerun()
        
        with col5:
            if user.is_active:
                if st.button("🚫", key=f"disable_{user.id}", help="Disable user"):
                    delete_user(user.id, hard_delete=False)
                    st.rerun()
            else:
                if st.button("✓", key=f"enable_{user.id}", help="Re-enable user"):
                    update_user(user.id, is_active=True)
                    st.rerun()
        
        st.divider()


def render_user_form(user_id: Optional[int] = None) -> None:
    """Render create/edit user form."""
    
    user = get_user_by_id(user_id) if user_id else None
    is_edit = user is not None
    
    st.subheader("✏️ Edit User" if is_edit else "➕ Create User")
    
    with st.form("user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "Email *",
                value=user.email if user else "",
                disabled=is_edit,
                placeholder="user@company.com"
            )
            
            display_name = st.text_input(
                "Display Name *",
                value=user.display_name if user else "",
                placeholder="John Smith"
            )
            
            role = st.selectbox(
                "Role *",
                options=list(ROLES.keys()),
                index=list(ROLES.keys()).index(user.role) if user and user.role in ROLES else 0,
                format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x]['name']}"
            )
        
        with col2:
            company = st.text_input(
                "Company",
                value=user.company if user else "rockITdata",
                placeholder="rockITdata"
            )
            
            phone = st.text_input(
                "Phone",
                value=user.phone if user else "",
                placeholder="+1 555-123-4567"
            )
            
            expiration = st.date_input(
                "Account Expiration (optional)",
                value=datetime.fromisoformat(user.expiration_date).date() if user and user.expiration_date else None,
                help="For partner/temporary accounts"
            )
        
        if not is_edit:
            st.text_input(
                "Initial Password *",
                type="password",
                value="changeme123",
                help="User should change this on first login"
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button(
                "Save Changes" if is_edit else "Create User",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.edit_user_id = None
                st.session_state.show_create_user = False
                st.rerun()
        
        if submitted:
            if not email or not display_name:
                st.error("Email and Display Name are required.")
            else:
                exp_date = expiration.isoformat() if expiration else None
                
                if is_edit:
                    update_user(
                        user_id,
                        display_name=display_name,
                        role=role,
                        company=company,
                        phone=phone,
                        expiration_date=exp_date
                    )
                    st.success("User updated!")
                else:
                    new_id = create_user(
                        email=email,
                        display_name=display_name,
                        password="changeme123",
                        role=role,
                        company=company,
                        phone=phone,
                        expiration_date=exp_date
                    )
                    if new_id:
                        st.success(f"User created! ID: {new_id}")
                    else:
                        st.error("Failed to create user. Email may already exist.")
                
                st.session_state.edit_user_id = None
                st.session_state.show_create_user = False
                st.rerun()
    
    # Reset password section (edit only)
    if is_edit:
        st.divider()
        st.subheader("🔑 Reset Password")
        
        new_password = st.text_input("New Password", type="password", key="reset_pw")
        if st.button("Reset Password"):
            if new_password and len(new_password) >= 8:
                reset_password(user_id, new_password)
                st.success("Password reset successfully!")
            else:
                st.error("Password must be at least 8 characters.")


def render_bulk_import() -> None:
    """Render bulk user import interface."""
    
    st.subheader("📤 Bulk User Import")
    
    # Template download
    st.markdown("**Step 1: Download Template**")
    
    template_csv = "email,display_name,company,role,phone,deals,expiration_date\n"
    template_csv += "john.doe@partner.com,John Doe,Acme Corp,partner,+15551234567,VA-2025-001|DHA-2025-003,2025-06-30\n"
    template_csv += "jane.smith@rockitdata.com,Jane Smith,rockITdata,analyst,,,\n"
    
    st.download_button(
        "📥 Download CSV Template",
        data=template_csv,
        file_name="user_import_template.csv",
        mime="text/csv"
    )
    
    st.divider()
    
    # File upload
    st.markdown("**Step 2: Upload File**")
    
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: CSV, Excel (.xlsx, .xls)"
    )
    
    if uploaded_file:
        try:
            # Parse file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.markdown(f"**Preview ({len(df)} rows)**")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Validate
            required_cols = ['email', 'display_name']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("🚀 Import Users", type="primary"):
                        users_data = df.fillna("").to_dict('records')
                        results = bulk_import_users(users_data)
                        
                        st.success(f"✓ Created: {results['created']} users")
                        if results['skipped'] > 0:
                            st.warning(f"⚠ Skipped: {results['skipped']} rows")
                        if results['errors']:
                            with st.expander("View Errors"):
                                for err in results['errors']:
                                    st.text(err)
                
                with col2:
                    if st.button("Cancel"):
                        st.session_state.show_bulk_import = False
                        st.rerun()
                        
        except Exception as e:
            st.error(f"Error parsing file: {e}")
    
    else:
        if st.button("← Back"):
            st.session_state.show_bulk_import = False
            st.rerun()


# =============================================================================
# TOKEN USAGE TAB
# =============================================================================

def render_token_usage_tab() -> None:
    """Render the token usage / cost tracking tab."""
    
    st.subheader("💰 Token Cost Meter")
    
    # Period selector
    col1, col2 = st.columns([1, 3])
    with col1:
        period = st.selectbox("Time Period", [7, 30, 90], index=1, format_func=lambda x: f"Last {x} days")
    
    # Get data
    summary = get_token_usage_summary(days=period)
    monthly_budget = int(get_config("token_budget_monthly", "100000"))
    alert_threshold = int(get_config("token_alert_threshold", "80"))
    
    # Budget progress
    usage_pct = (summary['total_tokens'] / monthly_budget * 100) if monthly_budget > 0 else 0
    bar_color = "#059669" if usage_pct < alert_threshold else "#F59E0B" if usage_pct < 100 else "#EF4444"
    
    st.markdown(f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 600;">Monthly Budget Usage</span>
            <span style="color: #64748B;">{summary['total_tokens']:,} / {monthly_budget:,} tokens</span>
        </div>
        <div class="token-meter">
            <div class="token-meter-fill" style="width: {min(usage_pct, 100)}%; background: {bar_color};"></div>
            <span class="token-meter-label">{usage_pct:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tokens", f"{summary['total_tokens']:,}")
    
    with col2:
        st.metric("Total Cost", f"${summary['total_cost_usd']:.2f}")
    
    with col3:
        st.metric("API Requests", f"{summary['request_count']:,}")
    
    with col4:
        avg_cost = summary['total_cost_usd'] / summary['request_count'] if summary['request_count'] > 0 else 0
        st.metric("Avg Cost/Request", f"${avg_cost:.4f}")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Daily Usage Trend**")
        if summary['daily_breakdown']:
            daily_df = pd.DataFrame(summary['daily_breakdown'])
            daily_df['date'] = pd.to_datetime(daily_df['date'])
            st.line_chart(daily_df.set_index('date')['tokens'])
        else:
            st.info("No usage data for this period.")
    
    with col2:
        st.markdown("**Usage by Bot**")
        if summary['by_bot']:
            bot_df = pd.DataFrame(summary['by_bot'])
            st.bar_chart(bot_df.set_index('bot_id')['tokens'])
        else:
            st.info("No usage data for this period.")
    
    st.divider()
    
    # Monthly history
    st.markdown("**Monthly History**")
    monthly = get_monthly_token_usage()
    
    if monthly:
        monthly_df = pd.DataFrame(monthly)
        monthly_df.columns = ['Month', 'Tokens', 'Cost ($)', 'Requests']
        monthly_df['Tokens'] = monthly_df['Tokens'].apply(lambda x: f"{x:,}" if x else "0")
        monthly_df['Cost ($)'] = monthly_df['Cost ($)'].apply(lambda x: f"${x:.2f}" if x else "$0.00")
        st.dataframe(monthly_df, use_container_width=True, hide_index=True)
    else:
        st.info("No historical data available.")
    
    st.divider()
    
    # Budget settings
    st.markdown("**⚙️ Budget Settings**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_budget = st.number_input(
            "Monthly Token Budget",
            value=monthly_budget,
            min_value=10000,
            step=10000
        )
    
    with col2:
        new_threshold = st.number_input(
            "Alert Threshold (%)",
            value=alert_threshold,
            min_value=50,
            max_value=100,
            step=5
        )
    
    with col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Save Settings"):
            set_config("token_budget_monthly", str(new_budget))
            set_config("token_alert_threshold", str(new_threshold))
            st.success("Budget settings saved!")
            st.rerun()


# =============================================================================
# AUDIT LOG TAB
# =============================================================================

def render_audit_log_tab() -> None:
    """Render the audit log viewer tab."""
    
    st.subheader("📋 Audit Log")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action_filter = st.text_input("Filter by Action", placeholder="login, user_created...")
    
    with col2:
        severity_filter = st.selectbox(
            "Severity",
            options=["All", "info", "warning", "error", "critical"],
        )
    
    with col3:
        days_filter = st.selectbox("Time Range", [1, 7, 30, 90], index=1, format_func=lambda x: f"Last {x} days")
    
    # Get logs
    since = (datetime.utcnow() - timedelta(days=days_filter)).isoformat()
    
    logs = get_audit_logs(
        limit=50,
        offset=st.session_state.audit_page * 50,
        action=action_filter if action_filter else None,
        severity=severity_filter if severity_filter != "All" else None,
        since=since
    )
    
    total_count = get_audit_log_count(
        action=action_filter if action_filter else None,
        severity=severity_filter if severity_filter != "All" else None,
    )
    
    st.caption(f"Showing {len(logs)} of {total_count} entries")
    
    # Log entries
    for log in logs:
        severity_color = SEVERITY_COLORS.get(log.severity, "#6B7280")
        timestamp = datetime.fromisoformat(log.timestamp) if log.timestamp else datetime.utcnow()
        
        details = ""
        if log.details:
            try:
                details_dict = json.loads(log.details)
                details = " • ".join([f"{k}: {v}" for k, v in details_dict.items()][:3])
            except:
                details = log.details[:100]
        
        st.markdown(f"""
        <div class="audit-row" style="border-color: {severity_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="audit-action">{log.action.replace('_', ' ').title()}</span>
                <span class="audit-time">{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="audit-details">
                <strong>{log.user_email or 'System'}</strong>
                {f' • {log.resource_type}:{log.resource_id}' if log.resource_type else ''}
                {f' • {details}' if details else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Pagination
    if total_count > 50:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.audit_page > 0:
                if st.button("← Previous"):
                    st.session_state.audit_page -= 1
                    st.rerun()
        
        with col2:
            total_pages = (total_count // 50) + 1
            st.markdown(f"<div style='text-align: center;'>Page {st.session_state.audit_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
        
        with col3:
            if (st.session_state.audit_page + 1) * 50 < total_count:
                if st.button("Next →"):
                    st.session_state.audit_page += 1
                    st.rerun()
    
    # Export
    st.divider()
    
    if st.button("📥 Export Audit Log (CSV)"):
        all_logs = get_audit_logs(limit=10000, since=since)
        
        export_data = []
        for log in all_logs:
            export_data.append({
                "Timestamp": log.timestamp,
                "User": log.user_email,
                "Action": log.action,
                "Resource": f"{log.resource_type}:{log.resource_id}" if log.resource_type else "",
                "Severity": log.severity,
                "Details": log.details,
                "IP": log.ip_address,
            })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            "💾 Download CSV",
            data=csv,
            file_name=f"audit_log_{datetime.utcnow().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


# =============================================================================
# SYSTEM CONFIG TAB
# =============================================================================

def render_system_config_tab() -> None:
    """Render system configuration tab."""
    
    st.subheader("⚙️ System Configuration")
    
    # Get current config
    config = get_all_config()
    
    # Security settings
    st.markdown("**🔐 Security**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        session_timeout = st.number_input(
            "Session Timeout (hours)",
            value=int(config.get("session_timeout_hours", "24")),
            min_value=1,
            max_value=168
        )
    
    with col2:
        max_failed = st.number_input(
            "Max Failed Logins",
            value=int(config.get("max_failed_logins", "5")),
            min_value=3,
            max_value=10
        )
    
    st.divider()
    
    # Compliance settings
    st.markdown("**📋 Compliance**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        evidence_threshold = st.number_input(
            "Evidence Coverage Threshold (%)",
            value=int(config.get("evidence_coverage_threshold", "95")),
            min_value=80,
            max_value=100
        )
    
    with col2:
        audit_retention = st.number_input(
            "Audit Log Retention (days)",
            value=int(config.get("audit_retention_days", "90")),
            min_value=30,
            max_value=365
        )
    
    st.divider()
    
    # Feature flags
    st.markdown("**🚩 Feature Flags**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        enable_partners = st.checkbox(
            "Partner Portal",
            value=config.get("feature_partners", "true") == "true"
        )
    
    with col2:
        enable_playbook = st.checkbox(
            "Playbook Learning",
            value=config.get("feature_playbook", "true") == "true"
        )
    
    with col3:
        enable_aurora = st.checkbox(
            "Aurora Celebrations",
            value=config.get("feature_aurora", "true") == "true"
        )
    
    st.divider()
    
    # Save button
    if st.button("💾 Save Configuration", type="primary"):
        set_config("session_timeout_hours", str(session_timeout))
        set_config("max_failed_logins", str(max_failed))
        set_config("evidence_coverage_threshold", str(evidence_threshold))
        set_config("audit_retention_days", str(audit_retention))
        set_config("feature_partners", "true" if enable_partners else "false")
        set_config("feature_playbook", "true" if enable_playbook else "false")
        set_config("feature_aurora", "true" if enable_aurora else "false")
        
        log_audit(
            action="config_updated",
            details={"settings": "multiple"},
            severity="info"
        )
        
        st.success("Configuration saved!")
    
    st.divider()
    
    # Database info
    st.markdown("**🗄️ Database**")
    
    users = get_all_users(include_inactive=True)
    log_count = get_audit_log_count()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        st.metric("Audit Entries", f"{log_count:,}")
    
    with col3:
        st.metric("Database", "SQLite (Local)")


# =============================================================================
# MAIN DASHBOARD RENDERER
# =============================================================================

def render_admin_dashboard() -> None:
    """
    Render the complete admin dashboard.
    Call this from your main app.py.
    """
    # Check database availability
    if not DATABASE_AVAILABLE:
        st.error("⚠️ Database module not available. Ensure `database.py` is in your project.")
        return
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return
    
    # Initialize state
    init_admin_state()
    
    # Inject styles
    st.markdown(ADMIN_STYLES, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="admin-header">
        <span style="font-size: 32px;">⚙️</span>
        <div>
            <h1 class="admin-title">Admin Dashboard</h1>
            <p class="admin-subtitle">AMANDA™ Portal Administration</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab navigation
    tabs = st.tabs([
        "📊 Overview",
        "👥 Users",
        "💰 Token Usage",
        "📋 Audit Log",
        "⚙️ Settings"
    ])
    
    with tabs[0]:
        render_overview_tab()
    
    with tabs[1]:
        render_user_management_tab()
    
    with tabs[2]:
        render_token_usage_tab()
    
    with tabs[3]:
        render_audit_log_tab()
    
    with tabs[4]:
        render_system_config_tab()


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Admin Dashboard | AMANDA",
        page_icon="⚙️",
        layout="wide",
    )
    
    render_admin_dashboard()
