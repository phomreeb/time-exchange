from django.contrib import admin
from apps.audits.models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "actor", "module", "action", "ip_address"]
    list_filter = ["module", "timestamp"]
    search_fields = ["actor__email", "action", "description", "ip_address"]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
