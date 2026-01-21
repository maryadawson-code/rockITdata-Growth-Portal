"""
AMANDA Portal Database Module
==============================
SQLite persistence for users, sessions, audit logs, and token tracking.

Author: rockITdata LLC
Version: 7.3
"""

import sqlite3
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file location
DB_PATH = os.getenv("AMANDA_DB_PATH", "amanda_portal.db")


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class User:
    """User account."""
    id: Optional[int] = None
    email: str = ""
    display_name: str = ""
    password_hash: str = ""
    salt: str = ""
    role: str = "standard"
    company: str = "rockITdata"
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    permissions: Optional[str] = None  # JSON string of permission overrides
    deal_assignments: Optional[str] = None  # JSON array of deal IDs
    expiration_date: Optional[str] = None  # For partner accounts


@dataclass
class Session:
    """User session."""
    id: Optional[int] = None
    user_id: int = 0
    token: str = ""
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class AuditLog:
    """Audit trail entry."""
    id: Optional[int] = None
    timestamp: Optional[str] = None
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str = ""
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None  # JSON
    ip_address: Optional[str] = None
    severity: str = "info"  # info, warning, error, critical


@dataclass
class TokenUsage:
    """API token usage record."""
    id: Optional[int] = None
    timestamp: Optional[str] = None
    user_id: Optional[int] = None
    bot_id: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    model: str = "claude-sonnet-4-20250514"
    proposal_id: Optional[str] = None


@dataclass 
class SystemConfig:
    """System configuration setting."""
    key: str = ""
    value: str = ""
    description: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[int] = None


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

@contextmanager
def get_db_connection():
    """Get database connection with context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite3.Row to dictionary."""
    return dict(zip(row.keys(), row))


# =============================================================================
# SCHEMA INITIALIZATION
# =============================================================================

def init_database() -> None:
    """Initialize database schema."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'standard',
                company TEXT DEFAULT 'rockITdata',
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                permissions TEXT,
                deal_assignments TEXT,
                expiration_date TEXT
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                user_email TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                severity TEXT DEFAULT 'info',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Token usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                bot_id TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                model TEXT,
                proposal_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # System config table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (updated_by) REFERENCES users(id)
            )
        """)
        
        # Playbook entries table (for admin curation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playbook_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                quality_score REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                is_approved INTEGER DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp ON token_usage(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_usage_user ON token_usage(user_id)")
        
        conn.commit()
        logger.info("Database schema initialized")


def seed_demo_data() -> None:
    """Seed database with demo users and data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            logger.info("Database already seeded")
            return
        
        # Demo users
        demo_users = [
            ("admin@rockitdata.com", "Admin User", "admin", "rockITdata"),
            ("mary.womack@rockitdata.com", "Mary Womack", "capture_lead", "rockITdata"),
            ("john.smith@rockitdata.com", "John Smith", "proposal_manager", "rockITdata"),
            ("sarah.jones@rockitdata.com", "Sarah Jones", "analyst", "rockITdata"),
            ("partner@acmecorp.com", "Partner User", "partner", "Acme Corp"),
        ]
        
        for email, name, role, company in demo_users:
            create_user(email, name, "demo123", role, company)
        
        # Default system config
        default_config = [
            ("token_budget_monthly", "100000", "Monthly token budget limit"),
            ("token_alert_threshold", "80", "Alert when usage exceeds this percentage"),
            ("session_timeout_hours", "24", "Session timeout in hours"),
            ("max_failed_logins", "5", "Max failed login attempts before lockout"),
            ("audit_retention_days", "90", "Days to retain audit logs"),
            ("evidence_coverage_threshold", "95", "Required evidence coverage percentage"),
        ]
        
        for key, value, description in default_config:
            set_config(key, value, description)
        
        conn.commit()
        logger.info("Demo data seeded")


# =============================================================================
# PASSWORD UTILITIES
# =============================================================================

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash a password with SHA-256 and salt.
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
        
    Returns:
        Tuple of (password_hash, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    salted = f"{salt}{password}".encode('utf-8')
    password_hash = hashlib.sha256(salted).hexdigest()
    
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify a password against stored hash."""
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


# =============================================================================
# USER OPERATIONS
# =============================================================================

def create_user(
    email: str,
    display_name: str,
    password: str,
    role: str = "standard",
    company: str = "rockITdata",
    phone: Optional[str] = None,
    permissions: Optional[Dict] = None,
    deal_assignments: Optional[List[str]] = None,
    expiration_date: Optional[str] = None,
) -> Optional[int]:
    """
    Create a new user.
    
    Returns:
        User ID or None if failed
    """
    password_hash, salt = hash_password(password)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (
                    email, display_name, password_hash, salt, role, company,
                    phone, permissions, deal_assignments, expiration_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email.lower(),
                display_name,
                password_hash,
                salt,
                role,
                company,
                phone,
                json.dumps(permissions) if permissions else None,
                json.dumps(deal_assignments) if deal_assignments else None,
                expiration_date,
            ))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            # Audit log
            log_audit(
                action="user_created",
                resource_type="user",
                resource_id=str(user_id),
                details={"email": email, "role": role},
                severity="info"
            )
            
            return user_id
            
        except sqlite3.IntegrityError:
            logger.error(f"User with email {email} already exists")
            return None


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email address."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
        
        if row:
            return User(**dict_from_row(row))
        return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return User(**dict_from_row(row))
        return None


def get_all_users(include_inactive: bool = False) -> List[User]:
    """Get all users."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if include_inactive:
            cursor.execute("SELECT * FROM users ORDER BY display_name")
        else:
            cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY display_name")
        
        return [User(**dict_from_row(row)) for row in cursor.fetchall()]


def update_user(
    user_id: int,
    display_name: Optional[str] = None,
    role: Optional[str] = None,
    company: Optional[str] = None,
    phone: Optional[str] = None,
    is_active: Optional[bool] = None,
    permissions: Optional[Dict] = None,
    deal_assignments: Optional[List[str]] = None,
    expiration_date: Optional[str] = None,
) -> bool:
    """Update user fields."""
    updates = []
    values = []
    
    if display_name is not None:
        updates.append("display_name = ?")
        values.append(display_name)
    if role is not None:
        updates.append("role = ?")
        values.append(role)
    if company is not None:
        updates.append("company = ?")
        values.append(company)
    if phone is not None:
        updates.append("phone = ?")
        values.append(phone)
    if is_active is not None:
        updates.append("is_active = ?")
        values.append(1 if is_active else 0)
    if permissions is not None:
        updates.append("permissions = ?")
        values.append(json.dumps(permissions))
    if deal_assignments is not None:
        updates.append("deal_assignments = ?")
        values.append(json.dumps(deal_assignments))
    if expiration_date is not None:
        updates.append("expiration_date = ?")
        values.append(expiration_date)
    
    if not updates:
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(user_id)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            values
        )
        conn.commit()
        
        log_audit(
            action="user_updated",
            resource_type="user",
            resource_id=str(user_id),
            details={"updates": updates},
            severity="info"
        )
        
        return cursor.rowcount > 0


def delete_user(user_id: int, hard_delete: bool = False) -> bool:
    """Delete or deactivate a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if hard_delete:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            action = "user_deleted"
        else:
            cursor.execute(
                "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            action = "user_deactivated"
        
        conn.commit()
        
        log_audit(
            action=action,
            resource_type="user",
            resource_id=str(user_id),
            severity="warning"
        )
        
        return cursor.rowcount > 0


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user and return user object if valid."""
    user = get_user_by_email(email)
    
    if not user:
        log_audit(
            action="login_failed",
            details={"email": email, "reason": "user_not_found"},
            severity="warning"
        )
        return None
    
    if not user.is_active:
        log_audit(
            action="login_failed",
            user_id=user.id,
            user_email=email,
            details={"reason": "account_inactive"},
            severity="warning"
        )
        return None
    
    # Check expiration
    if user.expiration_date:
        if datetime.fromisoformat(user.expiration_date) < datetime.utcnow():
            log_audit(
                action="login_failed",
                user_id=user.id,
                user_email=email,
                details={"reason": "account_expired"},
                severity="warning"
            )
            return None
    
    if not verify_password(password, user.password_hash, user.salt):
        log_audit(
            action="login_failed",
            user_id=user.id,
            user_email=email,
            details={"reason": "invalid_password"},
            severity="warning"
        )
        return None
    
    # Update last login
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user.id,)
        )
        conn.commit()
    
    log_audit(
        action="login_success",
        user_id=user.id,
        user_email=email,
        severity="info"
    )
    
    return user


def reset_password(user_id: int, new_password: str) -> bool:
    """Reset user password."""
    password_hash, salt = hash_password(new_password)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (password_hash, salt, user_id)
        )
        conn.commit()
        
        log_audit(
            action="password_reset",
            resource_type="user",
            resource_id=str(user_id),
            severity="info"
        )
        
        return cursor.rowcount > 0


# =============================================================================
# AUDIT LOG OPERATIONS
# =============================================================================

def log_audit(
    action: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    severity: str = "info",
) -> None:
    """Log an audit entry."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (
                user_id, user_email, action, resource_type, resource_id,
                details, ip_address, severity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_email,
            action,
            resource_type,
            resource_id,
            json.dumps(details) if details else None,
            ip_address,
            severity,
        ))
        conn.commit()


def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    severity: Optional[str] = None,
    since: Optional[str] = None,
) -> List[AuditLog]:
    """Get audit logs with optional filters."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if action:
            query += " AND action LIKE ?"
            params.append(f"%{action}%")
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [AuditLog(**dict_from_row(row)) for row in cursor.fetchall()]


def get_audit_log_count(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    severity: Optional[str] = None,
) -> int:
    """Get total count of audit logs matching filters."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if action:
            query += " AND action LIKE ?"
            params.append(f"%{action}%")
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]


# =============================================================================
# TOKEN USAGE OPERATIONS
# =============================================================================

def log_token_usage(
    user_id: Optional[int],
    bot_id: str,
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-sonnet-4-20250514",
    proposal_id: Optional[str] = None,
) -> None:
    """Log API token usage."""
    # Claude Sonnet pricing (as of 2024): $3/1M input, $15/1M output
    input_cost = (input_tokens / 1_000_000) * 3.0
    output_cost = (output_tokens / 1_000_000) * 15.0
    total_cost = input_cost + output_cost
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO token_usage (
                user_id, bot_id, input_tokens, output_tokens, total_tokens,
                cost_usd, model, proposal_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            bot_id,
            input_tokens,
            output_tokens,
            input_tokens + output_tokens,
            total_cost,
            model,
            proposal_id,
        ))
        conn.commit()


def get_token_usage_summary(
    days: int = 30,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get token usage summary for the specified period."""
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build query
        base_query = """
            SELECT 
                SUM(input_tokens) as total_input,
                SUM(output_tokens) as total_output,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as total_cost,
                COUNT(*) as request_count
            FROM token_usage
            WHERE timestamp >= ?
        """
        params = [since]
        
        if user_id:
            base_query += " AND user_id = ?"
            params.append(user_id)
        
        cursor.execute(base_query, params)
        row = cursor.fetchone()
        
        # Get daily breakdown
        daily_query = """
            SELECT 
                DATE(timestamp) as date,
                SUM(total_tokens) as tokens,
                SUM(cost_usd) as cost
            FROM token_usage
            WHERE timestamp >= ?
        """
        daily_params = [since]
        
        if user_id:
            daily_query += " AND user_id = ?"
            daily_params.append(user_id)
        
        daily_query += " GROUP BY DATE(timestamp) ORDER BY date"
        
        cursor.execute(daily_query, daily_params)
        daily_data = [dict_from_row(r) for r in cursor.fetchall()]
        
        # Get by bot breakdown
        bot_query = """
            SELECT 
                bot_id,
                SUM(total_tokens) as tokens,
                SUM(cost_usd) as cost,
                COUNT(*) as requests
            FROM token_usage
            WHERE timestamp >= ?
        """
        bot_params = [since]
        
        if user_id:
            bot_query += " AND user_id = ?"
            bot_params.append(user_id)
        
        bot_query += " GROUP BY bot_id ORDER BY tokens DESC"
        
        cursor.execute(bot_query, bot_params)
        by_bot = [dict_from_row(r) for r in cursor.fetchall()]
        
        return {
            "total_input_tokens": row["total_input"] or 0,
            "total_output_tokens": row["total_output"] or 0,
            "total_tokens": row["total_tokens"] or 0,
            "total_cost_usd": row["total_cost"] or 0.0,
            "request_count": row["request_count"] or 0,
            "daily_breakdown": daily_data,
            "by_bot": by_bot,
            "period_days": days,
        }


def get_monthly_token_usage() -> List[Dict[str, Any]]:
    """Get token usage grouped by month."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', timestamp) as month,
                SUM(total_tokens) as tokens,
                SUM(cost_usd) as cost,
                COUNT(*) as requests
            FROM token_usage
            GROUP BY strftime('%Y-%m', timestamp)
            ORDER BY month DESC
            LIMIT 12
        """)
        return [dict_from_row(r) for r in cursor.fetchall()]


# =============================================================================
# SYSTEM CONFIG OPERATIONS
# =============================================================================

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def set_config(
    key: str,
    value: str,
    description: Optional[str] = None,
    updated_by: Optional[int] = None,
) -> None:
    """Set a configuration value."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_config (key, value, description, updated_by)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET 
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = excluded.updated_by
        """, (key, value, description, updated_by))
        conn.commit()


def get_all_config() -> Dict[str, str]:
    """Get all configuration values as a dictionary."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM system_config")
        return {row["key"]: row["value"] for row in cursor.fetchall()}


# =============================================================================
# BULK IMPORT
# =============================================================================

def bulk_import_users(users_data: List[Dict]) -> Dict[str, Any]:
    """
    Bulk import users from a list of dictionaries.
    
    Expected fields: email, display_name, role, company, phone, deals, expiration_date
    
    Returns:
        Summary of import results
    """
    results = {
        "total": len(users_data),
        "created": 0,
        "skipped": 0,
        "errors": [],
    }
    
    for i, user_data in enumerate(users_data):
        try:
            email = user_data.get("email", "").strip()
            if not email:
                results["errors"].append(f"Row {i+1}: Missing email")
                results["skipped"] += 1
                continue
            
            # Check if user exists
            existing = get_user_by_email(email)
            if existing:
                results["errors"].append(f"Row {i+1}: User {email} already exists")
                results["skipped"] += 1
                continue
            
            # Parse deal assignments
            deals = user_data.get("deals", "")
            deal_list = [d.strip() for d in deals.split("|") if d.strip()] if deals else None
            
            # Create user with default password
            user_id = create_user(
                email=email,
                display_name=user_data.get("display_name", email.split("@")[0]),
                password="changeme123",  # Default password
                role=user_data.get("role", "standard"),
                company=user_data.get("company", "rockITdata"),
                phone=user_data.get("phone"),
                deal_assignments=deal_list,
                expiration_date=user_data.get("expiration_date"),
            )
            
            if user_id:
                results["created"] += 1
            else:
                results["errors"].append(f"Row {i+1}: Failed to create user {email}")
                results["skipped"] += 1
                
        except Exception as e:
            results["errors"].append(f"Row {i+1}: {str(e)}")
            results["skipped"] += 1
    
    # Log bulk import
    log_audit(
        action="bulk_user_import",
        details=results,
        severity="info"
    )
    
    return results


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize() -> None:
    """Initialize database and seed demo data."""
    init_database()
    seed_demo_data()


# Run initialization when module is imported
if __name__ == "__main__":
    initialize()
    print(f"Database initialized at: {DB_PATH}")
