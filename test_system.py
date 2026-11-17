"""
Comprehensive Unit Test Suite for ICICI Agent Gatekeeper.
Validates the Decision Engine (Rules R1 through R8) and Permanent Storage.
"""

import unittest
import os
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

class TestAgentGatekeeperRules(unittest.TestCase):

    def setUp(self):
        storage.ensure_data_directory()

    def test_r1_revocation_checked_first(self):
        """R1: If an AI agent has been revoked, all its requests must be BLOCKED."""
        revoked_agent = {
            "agent_id": "AGT-1004",
            "customer_name": "Sneha Roy",
            "agent_name": "Sneha Expense Manager",
            "status": STATUS_REVOKED,
            "permissions": {"view_balance": True, "pay_bills": True, "transfer_money": True},
            "revoked_at": "2026-11-15 11:00:00",
            "revocation_reason": "Administrative suspension"
        }
        # Even for View Balance (which would otherwise be ALLOW under R4), revoked agent MUST be BLOCKED under R1
        result = decision_engine.evaluate_request(
            customer_name="Sneha Roy",
            agent_name="Sneha Expense Manager",
            action=ACTION_VIEW_BALANCE,
            amount=0.0,
            agent_record=revoked_agent
        )
        self.assertEqual(result.decision, DECISION_BLOCK)
        self.assertEqual(result.rule_number, "R1")
        self.assertIn("permanently REVOKED", result.reason)

    def test_r2_unregistered_agent(self):
        """R2: If an AI agent is not registered with the bank, its request must be BLOCKED."""
        result = decision_engine.evaluate_request(
            customer_name="Stranger",
            agent_name="Unknown Hacking Bot",
            action=ACTION_VIEW_BALANCE,
            amount=0.0,
            agent_record=None
        )
        self.assertEqual(result.decision, DECISION_BLOCK)
        self.assertEqual(result.rule_number, "R2")
        self.assertIn("not registered", result.reason)

    def test_r2_customer_agent_ownership(self):
        """R2: Mismatched customer-agent ownership must be BLOCKED."""
        active_agent = {
            "agent_id": "AGT-1001",
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "status": STATUS_ACTIVE,
            "permissions": {"view_balance": True, "pay_bills": True}
        }
        # An unauthorized user attempting to invoke Rohan's agent
        result = decision_engine.evaluate_request(
            customer_name="Malicious Actor",
            agent_name="Rohan Personal Assistant",
            action=ACTION_VIEW_BALANCE,
            amount=0.0,
            agent_record=active_agent
        )
        self.assertEqual(result.decision, DECISION_BLOCK)
        self.assertEqual(result.rule_number, "R2")
        self.assertIn("ownership mismatch", result.reason.lower())

    def test_r3_invalid_action(self):
        """R3: Invalid actions must be BLOCKED."""
        active_agent = {
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "status": STATUS_ACTIVE,
            "permissions": {"view_balance": True}
        }
        result = decision_engine.evaluate_request(
            customer_name="Rohan Sharma",
            agent_name="Rohan Personal Assistant",
            action="Apply For Crypto Loan",
            amount=100.0,
            agent_record=active_agent
        )
        self.assertEqual(result.decision, DECISION_BLOCK)
        self.assertEqual(result.rule_number, "R3")
        self.assertIn("Invalid action", result.reason)

    def test_r3_negative_and_zero_amount(self):
        """R3: Negative and zero transaction amounts must be BLOCKED."""
        active_agent = {
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "status": STATUS_ACTIVE,
            "permissions": {"pay_bills": True}
        }
        # Negative amount
        neg_res = decision_engine.evaluate_request(
            customer_name="Rohan Sharma",
            agent_name="Rohan Personal Assistant",
            action=ACTION_PAY_BILL,
            amount=-500.0,
            agent_record=active_agent
        )
        self.assertEqual(neg_res.decision, DECISION_BLOCK)
        self.assertEqual(neg_res.rule_number, "R3")
        self.assertIn("negative", neg_res.reason.lower())

        # Zero amount
        zero_res = decision_engine.evaluate_request(
            customer_name="Rohan Sharma",
            agent_name="Rohan Personal Assistant",
            action=ACTION_TRANSFER_MONEY,
            amount=0.0,
            agent_record=active_agent
        )
        self.assertEqual(zero_res.decision, DECISION_BLOCK)
        self.assertEqual(zero_res.rule_number, "R3")

    def test_r4_view_balance(self):
        """R4: Registered and active AI agents can VIEW BALANCE without additional customer confirmation."""
        active_agent = {
            "customer_name": "Priya Nair",
            "agent_name": "Priya SmartFin Bot",
            "status": STATUS_ACTIVE,
            "permissions": {"view_balance": True}
        }
        result = decision_engine.evaluate_request(
            customer_name="Priya Nair",
            agent_name="Priya SmartFin Bot",
            action=ACTION_VIEW_BALANCE,
            amount=0.0,
            agent_record=active_agent
        )
        self.assertEqual(result.decision, DECISION_ALLOW)
        self.assertEqual(result.rule_number, "R4")
        self.assertIn("VIEW BALANCE", result.reason)

    def test_r5_pay_bills_up_to_5000_with_permission(self):
        """R5: Active agents with bill-payment permission can PAY BILLS up to ₹5,000 automatically."""
        agent_with_permission = {
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "status": STATUS_ACTIVE,
            "permissions": {"pay_bills": True}
        }
        result = decision_engine.evaluate_request(
            customer_name="Rohan Sharma",
            agent_name="Rohan Personal Assistant",
            action=ACTION_PAY_BILL,
            amount=4200.0,
            agent_record=agent_with_permission
        )
        self.assertEqual(result.decision, DECISION_ALLOW)
        self.assertEqual(result.rule_number, "R5")
        self.assertIn("PAY BILLS up to ₹5,000 automatically", result.reason)

    def test_r5_pay_bills_without_customer_permission(self):
        """R5: Agents without customer-granted bill-payment permission must be BLOCKED."""
        agent_no_permission = {
            "customer_name": "Amitabh Patel",
            "agent_name": "Amitabh ReadOnly Agent",
            "status": STATUS_ACTIVE,
            "permissions": {"pay_bills": False}
        }
        result = decision_engine.evaluate_request(
            customer_name="Amitabh Patel",
            agent_name="Amitabh ReadOnly Agent",
            action=ACTION_PAY_BILL,
            amount=1500.0,
            agent_record=agent_no_permission
        )
        self.assertEqual(result.decision, DECISION_BLOCK)
        self.assertEqual(result.rule_number, "R5")
        self.assertIn("Customer Permission Missing", result.reason)

    def test_r6_pay_bills_above_5000(self):
        """R6: Bill payments above ₹5,000 must return ASK CUSTOMER."""
        agent_with_permission = {
            "customer_name": "Rohan Sharma",
            "agent_name": "Rohan Personal Assistant",
            "status": STATUS_ACTIVE,
            "permissions": {"pay_bills": True}
        }
        result = decision_engine.evaluate_request(
            customer_name="Rohan Sharma",
            agent_name="Rohan Personal Assistant",
            action=ACTION_PAY_BILL,
            amount=7500.0,
            agent_record=agent_with_permission
        )
        self.assertEqual(result.decision, DECISION_ASK_CUSTOMER)
        self.assertEqual(result.rule_number, "R6")
        self.assertIn("ASK CUSTOMER", result.reason)

    def test_r7_transfer_money_always_asks_customer(self):
        """R7: Every TRANSFER MONEY request must return ASK CUSTOMER, regardless of amount."""
        active_agent = {
            "customer_name": "Priya Nair",
            "agent_name": "Priya SmartFin Bot",
            "status": STATUS_ACTIVE,
            "permissions": {"transfer_money": True}
        }
        # Small amount (₹200) -> Still ASK CUSTOMER
        res_small = decision_engine.evaluate_request(
            customer_name="Priya Nair",
            agent_name="Priya SmartFin Bot",
            action=ACTION_TRANSFER_MONEY,
            amount=200.0,
            agent_record=active_agent
        )
        self.assertEqual(res_small.decision, DECISION_ASK_CUSTOMER)
        self.assertEqual(res_small.rule_number, "R7")

        # Large amount (₹50,000) -> Still ASK CUSTOMER
        res_large = decision_engine.evaluate_request(
            customer_name="Priya Nair",
            agent_name="Priya SmartFin Bot",
            action=ACTION_TRANSFER_MONEY,
            amount=50000.0,
            agent_record=active_agent
        )
        self.assertEqual(res_large.decision, DECISION_ASK_CUSTOMER)
        self.assertEqual(res_large.rule_number, "R7")

    def test_r8_permanent_audit_log(self):
        """R8: Every request and decision must be recorded permanently in the audit log."""
        log_entry = storage.log_request(
            customer_name="Test Customer",
            agent_name="Test Agent",
            action=ACTION_PAY_BILL,
            amount=3500.0,
            decision=DECISION_ALLOW,
            rule_number="R5",
            reason="Test automated verification"
        )
        self.assertIsNotNone(log_entry.get("request_id"))
        self.assertIsNotNone(log_entry.get("timestamp"))
        self.assertEqual(log_entry.get("rule_number"), "R5")

        # Verify entry exists in loaded audit log
        logs = storage.load_audit_log()
        self.assertTrue(any(l["request_id"] == log_entry["request_id"] for l in logs))

if __name__ == "__main__":
    unittest.main()
