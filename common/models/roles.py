"""
common/models/roles.py
Defines official AEC role hierarchy for SR-05 (RBAC).
"""

from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"                         # System administrator
    AEC_STAFF = "aec_staff"                 # Handles registration/enrolment
    COMMISSIONER_DELEGATE = "commissioner_delegate"  # Manages candidates/results
    VOTER = "voter"                         # Standard eligible voter
    OBSERVER = "observer"                   # Read-only auditor
    GUEST = "guest"                         # Unauthenticated or public
