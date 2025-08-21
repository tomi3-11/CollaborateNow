from django.contrib import admin
from .models import Project, ProjectMembership, UserProfile, ProjectRequiredSkill, Skill
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

# Register your models here.

#admin.site.register(Project)
# admin.site.register(ProjectMembership)
admin.site.register(UserProfile)
admin.site.register(ProjectRequiredSkill)

admin.site.register(Skill)

class ProjectSkillRequiredInline(admin.TabularInline):
    model = ProjectRequiredSkill
    extra = 1
    
    
class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1 # number of empty forms to display for adding new members
    raw_id_fields = ('user',) # User raw_id_fields for better performance with many users


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'status', 'max_members', 'current_members')
    list_filter = ('status', 'creator', 'created_at')
    actions = ['approve_projects', 'reject_projects', 'email_members']
    inlines = [ProjectSkillRequiredInline, ProjectMembershipInline]
    list_editable = ('status', 'max_members')
    readonly_fields = ('current_members',) # Making the current_members read-only

    def approve_projects(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} project(s) approved.')

    approve_projects.short_description = "Approved selected projects."

    def reject_projects(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} project(s) rejected.")

    reject_projects.short_description = "Rejected selected projects."
    
    """
    Implementing sending emails with a simple message to the console
    Further Implementation will be for the real time email sending
        - Django and SMTP( Simple Mail Transfer Protocol)
    
    """
    def email_members(self, request, queryset):
        for project in queryset:
            memberships = ProjectMembership.objects.filter(project=project).select_related('user')
            recipient_list = [membership.user.email for membership in memberships if membership.user.email]
            if recipient_list:
                # In a real application, This is where the email will be sent
                print(f"Sending email to members of '{project.title}': {recipient_list}")
                self.message_user(request, f"Email initiated to {len(recipient_list)} members of '{project.title}'.")
            else:
                self.message_user(request, f"No members found for '{project.title}'.")
    email_members.short_description = "Email selected project members"

admin.site.register(Project, ProjectAdmin)

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'joined_date')
admin.site.register(ProjectMembership, ProjectMembershipAdmin) # keep the separate admin for ProjectMembership as well.
