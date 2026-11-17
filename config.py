"""
Configuration and UI Branding for ICICI Bank Agent Gatekeeper.
Designed for MBA Academic Project.
"""

# Student Project Information
STUDENT_NAME = "MBA Candidate"
ENROLMENT_NUMBER = "PGD202563436"
PROJECT_TITLE = "AGENT GATEKEEPER"
PROJECT_SUBTITLE = "An AI Agent Permission and Risk Management System for ICICI Bank"
BANK_NAME = "ICICI Bank"

# Corporate Brand Colors (Official ICICI Palette)
COLOR_PRIMARY = "#B3282D"     # ICICI Maroon / Deep Red
COLOR_SECONDARY = "#F58220"   # ICICI Corporate Orange
COLOR_NAVY = "#0B2341"        # Corporate Navy
COLOR_BG_LIGHT = "#F8F9FA"    # Soft Background Gray
COLOR_SUCCESS = "#2E7D32"     # Emerald Green for ALLOW
COLOR_WARNING = "#ED6C02"     # Amber Orange for ASK CUSTOMER
COLOR_DANGER = "#D32F2F"      # Crimson Red for BLOCK

# Available Agent Actions
ACTION_VIEW_BALANCE = "View Balance"
ACTION_PAY_BILL = "Pay Bill"
ACTION_TRANSFER_MONEY = "Transfer Money"

ACTIONS = [ACTION_VIEW_BALANCE, ACTION_PAY_BILL, ACTION_TRANSFER_MONEY]

# Decision Constants
DECISION_ALLOW = "ALLOW"
DECISION_ASK_CUSTOMER = "ASK CUSTOMER"
DECISION_BLOCK = "BLOCK"

# Agent Statuses
STATUS_ACTIVE = "ACTIVE"
STATUS_REVOKED = "REVOKED"
