from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    min_members = models.IntegerField(default=4)
    max_members = models.IntegerField(default=7)
    required_skills = models.TextField(help_text="ist of required skills for this project, separated by commas")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    current_members = models.IntegerField(default=0)  # Temporary field for demonstration
    # Project Details
    objectives = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    operation_days = models.CharField(max_length=200, blank=True, help_text="e.g. Mon, Wednesday, Friday")
    deadline = models.DateField(blank=True, null=True)
    # Project Status
    action = models.CharField(max_length=20, choices=[
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ], default='ongoing')
    # Project Type
    project_type = models.CharField(max_length=20, choices=[
        ('open_source', 'Open Source'),
        ('private', 'Private'),
        ('public', 'Public'),
    ], default='open_source')
    # Project Visibility
    visibility = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('private', 'Private'),
        ('restricted', 'Restricted'),
    ], default='public')
    # Project Location
    location = models.CharField(max_length=100, blank=True, help_text="e.g. Remote, On-site")
    

    def __str__(self):
        return self.title


class ProjectMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project') # Ensure a user can't join the same project mulriple times.


    def __str__(self):
        return f"{self.user.username} joined {self.project.title}"
    

class UserProfile(models.Model):
    user =models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    skills = models.TextField(blank=True, help_text="List your skills (e.g. Python, UI/UX, Illustration), separated by commas.")
    bio = models.TextField(blank=True, help_text="Tell us a bit about yourself and your interests.")
    portfolio_url = models.URLField(blank=True, null=True, help_text='Link to your online portfolis (e.g., Github )')
    experience_level = models.CharField(
        max_length=200,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        blank=True,
        null=True,
        help_text='Your Overall experience level.'
    )

    def __str__(self):
        return self.user.username
