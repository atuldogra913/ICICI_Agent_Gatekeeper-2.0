"""
Decision Engine for ICICI Bank Agent Gatekeeper.
Implements the 8 Business Rules (R1 - R8) for AI Agent Permission and Risk Management.

Evaluation Hierarchy & Constraints:
1. R1: Revocation must be checked before every other rule.
2. R2: Unregistered agents and customer-agent ownership mismatches must be blocked.
3. R3: Invalid actions and negative/zero transaction amounts must be blocked.
4. R4: Registered and active agents can View Balance (ALLOW).
5. R5: Registered & active agents with bill-payment permission can Pay Bills up to ₹5,000 (ALLOW).
       If bill-payment permission is not granted by customer, request is BLOCKED.
6. R6: Bill payments above ₹5,000 return ASK CUSTOMER.
7. R7: Every Transfer Money request returns ASK CUSTOMER, regardless of amount.
8. R8: Every evaluated request is permanently logged with complete audit attributes.
"""

from typing import Dict, Any, Optional
from config import (
    DECISION_ALLOW,
    DECISION_ASK_CUSTOMER,
    DECISION_BLOCK,
    ACTION_VIEW_BALANCE,
    ACTION_PAY_BILL,
    ACTION_TRANSFER_MONEY,
    ACTIONS,
    STATUS_REVOKED
)

class EvaluationResult:
    """Encapsulates the decision, rule number, rule name, and plain-language explanation."""
    def __init__(self, decision: str, rule_number: str, reason: str, rule_name: str = ""):
        self.decision = decision
        self.rule_number = rule_number
        self.rule_code = rule_number
        self.reason = reason
        self.explanation = reason
        self.rule_name = rule_name or f"Policy Rule {rule_number}"

    def to_dict(self) -> Dict[str, str]:
        return {
            "decision": self.decision,
            "rule_number": self.rule_number,
            "rule_code": self.rule_code,
            "rule_name": self.rule_name,
            "reason": self.reason,
            "explanation": self.explanation
        }

def evaluate_request(
    customer_name: str,
    agent_name: str,
    action: str,
    amount: float,
    agent_record: Optional[Dict[str, Any]] = None
) -> EvaluationResult:
    """
    Evaluates an AI agent's transaction request against ICICI Bank's 8 Business Rules.
    The first applicable rule determines the outcome.
    """

    # Clean inputs
    cust_clean = (customer_name or "").strip()
    agent_clean = (agent_name or "").strip()

    # Automatic storage resolution if agent_record is not explicitly provided
    if agent_record is None and agent_clean:
        try:
            import storage
            agent_record = storage.get_agent_by_name(agent_clean)
        except Exception:
            pass

    # =========================================================================
    # R1: REVOCATION CHECK (Must be checked before every other rule)
    # If an AI agent has been revoked, all its requests must be BLOCKED.
    # =========================================================================
    if agent_record is not None and agent_record.get("status") == STATUS_REVOKED:
        revoked_time = agent_record.get("revoked_at", "Earlier Date")
        revocation_reason = agent_record.get("revocation_reason", "Administrative Action")
        return EvaluationResult(
            decision=DECISION_BLOCK,
            rule_number="R1",
            rule_name="Agent Revocation Access Control",
            reason=(
                f"Agent '{agent_clean}' has been permanently REVOKED on {revoked_time} "
                f"({revocation_reason}). All requests from revoked agents must be BLOCKED."
            )
        )

    # =========================================================================
    # R2: AGENT REGISTRATION & OWNERSHIP CHECK
    # If an AI agent is not registered with the bank, its request must be BLOCKED.
    # The system must also verify customer-agent ownership.
    # =========================================================================
    if agent_record is None:
        return EvaluationResult(
            decision=DECISION_BLOCK,
            rule_number="R2",
            rule_name="Unregistered Agent Access Firewall",
            reason=f"AI agent '{agent_clean}' is not registered with ICICI Bank. Request must be BLOCKED."
        )

    # Verify Customer-Agent Ownership
    registered_customer = agent_record.get("customer_name", "").strip().lower()
    if cust_clean.lower() != registered_customer:
        return EvaluationResult(
            decision=DECISION_BLOCK,
            rule_number="R2",
            rule_name="Customer Ownership Identity Binding",
            reason=(
                f"Customer ownership mismatch: Agent '{agent_clean}' belongs to '{agent_record.get('customer_name')}', "
                f"not '{cust_clean}'. Unauthorized cross-customer access is BLOCKED."
            )
        )

    # Safe extraction of permissions dictionary
    permissions = agent_record.get("permissions") or {}

    # =========================================================================
    # R3: INVALID ACTIONS & NEGATIVE AMOUNTS CHECK
    # Invalid actions and negative transaction amounts must be BLOCKED.
    # =========================================================================
    # 1. Action Validation
    if action not in ACTIONS:
        return EvaluationResult(
            decision=DECISION_BLOCK,
            rule_number="R3",
            rule_name="Action Type & Payload Validation",
            reason=(
                f"Invalid action '{action}'. Permitted actions are: "
                f"{', '.join(ACTIONS)}. Request must be BLOCKED."
            )
        )

    # 2. Transaction Amount Validation for monetary actions
    if action in [ACTION_PAY_BILL, ACTION_TRANSFER_MONEY]:
        try:
            numeric_amount = float(amount)
        except (ValueError, TypeError):
            return EvaluationResult(
                decision=DECISION_BLOCK,
                rule_number="R3",
                rule_name="Monetary Value Integrity Check",
                reason=f"Invalid transaction amount '{amount}'. Non-numeric values must be BLOCKED."
            )

        if numeric_amount <= 0:
            return EvaluationResult(
                decision=DECISION_BLOCK,
                rule_number="R3",
                rule_name="Non-Positive Amount Prohibition",
                reason=(
                    f"Invalid or negative transaction amount of ₹{numeric_amount:,.2f}. "
                    "Transaction amount must be strictly greater than ₹0.00. Request must be BLOCKED."
                )
            )
    else:
        # View Balance does not require amount
        numeric_amount = 0.0

    # =========================================================================
    # R4: VIEW BALANCE
    # Registered and active AI agents can VIEW BALANCE without additional customer confirmation.
    # =========================================================================
    if action == ACTION_VIEW_BALANCE:
        has_view_perm = permissions.get("view_balance", True)
        if not has_view_perm:
            return EvaluationResult(
                decision=DECISION_BLOCK,
                rule_number="R4",
                rule_name="Customer Read Permission Missing",
                reason=f"Customer Permission Missing: Customer '{agent_record.get('customer_name')}' has not granted balance view permission to agent '{agent_clean}'."
            )
        return EvaluationResult(
            decision=DECISION_ALLOW,
            rule_number="R4",
            rule_name="Read-Only Information Access",
            reason="Registered and active AI agents can VIEW BALANCE without additional customer confirmation."
        )

    # =========================================================================
    # R5 & R6: BILL PAYMENTS & CUSTOMER PERMISSIONS
    # R5: Registered & active agents with customer-granted bill-payment permission
    #     can PAY BILLS up to ₹5,000 automatically.
    # R6: Bill payments above ₹5,000 must return ASK CUSTOMER.
    # =========================================================================
    if action == ACTION_PAY_BILL:
        # Check customer-granted bill-payment permission
        has_bill_permission = permissions.get("pay_bills", False)

        if not has_bill_permission:
            return EvaluationResult(
                decision=DECISION_BLOCK,
                rule_number="R5",
                rule_name="Customer Bill Payment Permission Missing",
                reason=(
                    f"Customer Permission Missing: Customer '{agent_record.get('customer_name')}' "
                    f"has not granted bill-payment permission to agent '{agent_clean}'. Request must be BLOCKED."
                )
            )

        # Evaluate threshold
        if numeric_amount <= 5000:
            return EvaluationResult(
                decision=DECISION_ALLOW,
                rule_number="R5",
                rule_name="Autonomous Utility Payment Clearance",
                reason=(
                    f"Registered and active agent with customer-granted bill-payment permission "
                    f"can PAY BILLS up to ₹5,000 automatically (Requested: ₹{numeric_amount:,.2f})."
                )
            )
        else:
            return EvaluationResult(
                decision=DECISION_ASK_CUSTOMER,
                rule_number="R6",
                rule_name="High-Value Bill Payment Step-Up",
                reason=(
                    f"Bill payments above ₹5,000 must return ASK CUSTOMER "
                    f"(Requested: ₹{numeric_amount:,.2f} > ₹5,000.00)."
                )
            )

    # =========================================================================
    # R7: TRANSFER MONEY
    # Every TRANSFER MONEY request must return ASK CUSTOMER, regardless of the amount.
    # =========================================================================
    if action == ACTION_TRANSFER_MONEY:
        has_transfer_perm = permissions.get("transfer_money", True)
        if not has_transfer_perm:
            return EvaluationResult(
                decision=DECISION_BLOCK,
                rule_number="R7",
                rule_name="Customer Transfer Permission Missing",
                reason=(
                    f"Customer Permission Missing: Customer '{agent_record.get('customer_name')}' "
                    f"has not granted fund-transfer permission to agent '{agent_clean}'. Request must be BLOCKED."
                )
            )
        return EvaluationResult(
            decision=DECISION_ASK_CUSTOMER,
            rule_number="R7",
            rule_name="Mandatory Fund Transfer Step-Up 2FA",
            reason=(
                f"Every TRANSFER MONEY request must return ASK CUSTOMER, "
                f"regardless of the amount (Requested: ₹{numeric_amount:,.2f})."
            )
        )

    # Fallback
    return EvaluationResult(
        decision=DECISION_BLOCK,
        rule_number="R3",
        rule_name="Unknown Request Category",
        reason="Unrecognized or unsupported request structure. Request must be BLOCKED."
    )
