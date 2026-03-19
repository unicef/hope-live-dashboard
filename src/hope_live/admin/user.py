from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from hope_live.models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin[User]):  # type: ignore[misc]
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):  # type: ignore[misc]
    pass
