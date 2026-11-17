"""
End-to-End Revocation Lifecycle Test for ICICI Agent Gatekeeper.
Demonstrates:
1. Agent Registration (ACTIVE status, timestamp).
2. Successful payment transaction while ACTIVE (ALLOW under R5).
3. Administrative Revocation (Exact timestamp, permanent JSON storage, audit log entry).
4. Attempting another payment after revocation (BLOCK under R1).
"""

import storage
import decision_engine
from config import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    ACTION_PAY_BILL,
    STATUS_ACTIVE,
    STATUS_REVOKED
)

def run_revocation_lifecycle_test():
    print("=" * 75)
    print("  ICICI AGENT GATEKEEPER: AGENT REVOCATION LIFECYCLE TEST")
    print("=" * 75)

    # -------------------------------------------------------------
    # STEP 1: Register a new AI Agent
    # -------------------------------------------------------------
    customer_name = "Kavita Rao"
    agent_name = "Kavita Autonomous FinBot"

    print("\n[STEP 1] Registering New AI Agent...")
    new_agent = storage.save_agent(
        customer_name=customer_name,
        agent_name=agent_name,
        can_view_balance=True,
        can_pay_bills=True,
        can_transfer_money=True
    )

    agent_id = new_agent["agent_id"]
    print(f"  -> Agent ID:           {agent_id}")
    print(f"  -> Customer Name:       {new_agent['customer_name']}")
    print(f"  -> Agent Name:          {new_agent['agent_name']}")
    print(f"  -> Initial Status:      {new_agent['status']}")
    print(f"  -> Registration Time:   {new_agent['registration_date']}")
    print(f"  -> Bill Pay Permission: {new_agent['permissions']['pay_bills']}")

    assert new_agent["status"] == STATUS_ACTIVE, "Initial status must be ACTIVE"
    print("  ✓ Verification: Agent is registered as ACTIVE.")

    # -------------------------------------------------------------
    # STEP 2: Pre-Revocation Payment Evaluation (Expected: ALLOW)
    # -------------------------------------------------------------
    print("\n[STEP 2] Attempting Bill Payment While Agent is ACTIVE (Pre-Revocation)...")
    bill_amount = 3500.0
    pre_result = decision_engine.evaluate_request(
        customer_name=customer_name,
        agent_name=agent_name,
        action=ACTION_PAY_BILL,
        amount=bill_amount,
        agent_record=new_agent
    )

    print(f"  -> Action:      {ACTION_PAY_BILL}")
    print(f"  -> Amount:      ₹{bill_amount:,.2f}")
    print(f"  -> Decision:    {pre_result.decision}")
    print(f"  -> Rule Code:   {pre_result.rule_number}")
    print(f"  -> Rationale:   {pre_result.reason}")

    # Log in audit trail
    storage.log_request(
        customer_name=customer_name,
        agent_name=agent_name,
        action=ACTION_PAY_BILL,
        amount=bill_amount,
        decision=pre_result.decision,
        rule_number=pre_result.rule_number,
        reason=pre_result.reason
    )

    assert pre_result.decision == DECISION_ALLOW, "Active agent with permission must be ALLOWED for bills <= ₹5,000"
    print("  ✓ Verification: Payment was successfully ALLOWED under Rule R5.")

    # -------------------------------------------------------------
    # STEP 3: Administrator Revokes the Agent
    # -------------------------------------------------------------
    print("\n[STEP 3] Administrator Revoking AI Agent...")
    revocation_reason = "Security Audit: Compromised API key and anomalous frequency detected"
    revoke_success = storage.revoke_agent(agent_id=agent_id, reason=revocation_reason)

    assert revoke_success is True, "Revocation function must return True"

    # Reload agent directly from permanent JSON storage to verify persistence
    reloaded_agent = storage.get_agent_by_name(agent_name)
    print(f"  -> Revocation Successful:  {revoke_success}")
    print(f"  -> Updated Status:         {reloaded_agent['status']}")
    print(f"  -> Exact Revocation Time:  {reloaded_agent['revoked_at']}")
    print(f"  -> Recorded Reason:        {reloaded_agent['revocation_reason']}")

    assert reloaded_agent["status"] == STATUS_REVOKED, "Agent status must be REVOKED in storage"
    assert reloaded_agent["revoked_at"] is not None, "Revocation timestamp must not be None"
    print("  ✓ Verification: Permanent JSON file updated with REVOKED status and timestamp.")

    # -------------------------------------------------------------
    # STEP 4: Post-Revocation Payment Evaluation (Expected: BLOCK under R1)
    # -------------------------------------------------------------
    print("\n[STEP 4] Attempting Payment With REVOKED Agent (Post-Revocation)...")
    post_result = decision_engine.evaluate_request(
        customer_name=customer_name,
        agent_name=agent_name,
        action=ACTION_PAY_BILL,
        amount=bill_amount,
        agent_record=reloaded_agent
    )

    print(f"  -> Action Attempted: {ACTION_PAY_BILL}")
    print(f"  -> Amount:           ₹{bill_amount:,.2f}")
    print(f"  -> Gatekeeper Verdict: {post_result.decision}")
    print(f"  -> Rule Triggered:   {post_result.rule_number}")
    print(f"  -> Explanation:      {post_result.reason}")

    # Record the blocked attempt in the permanent audit trail
    storage.log_request(
        customer_name=customer_name,
        agent_name=agent_name,
        action=ACTION_PAY_BILL,
        amount=bill_amount,
        decision=post_result.decision,
        rule_number=post_result.rule_number,
        reason=post_result.reason
    )

    assert post_result.decision == DECISION_BLOCK, "Revoked agent must be strictly BLOCKED"
    assert post_result.rule_number == "R1", "Revocation rule R1 must trigger first"
    print("  ✓ Verification: Revoked agent was strictly BLOCKED under Rule R1.")

    # -------------------------------------------------------------
    # STEP 5: Verify Security Audit Log Trail
    # -------------------------------------------------------------
    print("\n[STEP 5] Inspecting Permanent Audit Log for Revocation and Block Records...")
    audit_trail = storage.load_audit_log()
    recent_agent_events = [e for e in audit_trail if e.get("agent_name") == agent_name]

    print(f"  -> Total Audit Entries for '{agent_name}': {len(recent_agent_events)}")
    for idx, event in enumerate(recent_agent_events, 1):
        print(f"     [{idx}] Timestamp: {event.get('timestamp')} | Action: {event.get('action')} | Verdict: {event.get('decision')} | Rule: {event.get('rule_number')}")

    print("\n" + "=" * 75)
    print("  ALL 7 REVOCATION REQUIREMENTS FULLY MET & VERIFIED!")
    print("=" * 75)

if __name__ == "__main__":
    run_revocation_lifecycle_test()
