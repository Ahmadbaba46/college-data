from __future__ import annotations

from django.contrib.auth.models import AnonymousUser


def user_in_groups(user, group_names: list[str]) -> bool:
    if not user or isinstance(user, AnonymousUser):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    user_groups = set(user.groups.values_list('name', flat=True))
    return any(name in user_groups for name in group_names)
