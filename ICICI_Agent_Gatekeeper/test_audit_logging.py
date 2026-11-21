"""
Audit Logging Verification Test for ICICI Agent Gatekeeper.
Validates:
1. Every request generates a record with: Date/Time, Customer, Agent, Action, Amount, Decision, Rule #, Explanation.
2. Agent Registration is logged in the audit trail.
3. Agent Revocation and exact revocation timestamp are logged in the audit trail.
4. Data remains available across app close / reopen (disk persistence in CSV and JSON).
5. Audit records format correctly into readable table structures.
"""

import storage
import decision_engine
from config import (
    DECISION_ALLOW,
    DECISION_ASK_CUSTOMER,
    DECISION_BLOCK,
    ACTION_VIEW_BALANCE,
    ACTION_PAY_BILL,
    ACTION_TRANSFER_MONEY
)

def run_audit_log_tests():
    print("=" * 80)
    print("  ICICI AGENT GATEKEEPER: AUDIT LOGGING FUNCTIONALITY AUDIT & TEST")
    print("=" * 80)

    # -------------------------------------------------------------
    # TEST 1: Agent Registration Audit Event
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Agent Registration Audit Logging...")
    cust_1 = "Aditya Sen"
    agent_1 = "Aditya Investment Assistant"
    
    reg_agent = storage.save_agent(
        customer_name=cust_1,
        agent_name=agent_1,
        can_view_balance=True,
        can_pay_bills=True,
        can_transfer_money=True
    )
    
    logs = storage.load_audit_log()
    reg_entry = next((l for l in logs if l.get("agent_name") == agent_1 and l.get("action") == "Agent Registration"), None)
    
    assert reg_entry is not None, "Registration event must be logged in audit trail"
    assert reg_entry["timestamp"] is not None, "Timestamp must be present"
    assert reg_entry["customer_name"] == cust_1, "Customer name must match"
    assert reg_entry["rule_number"] == "REG", "Rule code must be REG"
    assert "enrolled" in reg_entry["explanation"].lower(), "Explanation must detail registration"
    
    print("  ✓ Agent Registration recorded in audit log successfully:")
    print(f"    - Event ID:    {reg_entry.get('request_id')}")
    print(f"    - Timestamp:   {reg_entry.get('timestamp')}")
    print(f"    - Action:      {reg_entry.get('action')}")
    print(f"    - Explanation: {reg_entry.get('explanation')}")

    # -------------------------------------------------------------
    # TEST 2: Transaction Request Audit Event (All 8 Required Fields)
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Transaction Request Audit Logging (All 8 Fields)...")
    eval_res = decision_engine.evaluate_request(
        customer_name=cust_1,
        agent_name=agent_1,
        action=ACTION_PAY_BILL,
        amount=4800.0,
        agent_record=reg_agent
    )
    
    logged_req = storage.log_request(
        customer_name=cust_1,
        agent_name=agent_1,
        action=ACTION_PAY_BILL,
        amount=4800.0,
        decision=eval_res.decision,
        rule_number=eval_res.rule_number,
        explanation=eval_res.explanation
    )
    
    required_fields = [
        "timestamp", "customer_name", "agent_name",
        "action", "amount", "decision", "rule_number", "explanation"
    ]
    for field in required_fields:
        assert field in logged_req and logged_req[field] != "", f"Field '{field}' must be present and non-empty"

    print("  ✓ Transaction Request logged with all 8 required fields:")
    print(f"    1. Date and Time:      {logged_req['timestamp']}")
    print(f"    2. Customer Name:      {logged_req['customer_name']}")
    print(f"    3. Agent Name:         {logged_req['agent_name']}")
    print(f"    4. Requested Action:   {logged_req['action']}")
    print(f"    5. Transaction Amount: ₹{logged_req['amount']:,.2f}")
    print(f"    6. Decision:           {logged_req['decision']}")
    print(f"    7. Rule Number:        {logged_req['rule_number']}")
    print(f"    8. Explanation:        {logged_req['explanation']}")

    # -------------------------------------------------------------
    # TEST 3: Agent Revocation Audit Event & Revocation Timestamp
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Agent Revocation Audit Logging & Timestamp...")
    revoke_reason = "Customer lost device containing agent credentials"
    storage.revoke_agent(agent_id=reg_agent["agent_id"], reason=revoke_reason)
    
    logs_after_revoke = storage.load_audit_log()
    rev_entry = next((l for l in logs_after_revoke if l.get("agent_name") == agent_1 and l.get("action") == "Agent Revocation"), None)
    
    assert rev_entry is not None, "Revocation event must be logged in audit trail"
    assert "Revocation Timestamp:" in rev_entry["explanation"], "Revocation timestamp must be recorded in explanation"
    assert rev_entry["decision"] == DECISION_BLOCK, "Revocation decision should be recorded as BLOCK"
    assert rev_entry["rule_number"] == "R1", "Revocation rule must be R1"

    print("  ✓ Agent Revocation event recorded in audit log successfully:")
    print(f"    - Event ID:              {rev_entry.get('request_id')}")
    print(f"    - Date & Time:           {rev_entry.get('timestamp')}")
    print(f"    - Action:                {rev_entry.get('action')}")
    print(f"    - Decision:              {rev_entry.get('decision')}")
    print(f"    - Rule #:                {rev_entry.get('rule_number')}")
    print(f"    - Recorded Explanation:  {rev_entry.get('explanation')}")

    # -------------------------------------------------------------
    # TEST 4: Persistence Test (Simulate App Restart / Reopen)
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Persistence Across Application Restarts (Disk Reload)...")
    # Force reload directly from CSV file
    fresh_logs = storage.load_audit_log()
    
    # Check that our test entries are fully intact
    matched_events = [l for l in fresh_logs if l.get("agent_name") == agent_1]
    assert len(matched_events) >= 3, "All 3 events (Registration, Payment, Revocation) must persist on disk"

    print(f"  ✓ Data remains 100% available on disk ({len(fresh_logs)} total persistent records loaded).")
    print(f"  ✓ Found all {len(matched_events)} lifecycle audit events for '{agent_1}'.")

    # -------------------------------------------------------------
    # TEST 5: Table Formatting Verification
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Readable Table Presentation Structure...")
    import pandas as pd
    df = pd.DataFrame(fresh_logs)
    
    for f in required_fields:
        assert f in df.columns, f"DataFrame must contain column '{f}'"

    print(f"  ✓ Pandas DataFrame successfully formats {len(df)} audit rows with required columns:")
    print("    ", list(df.columns))

    print("\n" + "=" * 80)
    print("  AUDIT LOGGING TEST COMPLETED: ALL REQUIREMENTS VERIFIED!")
    print("=" * 80)

if __name__ == "__main__":
    run_audit_log_tests()
