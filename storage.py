"""
Data storage layer for ICICI Agent Gatekeeper.
Handles JSON and CSV persistence for registered AI Agents and Audit Logs.
Guarantees permanent data persistence across application restarts.
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import STATUS_ACTIVE, STATUS_REVOKED, DECISION_ALLOW, DECISION_BLOCK

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
AGENTS_FILE = os.path.join(DATA_DIR, "agents.json")
AUDIT_LOG_CSV = os.path.join(DATA_DIR, "audit_log.csv")
AUDIT_LOG_JSON = os.path.join(DATA_DIR, "audit_log.json")

CSV_HEADERS = [
    "request_id", "timestamp", "customer_name", "agent_name",
    "action", "amount", "decision", "rule_number", "explanation"
]

def ensure_data_directory():
    """Ensure the data directory exists and initialize files with sample data if empty."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(AGENTS_FILE):
        _initialize_sample_agents()
    if not os.path.exists(AUDIT_LOG_CSV):
        _initialize_sample_audit_log()

def _initialize_sample_agents():
    """Seed initial sample agents with explicit permissions for demonstration."""
    sample_agents = [
        {
            "agent_id": "AGT-1001",
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "registration_date": "2026-11-10 10:30:00",
            "status": STATUS_ACTIVE,
            "permissions": {
                "view_balance": True,
                "pay_bills": True,
                "transfer_money": True
            },
            "revoked_at": None,
            "revocation_reason": None
        },
        {
            "agent_id": "AGT-1002",
            "customer_name": "Priya Nair",
            "agent_name": "Priya SmartFin Bot",
            "registration_date": "2026-11-12 14:15:00",
            "status": STATUS_ACTIVE,
            "permissions": {
                "view_balance": True,
                "pay_bills": True,
                "transfer_money": True
            },
            "revoked_at": None,
            "revocation_reason": None
        },
        {
            "agent_id": "AGT-1003",
            "customer_name": "Amitabh Patel",
            "agent_name": "Amitabh ReadOnly Agent",
            "registration_date": "2026-11-14 09:45:00",
            "status": STATUS_ACTIVE,
            "permissions": {
                "view_balance": True,
                "pay_bills": False,
                "transfer_money": False
            },
            "revoked_at": None,
            "revocation_reason": None
        },
        {
            "agent_id": "AGT-1004",
            "customer_name": "Sneha Roy",
            "agent_name": "Sneha Expense Manager",
            "registration_date": "2026-11-05 16:20:00",
            "status": STATUS_REVOKED,
            "permissions": {
                "view_balance": True,
                "pay_bills": True,
                "transfer_money": True
            },
            "revoked_at": "2026-11-15 11:00:00",
            "revocation_reason": "Revoked by bank administrator due to suspicious activity"
        }
    ]
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(sample_agents, f, indent=4)

def _initialize_sample_audit_log():
    """Seed sample audit log entries conforming to R1-R8 and all required audit fields."""
    sample_logs = [
        {
            "request_id": "REQ-8001",
            "timestamp": "2026-11-16 11:20:05",
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "action": "View Balance",
            "amount": 0.0,
            "decision": "ALLOW",
            "rule_number": "R4",
            "explanation": "Registered and active AI agents can view balance without additional customer confirmation."
        },
        {
            "request_id": "REQ-8002",
            "timestamp": "2026-11-16 13:45:12",
            "customer_name": "Priya Nair",
            "agent_name": "Priya SmartFin Bot",
            "action": "Pay Bill",
            "amount": 3200.0,
            "decision": "ALLOW",
            "rule_number": "R5",
            "explanation": "Registered and active agent with customer-granted bill-payment permission authorized for bill payment of ₹3,200.00 (<= ₹5,000)."
        },
        {
            "request_id": "REQ-8003",
            "timestamp": "2026-11-16 15:10:33",
            "customer_name": "Priya Nair",
            "agent_name": "Priya SmartFin Bot",
            "action": "Transfer Money",
            "amount": 2500.0,
            "decision": "ASK CUSTOMER",
            "rule_number": "R7",
            "explanation": "Every transfer money request must return ASK CUSTOMER regardless of amount."
        },
        {
            "request_id": "REQ-8004",
            "timestamp": "2026-11-17 09:05:40",
            "customer_name": "Sneha Roy",
            "agent_name": "Sneha Expense Manager",
            "action": "View Balance",
            "amount": 0.0,
            "decision": "BLOCK",
            "rule_number": "R1",
            "explanation": "Agent 'Sneha Expense Manager' has been permanently revoked. All requests are strictly BLOCKED."
        }
    ]

    with open(AUDIT_LOG_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(sample_logs)

    with open(AUDIT_LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(sample_logs, f, indent=4)

def load_agents() -> List[Dict[str, Any]]:
    """Load all registered agents from JSON."""
    ensure_data_directory()
    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading agents: {e}")
        return []

def save_agent(
    customer_name: str,
    agent_name: str,
    can_view_balance: bool = True,
    can_pay_bills: bool = True,
    can_transfer_money: bool = True
) -> Dict[str, Any]:
    """
    Register a new AI agent with explicit customer-granted permissions, save permanently,
    and automatically record the Agent Registration event in the security audit log.
    """
    ensure_data_directory()
    agents = load_agents()
    
    next_num = 1001 + len(agents)
    agent_id = f"AGT-{next_num}"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_agent = {
        "agent_id": agent_id,
        "customer_name": customer_name.strip(),
        "agent_name": agent_name.strip(),
        "registration_date": current_time,
        "status": STATUS_ACTIVE,
        "permissions": {
            "view_balance": can_view_balance,
            "pay_bills": can_pay_bills,
            "transfer_money": can_transfer_money
        },
        "revoked_at": None,
        "revocation_reason": None
    }
    
    agents.append(new_agent)
    
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=4)

    # Record Agent Registration event in permanent Audit Log
    log_request(
        customer_name=customer_name.strip(),
        agent_name=agent_name.strip(),
        action="Agent Registration",
        amount=0.0,
        decision=DECISION_ALLOW,
        rule_number="REG",
        explanation=(
            f"New AI agent '{agent_name.strip()}' enrolled with ID {agent_id}. "
            f"Permissions: View Balance={'Yes' if can_view_balance else 'No'}, "
            f"Pay Bills={'Yes' if can_pay_bills else 'No'}, "
            f"Transfer Money={'Yes' if can_transfer_money else 'No'}."
        )
    )
        
    return new_agent

def revoke_agent(agent_id: str, reason: str = "Revoked by Administrator") -> bool:
    """
    Permanently revoke an agent by updating status to REVOKED, recording timestamp,
    and recording the revocation event with revocation timestamp in the audit log (Rule R1).
    """
    ensure_data_directory()
    agents = load_agents()
    updated = False
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    revoked_agent_record = None

    for agent in agents:
        if agent["agent_id"] == agent_id:
            agent["status"] = STATUS_REVOKED
            agent["revoked_at"] = current_time
            agent["revocation_reason"] = reason
            updated = True
            revoked_agent_record = agent
            break

    if updated:
        with open(AGENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(agents, f, indent=4)

        # Record Agent Revocation event with exact timestamp in the permanent audit log
        if revoked_agent_record:
            log_request(
                customer_name=revoked_agent_record.get("customer_name", "Unknown"),
                agent_name=revoked_agent_record.get("agent_name", "Unknown"),
                action="Agent Revocation",
                amount=0.0,
                decision=DECISION_BLOCK,
                rule_number="R1",
                explanation=(
                    f"Administrator revoked agent '{revoked_agent_record.get('agent_name')}' ({agent_id}). "
                    f"Revocation Timestamp: {current_time}. Reason: {reason}."
                )
            )

    return updated

def get_agent_by_id(agent_id: str) -> Optional[Dict[str, Any]]:
    """Find an agent record by agent ID."""
    ensure_data_directory()
    agents = load_agents()
    for agent in agents:
        if agent.get("agent_id", "").strip().upper() == agent_id.strip().upper():
            return agent
    return None

def get_agent_by_name(agent_name: str) -> Optional[Dict[str, Any]]:
    """Find an agent record by agent name (returns most recent matching entry)."""
    agents = load_agents()
    for agent in reversed(agents):
        if agent["agent_name"].strip().lower() == agent_name.strip().lower():
            return agent
    return None

def load_audit_log() -> List[Dict[str, Any]]:
    """
    Load all audit log records from permanent CSV storage.
    Normalizes field names to guarantee availability of date/time, customer, agent,
    action, amount, decision, rule number, and explanation.
    """
    ensure_data_directory()
    logs = []
    if not os.path.exists(AUDIT_LOG_CSV):
        return logs

    try:
        with open(AUDIT_LOG_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize amount
                try:
                    row["amount"] = float(row.get("amount", 0.0))
                except (ValueError, TypeError):
                    row["amount"] = 0.0

                # Normalize explanation & reason
                expl = row.get("explanation") or row.get("reason") or ""
                row["explanation"] = expl
                row["reason"] = expl

                logs.append(row)

        # Return with newest events first
        logs.reverse()
        return logs
    except Exception as e:
        print(f"Error loading audit log: {e}")
        return []

def log_request(
    customer_name: str,
    agent_name: str,
    action: str,
    amount: float,
    decision: str,
    rule_number: str,
    explanation: Optional[str] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    R8: Save every request and event permanently in CSV and JSON audit storage.
    Records: Date and time, Customer name, Agent name, Requested action,
             Transaction amount, Decision, Rule number, Explanation.
    """
    ensure_data_directory()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    import random
    req_num = random.randint(1000, 9999)
    request_id = f"REQ-{req_num}"

    expl_text = (explanation or reason or "").strip()

    new_log = {
        "request_id": request_id,
        "timestamp": current_time,
        "customer_name": customer_name.strip(),
        "agent_name": agent_name.strip(),
        "action": action,
        "amount": round(float(amount), 2),
        "decision": decision,
        "rule_number": rule_number,
        "explanation": expl_text
    }

    # Append to CSV
    file_exists = os.path.exists(AUDIT_LOG_CSV)
    with open(AUDIT_LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, extrasaction="ignore")
        if not file_exists or os.path.getsize(AUDIT_LOG_CSV) == 0:
            writer.writeheader()
        writer.writerow(new_log)

    # Mirror to JSON for dual storage resilience
    json_logs = []
    if os.path.exists(AUDIT_LOG_JSON):
        try:
            with open(AUDIT_LOG_JSON, "r", encoding="utf-8") as f:
                json_logs = json.load(f)
        except Exception:
            json_logs = []
            
    json_logs.append(new_log)
    with open(AUDIT_LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(json_logs, f, indent=4)

    return new_log

def get_dashboard_metrics() -> Dict[str, int]:
    """Calculate key performance indicators (KPIs) for the executive dashboard."""
    agents = load_agents()
    audit_logs = load_audit_log()

    total_agents = len(agents)
    active_agents = sum(1 for a in agents if a.get("status") == STATUS_ACTIVE)
    revoked_agents = sum(1 for a in agents if a.get("status") == STATUS_REVOKED)

    total_requests = len(audit_logs)
    allowed_requests = sum(1 for r in audit_logs if r.get("decision") in ["ALLOW", "REGISTERED"])
    pending_requests = sum(1 for r in audit_logs if r.get("decision") == "ASK CUSTOMER")
    blocked_requests = sum(1 for r in audit_logs if r.get("decision") in ["BLOCK", "REVOKED"])

    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "revoked_agents": revoked_agents,
        "total_requests": total_requests,
        "allowed_requests": allowed_requests,
        "pending_requests": pending_requests,
        "blocked_requests": blocked_requests
    }
