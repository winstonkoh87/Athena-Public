from enum import Enum
from typing import List, Dict, Optional

class Seat(Enum):
    STRATEGIST = "The Strategist"
    GUARDIAN = "The Guardian"
    OPERATOR = "The Operator"
    ARCHITECT = "The Architect"
    SKEPTIC = "The Skeptic"
    COMPLIANCE_GATE = "The Compliance Gate"

class SpecializedRole(Enum):
    PM = "Product Manager"
    BA = "Business Analyst"
    SECURITY_ENGINEER = "Security Engineer"
    RISK_OFFICER = "Risk Officer"
    FRONTEND_DEV = "Frontend Developer"
    BACKEND_DEV = "Backend Developer"
    DEVOPS_ENGINEER = "DevOps Engineer"
    SYSTEM_ARCHITECT = "System Architect"
    DATABASE_ARCHITECT = "Database Architect"
    QA_ENGINEER = "QA Engineer"
    RED_TEAMER = "Red Teamer"
    LEGAL_COMPLIANCE = "Legal/Compliance"
    TECH_LEAD = "Tech Lead"

# Mapping specialized roles to core seats per Protocol 333
ROLE_TO_SEAT_MAP = {
    SpecializedRole.PM: Seat.STRATEGIST,
    SpecializedRole.BA: Seat.STRATEGIST,
    SpecializedRole.SECURITY_ENGINEER: Seat.GUARDIAN,
    SpecializedRole.RISK_OFFICER: Seat.GUARDIAN,
    SpecializedRole.FRONTEND_DEV: Seat.OPERATOR,
    SpecializedRole.BACKEND_DEV: Seat.OPERATOR,
    SpecializedRole.DEVOPS_ENGINEER: Seat.OPERATOR,
    SpecializedRole.SYSTEM_ARCHITECT: Seat.ARCHITECT,
    SpecializedRole.DATABASE_ARCHITECT: Seat.ARCHITECT,
    SpecializedRole.QA_ENGINEER: Seat.SKEPTIC,
    SpecializedRole.RED_TEAMER: Seat.SKEPTIC,
    SpecializedRole.LEGAL_COMPLIANCE: Seat.COMPLIANCE_GATE,
    SpecializedRole.TECH_LEAD: Seat.COMPLIANCE_GATE,
}

class COSEngine:
    """
    Committee of Seats (COS) Engine.
    Manages identity-driven reasoning and perspective-taking.
    """
    def __init__(self):
        self.active_seats: List[Seat] = list(Seat)
        self.active_roles: Dict[SpecializedRole, Seat] = ROLE_TO_SEAT_MAP

    def get_seat_for_role(self, role: SpecializedRole) -> Seat:
        return self.active_roles.get(role)

    def get_roles_for_seat(self, seat: Seat) -> List[SpecializedRole]:
        return [role for role, assigned_seat in self.active_roles.items() if assigned_seat == seat]

    def format_perspective_prompt(self, seat_or_role) -> str:
        """Formats a prompt prefix for a specific seat or role."""
        name = seat_or_role.value
        return f"Speaking as **{name}**, "

    def get_committee_for_complexity(self, complexity: int) -> List[Seat]:
        """
        Returns a subset of seats based on task complexity (1-100).
        Per Protocol 166 (Deep Think Proxy).
        """
        if complexity < 30:
            return [Seat.OPERATOR]
        elif complexity < 70:
            return [Seat.STRATEGIST, Seat.OPERATOR, Seat.SKEPTIC]
        else:
            return list(Seat)

def get_cos_engine() -> COSEngine:
    return COSEngine()
