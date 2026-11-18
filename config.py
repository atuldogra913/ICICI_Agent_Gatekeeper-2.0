"""
Configuration and Official ICICI Bank Brand Palette for Agent Gatekeeper.
Designed for MBA Academic Project & Presentation.
"""

# Student Project Information
STUDENT_NAME = "MBA Candidate"
ENROLMENT_NUMBER = "PGD202563436"
PROJECT_TITLE = "AGENT GATEKEEPER"
PROJECT_SUBTITLE = "An AI Agent Permission and Risk Management System for ICICI Bank"
BANK_NAME = "ICICI Bank"
BANK_TAGLINE = "Hum Hai Na, Khayal Aapka"

# Official ICICI Bank Brand Color Palette
ICICI_MAROON = "#8B1E22"       # Signature ICICI Deep Maroon / Crimson
ICICI_MAROON_DARK = "#661417"  # Dark Burgundy for gradients
ICICI_ORANGE = "#F58220"       # Official ICICI Corporate Orange
ICICI_ORANGE_LIGHT = "#FFF3E8" # Soft Orange tint for highlight cards
ICICI_GOLD = "#FDB813"         # Golden Yellow accent
ICICI_NAVY = "#002B49"         # ICICI Corporate Deep Navy
ICICI_BG = "#FDFBF7"           # Warm off-white / ivory banking canvas
CARD_WHITE = "#FFFFFF"         # Card background
TEXT_DARK = "#1E293B"          # High-contrast charcoal text
TEXT_MUTED = "#64748B"         # Subdued slate for subtitles
BORDER_COLOR = "#E2E8F0"       # Clean subtle border

# Legacy / Universal Color Aliases
COLOR_PRIMARY = ICICI_MAROON
COLOR_SECONDARY = ICICI_ORANGE
COLOR_NAVY = ICICI_NAVY
COLOR_BG_LIGHT = ICICI_BG
COLOR_SUCCESS = "#0A7E3E"      # ICICI Green for ALLOW
COLOR_WARNING = "#D97706"      # ICICI Amber for ASK CUSTOMER
COLOR_DANGER = "#DC2626"       # ICICI Crimson Red for BLOCK

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
