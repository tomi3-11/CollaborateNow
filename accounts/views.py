from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, LoginForm, ProjectCreationForm, UserProfileForm, ProjectRequiredSkillFormSet, CreateProjectStep1Form, CreateProjectStep2Form, CreateProjectStep3Form
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectMembership, UserProfile, Skill, ProjectRequiredSkill
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


@login_required
def create_project_wizard_step1(request):
    if request.method == "POST":
        form = CreateProjectStep1Form(request.POST)
        if form.is_valid():
            request.session['project_step1_data'] = form.cleaned_data
            return redirect('accounts:create_project_wizard_step2')
    else:
        form = CreateProjectStep1Form(request.session.get('project_step1_data'))
        context = {
            'form': form,
            'step': 1,
            'total_steps': 3
        }
        return render(request, 'accounts/create_project_wizard_step1.html', context)
    
    
@login_required
def create_project_wizard_step2(request):
    if request.method == "POST":
        formset = ProjectRequiredSkillFormSet(request.POST)
        if formset.is_valid():
            request.session['project_step2_data'] = []
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    request.session['project_step2_data'].append(form.cleaned_data)
                    return redirect('create_project_wizard_step3')
    else:
         formset = ProjectRequiredSkillFormSet()
         if 'project_step2_data' in request.session:
             formset = ProjectRequiredSkillFormSet(initial=request.session['project_step2_data'])
             
    context = [
        'formset': formset,
        'step': 2,
        'total_steps': 3
    ]
    return render(request, 'accounts/create_project_wizard_step2.html', context)           


@login_required
def create_project_wizard_step3(request):
    if request.method == "POST":
        form = CreateProjectStep3Form(request.POST)
        if form.is_valid():
            request.session['project_step3_data'] = form.cleaned_data
            return redirect('accounts:create_project_wizard_submit')
    else:
        form = CreateProjectStep3Form(request.session.get('project_step3_data'))
        
    context = {
        'form': form,
        'step': 3,
        'total_steps': 3
    }
    return render(request, 'accounts/create_project_wizard_step3.html', context)


@login_required
def create_project_wizard_submit(request):
    step1_data = request.session.get('project_step1_data')
    step2_data = request.session.get('project_step2_data')
    step3_data = request.session.get('project_step3_data')
    
    if step1_data and step2_data and step3_data:
        project = Project.objects.create(
            creator=request.user,
            title=step1_data['title'],
            description=step1_data['description'],
            min_members=step1_data['min_members'],
            max_members=step1_data['max_members'],
            objectives=step3_data.get('objectives', ''),
            goals=step3_data.get('goals', ''),
            start_time=step3_data.get('start_time',),
            operation_days=step3_data.get('operation_days', ''),
            deadline=step3_data.get('deadline'),
        )
        for skill_data in step2_data:
            skill, created = Skill.objects.get_or_create(name=skill_data['skill'])
            ProjectRequiredSkill.objects.create(project=project, skill=skill, proficiency_level=skill_data['proficiency_level'])
            
            # Clear the wizard data fromt the session
        del request.session['project_step1_data']
        del request.session['project_step2_data']
        del request.session['project_step3_data']
            
        return redirect('accounts:project_submitted')
    else:
        # Handle cases where the user might have skipped steps
        messages.error(request, "There was an error submitting your project. Please try again.")
        
        return redirect('accounts:create_project_step1')  