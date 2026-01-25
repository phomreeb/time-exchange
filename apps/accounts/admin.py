from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined"
    ]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    fieldsets = [
        (
            _("Personal Info"), 
            {
                "fields": [
                    "id",
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ]
            }
        ),
        (
            _("Permissions"),
            {
                "fields": [
                    "groups",
                    "user_permissions",
                ],
            },
        ),
        (_("Important dates"), {"fields": ["last_login", "date_joined"]}),
    ]
    readonly_fields = ["id", "last_login", "date_joined"]

    add_fieldsets = [
        (
            _("Personal Info"), 
            {
                "fields": [
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ]
            }
        )
    ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        filtered_fieldsets = []
        for name, opts in fieldsets:
            fields = tuple(opts.get("fields", ()))
            is_permissions = {"groups", "user_permissions"}.issubset(fields)
            if is_permissions and (obj is None or not obj.is_staff or obj.is_superuser):
                continue
            filtered_fieldsets.append((name, opts))

        return tuple(filtered_fieldsets)
    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            read_fields = super().get_readonly_fields(request, obj)
            return read_fields + ["is_superuser"]
        return super().get_readonly_fields(request, obj)

    # actions = ["activate_selected_users", "deactivate_selected_users"]

    # @admin.action(description="Activate selected users")
    # def activate_selected_users(self, request, queryset):
    #     queryset.update(is_active=True)
    #     self.message_user(request, f"{queryset.count()} users activated successfully")

    # @admin.action(description="Deactivate selected users")
    # def deactivate_selected_users(self, request, queryset):
    #     queryset.update(is_active=False)
    #     self.message_user(request, f"{queryset.count()} users deactivated successfully")
