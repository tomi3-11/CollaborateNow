from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, LoginForm, ProjectCreationForm, UserProfileForm, ProjectRequiredSkillFormSet
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectMembership, UserProfile
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home') # Redirect to home page after registration
    else:
        form = RegistrationForm()
    
    context = { 'form': form}
    return render(request, 'accounts/register.html', context)


def login_view(request):
    if request.method == 'POSt':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home') # Redirect to the home page after successful login.
    else:
        form = AuthenticationForm()

    context = { 'form': form }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    auth_logout(request)
    return redirect('home') # Redirect to the home page after logout.


@login_required
def create_project(request):
    if request.method == 'POST':
        project_form = ProjectCreationForm(request.POST)
        required_skills_formset = ProjectRequiredSkillFormSet(request.POST)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.creator = request.user
            project.save()

            required_skills_formset.instance = project
            required_skills_formset.save()

            return redirect('accounts:project_submitted') # Redirect to a page indicating project submission success
    else:
        project_form = ProjectCreationForm()
        required_skills_formset = ProjectRequiredSkillFormSet()

    context = {'project_form': project_form, 'required_skills_formset': required_skills_formset}
    return render(request, 'accounts/create_project.html', context)


def project_submitted(request):
    return render(request, 'accounts/project_submitted.html')


def project_list(request):
    approved_projects = Project.objects.filter(status='approved')
    
    if request.user.is_authenticated:
        # Get all project IDs the user is a member of
        user_memberships = ProjectMembership.objects.filter(user=request.user).values_list('project_id', flat=True)
        for project in approved_projects:
            project.user_is_member = project.id in user_memberships
    else:
        for project in approved_projects:
            project.user_is_member = False

    context = {'approved_projects': approved_projects}
    return render(request, 'accounts/project_list.html', context)


@login_required
def join_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user is already a member
    if ProjectMembership.objects.filter(user=request.user, project=project).exists():
        messages.error(request, f"You are already a member of '{project.title}'.")
        return redirect('accounts:project_list')
    
    # Create a new membership
    ProjectMembership.objects.create(user=request.user, project=project)

    # Increment the project's current member count
    project.current_members += 1
    project.save()

    messages.success(request, f"You have successfully joined '{project.title}")
    return redirect('accounts:project_list')


@login_required
def joined_projects(request):
    memberships = ProjectMembership.objects.filter(user= request.user)
    joined_projects = [membership.project for membership in memberships]
    context = {'joined_projects': joined_projects}
    return render(request, 'accounts/joined_projects.html', context)


@login_required
def profile(request):
    context = {'user': request.user}
    return render(request, 'accounts/profile.html', context)


@login_required
def profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    context = {'user': request.user, 'profile': user_profile}
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()


    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {'form': form}
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_member = ProjectMembership.objects.filter(user=request.user, project=project).exists()
    if not is_member and not request.user.is_staff and project.creator != request.user:
        messages.error(request, "You do not have permission to access this projects page.")
        return redirect("accounts:project_list")
    
    members = ProjectMembership.objects.filter(project=project).select_related('user_profile') # Efficiently fetch user profiles.
    context = {'project': project, 'members': members, 'is_member': is_member}
    return render(request, 'accounts/project_detail.html', context)

