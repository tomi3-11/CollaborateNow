from django.contrib import admin
from .models import Project, ProjectMembership, UserProfile, ProjectRequiredSkill

# Register your models here.

#admin.site.register(Project)
admin.site.register(ProjectMembership)
admin.site.register(UserProfile)
admin.site.register(ProjectRequiredSkill)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'status')
    list_filter = ('status',)
    actions = ['approve_projects', 'reject_projects']

    def approve_projects(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} project(s) approved.')

    approve_projects.short_description = "Approved selected projects."

    def reject_projects(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} project(s) rejected.")

    reject_projects.short_description = "Rejected selected projects."

admin.site.register(Project, ProjectAdmin)