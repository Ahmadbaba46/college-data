from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import User

from users.models import UserProfile
from users.permissions import user_in_groups


@dataclass
class ActingContext:
    user: User | None
    teacher: object | None
    is_teacher_limited: bool


def resolve_acting_context(username: str | None) -> ActingContext:
    """Resolve acting user and whether teacher-course restrictions apply.

    - If username is None: returns (None, None, False)
    - If user is superuser/Admin/DataEntry: not teacher-limited
    - If user is Teacher only: teacher-limited and requires linked UserProfile.teacher
    """
    if not username:
        return ActingContext(user=None, teacher=None, is_teacher_limited=False)

    user = User.objects.get(username=username)

    # Admin/DataEntry can do anything
    if user_in_groups(user, ['Admin', 'DataEntry']):
        return ActingContext(user=user, teacher=None, is_teacher_limited=False)

    # Teacher-limited
    if user_in_groups(user, ['Teacher']):
        profile = UserProfile.objects.filter(user=user).select_related('teacher').first()
        teacher = profile.teacher if profile else None
        if not teacher:
            raise ValueError('Teacher user is not linked to a Teacher profile.')
        return ActingContext(user=user, teacher=teacher, is_teacher_limited=True)

    # Unknown role: treat as no permissions for restricted operations
    return ActingContext(user=user, teacher=None, is_teacher_limited=True)
