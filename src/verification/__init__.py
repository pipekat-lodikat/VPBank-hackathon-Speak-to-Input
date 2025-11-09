"""
Verification module for achieving 99% accuracy compliance with BTC requirements.
"""

from .verification_handler import (
    VerificationHandler,
    VerificationStatus,
    FieldVerification,
    FormVerification,
    verification_handler
)

__all__ = [
    'VerificationHandler',
    'VerificationStatus',
    'FieldVerification',
    'FormVerification',
    'verification_handler'
]
