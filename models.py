"""Compatibility shim: expose models from static.models.models

This file allows existing imports like `from models.models import ...`
to work while the actual definitions live under `static/models/models.py`.
"""
from static.models.models import (
    db,
    User,
    Complaint,
    Notification,
    Upvote,
    Department,
    Update,
    Escalation,
)

__all__ = [
    'db', 'User', 'Complaint', 'Notification', 'Upvote', 'Department', 'Update', 'Escalation'
]
