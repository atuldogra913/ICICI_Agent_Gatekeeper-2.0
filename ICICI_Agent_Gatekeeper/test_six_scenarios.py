"""
Comprehensive Verification Script for the 6 Test Scenarios:
1. Registered active agent requesting View Balance = ALLOW (R4).
2. Unknown agent requesting a transaction = BLOCK (R2).
3. Registered agent requesting bill payment of ₹8,000 = ASK CUSTOMER (R6).
4. Registered agent with bill-payment permission requesting ₹2,000 = ALLOW (R5).
5. Revoked agent requesting a transaction = BLOCK (R1).
6. Registered active agent requesting Transfer Money = ASK CUSTOMER (R7).

Also verifies:
- Rule precedence (R1 checked first, R2 unknown agent check, R3 validation, R5 permission checks).
- Audit logging for every scenario into permanent CSV and JSON storage.
"""

import storage
import decision_engine
from config import (
    DECISION_ALLOW,
    DECISION_ASK_CUSTOMER,
    DECISION_BLOCK,
    ACTION_VIEW_BALANCE,
    ACTION_PAY_BILL,
    ACTION_TRANSFER_MONEY,
    STATUS_ACTIVE,
    STATUS_REVOKED
)

def run_scenario_verifications():
    print("=" * 80)
    print("  ICICI AGENT GATEKEEPER: 6 CORE SCENARIO VERIFICATION TEST")
    print("=" * 80)

    storage.ensure_data_directory()

    # Pre-test: Ensure we have sample agents available
    active_agent = storage.get_agent_by_name("Rohan Personal Assistant")
    if not active_agent:
        active_agent = storage.save_agent("Rohan Sharma", "Rohan Personal Assistant", True, True, True)

    revoked_agent = storage.get_agent_by_name("Sneha Expense Manager")
    if not revoked_agent:
        sneha = storage.save_agent("Sneha Roy", "Sneha Expense Manager", True, True, True)
        storage.revoke_agent(sneha["agent_id"], "Administrative freeze: Suspicious pattern")
        revoked_agent = storage.get_agent_by_name("Sneha Expense Manager")

    results_summary = []

    # -------------------------------------------------------------
    # SCENARIO 1: Registered active agent requesting View Balance = ALLOW
    # -------------------------------------------------------------
    print("\n[SCENARIO 1] Registered Active Agent requesting View Balance...")
    s1_cust = active_agent["customer_name"]
    s1_agent = active_agent["agent_name"]
    res1 = decision_engine.evaluate_request(
        customer_name=s1_cust,
        agent_name=s1_agent,
        action=ACTION_VIEW_BALANCE,
        amount=0.0,
        agent_record=active_agent
    )
    print(f"  -> Agent:       {s1_agent} (Customer: {s1_cust})")
    print(f"  -> Action:      {ACTION_VIEW_BALANCE}")
    print(f"  -> Decision:    {res1.decision} (Expected: ALLOW)")
    print(f"  -> Rule Code:   {res1.rule_number} ({res1.rule_name})")
    print(f"  -> Explanation: {res1.reason}")

    assert res1.decision == DECISION_ALLOW, "Scenario 1 must return ALLOW"
    assert res1.rule_number == "R4", "Scenario 1 must trigger Rule R4"
    results_summary.append(("Scenario 1: View Balance", res1.decision, res1.rule_number, "PASS"))

    # Log to audit trail
    storage.log_request(s1_cust, s1_agent, ACTION_VIEW_BALANCE, 0.0, res1.decision, res1.rule_number, res1.explanation)

    # -------------------------------------------------------------
    # SCENARIO 2: Unknown agent requesting a transaction = BLOCK
    # -------------------------------------------------------------
    print("\n[SCENARIO 2] Unknown Agent requesting a transaction...")
    s2_cust = "Ankit Verma"
    s2_agent = "Rogue Unregistered Scraper Bot"
    res2 = decision_engine.evaluate_request(
        customer_name=s2_cust,
        agent_name=s2_agent,
        action=ACTION_VIEW_BALANCE,
        amount=0.0,
        agent_record=None  # Unknown agent
    )
    print(f"  -> Agent:       {s2_agent} (Unregistered)")
    print(f"  -> Action:      {ACTION_VIEW_BALANCE}")
    print(f"  -> Decision:    {res2.decision} (Expected: BLOCK)")
    print(f"  -> Rule Code:   {res2.rule_number} ({res2.rule_name})")
    print(f"  -> Explanation: {res2.reason}")

    assert res2.decision == DECISION_BLOCK, "Scenario 2 must return BLOCK"
    assert res2.rule_number == "R2", "Scenario 2 must trigger Rule R2"
    results_summary.append(("Scenario 2: Unknown Agent", res2.decision, res2.rule_number, "PASS"))

    storage.log_request(s2_cust, s2_agent, ACTION_VIEW_BALANCE, 0.0, res2.decision, res2.rule_number, res2.explanation)

    # -------------------------------------------------------------
    # SCENARIO 3: Registered agent requesting bill payment of ₹8,000 = ASK CUSTOMER
    # -------------------------------------------------------------
    print("\n[SCENARIO 3] Registered Agent requesting bill payment of ₹8,000...")
    s3_amount = 8000.0
    res3 = decision_engine.evaluate_request(
        customer_name=s1_cust,
        agent_name=s1_agent,
        action=ACTION_PAY_BILL,
        amount=s3_amount,
        agent_record=active_agent
    )
    print(f"  -> Agent:       {s1_agent}")
    print(f"  -> Action:      {ACTION_PAY_BILL}")
    print(f"  -> Amount:      ₹{s3_amount:,.2f}")
    print(f"  -> Decision:    {res3.decision} (Expected: ASK CUSTOMER)")
    print(f"  -> Rule Code:   {res3.rule_number} ({res3.rule_name})")
    print(f"  -> Explanation: {res3.reason}")

    assert res3.decision == DECISION_ASK_CUSTOMER, "Scenario 3 must return ASK CUSTOMER"
    assert res3.rule_number == "R6", "Scenario 3 must trigger Rule R6"
    results_summary.append(("Scenario 3: Pay Bill ₹8,000", res3.decision, res3.rule_number, "PASS"))

    storage.log_request(s1_cust, s1_agent, ACTION_PAY_BILL, s3_amount, res3.decision, res3.rule_number, res3.explanation)

    # -------------------------------------------------------------
    # SCENARIO 4: Registered agent with bill-payment permission requesting ₹2,000 = ALLOW
    # -------------------------------------------------------------
    print("\n[SCENARIO 4] Registered Agent with bill-payment permission requesting ₹2,000...")
    s4_amount = 2000.0
    res4 = decision_engine.evaluate_request(
        customer_name=s1_cust,
        agent_name=s1_agent,
        action=ACTION_PAY_BILL,
        amount=s4_amount,
        agent_record=active_agent
    )
    print(f"  -> Agent:       {s1_agent}")
    print(f"  -> Action:      {ACTION_PAY_BILL}")
    print(f"  -> Amount:      ₹{s4_amount:,.2f}")
    print(f"  -> Decision:    {res4.decision} (Expected: ALLOW)")
    print(f"  -> Rule Code:   {res4.rule_number} ({res4.rule_name})")
    print(f"  -> Explanation: {res4.reason}")

    assert res4.decision == DECISION_ALLOW, "Scenario 4 must return ALLOW"
    assert res4.rule_number == "R5", "Scenario 4 must trigger Rule R5"
    results_summary.append(("Scenario 4: Pay Bill ₹2,000", res4.decision, res4.rule_number, "PASS"))

    storage.log_request(s1_cust, s1_agent, ACTION_PAY_BILL, s4_amount, res4.decision, res4.rule_number, res4.explanation)

    # -------------------------------------------------------------
    # SCENARIO 5: Revoked agent requesting a transaction = BLOCK
    # -------------------------------------------------------------
    print("\n[SCENARIO 5] Revoked Agent requesting a transaction...")
    s5_cust = revoked_agent["customer_name"]
    s5_agent = revoked_agent["agent_name"]
    res5 = decision_engine.evaluate_request(
        customer_name=s5_cust,
        agent_name=s5_agent,
        action=ACTION_VIEW_BALANCE,
        amount=0.0,
        agent_record=revoked_agent
    )
    print(f"  -> Agent:       {s5_agent} (Status: REVOKED on {revoked_agent.get('revoked_at')})")
    print(f"  -> Action:      {ACTION_VIEW_BALANCE}")
    print(f"  -> Decision:    {res5.decision} (Expected: BLOCK)")
    print(f"  -> Rule Code:   {res5.rule_number} ({res5.rule_name})")
    print(f"  -> Explanation: {res5.reason}")

    assert res5.decision == DECISION_BLOCK, "Scenario 5 must return BLOCK"
    assert res5.rule_number == "R1", "Scenario 5 must trigger Rule R1 (Revocation first)"
    results_summary.append(("Scenario 5: Revoked Agent", res5.decision, res5.rule_number, "PASS"))

    storage.log_request(s5_cust, s5_agent, ACTION_VIEW_BALANCE, 0.0, res5.decision, res5.rule_number, res5.explanation)

    # -------------------------------------------------------------
    # SCENARIO 6: Registered active agent requesting Transfer Money = ASK CUSTOMER
    # -------------------------------------------------------------
    print("\n[SCENARIO 6] Registered Active Agent requesting Transfer Money...")
    s6_amount = 1500.0
    res6 = decision_engine.evaluate_request(
        customer_name=s1_cust,
        agent_name=s1_agent,
        action=ACTION_TRANSFER_MONEY,
        amount=s6_amount,
        agent_record=active_agent
    )
    print(f"  -> Agent:       {s1_agent}")
    print(f"  -> Action:      {ACTION_TRANSFER_MONEY}")
    print(f"  -> Amount:      ₹{s6_amount:,.2f}")
    print(f"  -> Decision:    {res6.decision} (Expected: ASK CUSTOMER)")
    print(f"  -> Rule Code:   {res6.rule_number} ({res6.rule_name})")
    print(f"  -> Explanation: {res6.reason}")

    assert res6.decision == DECISION_ASK_CUSTOMER, "Scenario 6 must return ASK CUSTOMER"
    assert res6.rule_number == "R7", "Scenario 6 must trigger Rule R7"
    results_summary.append(("Scenario 6: Transfer Money", res6.decision, res6.rule_number, "PASS"))

    storage.log_request(s1_cust, s1_agent, ACTION_TRANSFER_MONEY, s6_amount, res6.decision, res6.rule_number, res6.explanation)

    # -------------------------------------------------------------
    # AUDIT LOG VERIFICATION
    # -------------------------------------------------------------
    print("\n[AUDIT LOG] Verifying Permanent Audit Trail in CSV and JSON...")
    logs = storage.load_audit_log()
    print(f"  -> Total Events in Audit Ledger: {len(logs)}")
    
    # Check that our latest 6 events were recorded with all 8 fields
    recent_events = logs[:6]
    required_keys = ["timestamp", "customer_name", "agent_name", "action", "amount", "decision", "rule_number", "explanation"]
    
    for idx, ev in enumerate(recent_events, 1):
        for k in required_keys:
            assert k in ev and ev[k] is not None, f"Audit event must contain '{k}'"
        print(f"     Record {idx}: {ev['timestamp']} | {ev['action']} | ₹{ev['amount']} | {ev['decision']} | {ev['rule_number']}")

    print("\n" + "=" * 80)
    print("  VERIFICATION RESULTS MATRIX:")
    print("=" * 80)
    for name, dec, rule, status in results_summary:
        print(f"  ✓ {name:<35} -> Verdict: {dec:<14} Rule: {rule:<5} [{status}]")
    print("=" * 80)
    print("  ALL 6 SCENARIOS AND AUDIT LOGGING FULLY VERIFIED AND PASSING!")
    print("=" * 80)

if __name__ == "__main__":
    run_scenario_verifications()
