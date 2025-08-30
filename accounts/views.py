from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, LoginForm, ProjectCreationForm, UserProfileForm, ProjectRequiredSkillFormSet, CreateProjectStep1Form, CreateProjectStep2Form, CreateProjectStep3Form, TaskForm, ProjectEditForm, ProjectFileUploadForm
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectMembership, UserProfile, Skill, ProjectRequiredSkill
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.dateparse import parse_datetime, parse_date
from datetime import datetime
from .models import Skill, Notification, Whiteboard, Task, ProjectFile
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import markdown2
from django.http import FileResponse


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('accounts:login_view') # Redirect to login page after registration
    else:
        form = RegistrationForm()
    
    context = { 'form': form}
    return render(request, 'accounts/register.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
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


@login_required
def edit_project(request, project_id):
    project  = get_object_or_404(Project, id=project_id)
    
    # Add permission checks here if needed (e.g., only creator can edit )
    if project.creator != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this project.")
        return redirect('accounts:project_detail', project_id=project_id)
    
    if request.method == "POST":
        form = ProjectEditForm(request.POST, instance=project) # Passing the existing project instance
        if form.is_valid():
            form.save()
            messages.success(request, f"Project '{project.title}' updated successfully.")
            return redirect('accounts:project_detail', project_id=project_id)
        
    else:
        form = ProjectEditForm(instance=project) # Passing existing project instance
            
    context = {
        'form': form,
        'project': project,
    }
        
    return render(request, 'accounts/edit_project.html', context)


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
    
    # Checks if a user is a member
    # if project.projectmembership_set.filter(user=request.user, project=project).exist():
    #     messages.info(request, "You are already a member of this project.")
    #     return redirect('accounts:project_detail', project_id=project_id)
    
    # Informs user if project reaches maximum number of members of FULL
    if project.current_members >= project.max_members:
        messages.error(request, "This project is full.")
        return redirect('accounts:project_list')
    
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
    # return redirect('accounts:project_list')

    # Create a notification for the project creator
    if request.user != project.creator:
        Notification.objects.create(
            user=project.creator,
            notification_type='new_member',
            message=f"{request.user.username} has joined your project '{project.title}'."
        )
    
    return redirect('accounts:project_detail', project_id=project_id)


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
    members = project.projectmembership_set.all()
    
    is_member = False
    if request.user.is_authenticated:
        is_member = project.projectmembership_set.filter(user=request.user).exists()
        
    whiteboard, created = Whiteboard.objects.get_or_create(project=project) # Get or create whiteboard
    tasks = Task.objects.filter(project=project).order_by('-created_at') # Fetch tasks from the project
    files = ProjectFile.objects.filter(project=project).order_by('-uploaded_at') # Fetch project files
    
    # Adds status_choices for rendering dropdowns
    status_choices = Task._meta.get_field('status').choices
    
    if request.method == 'POST':
        task_form = TaskForm(request.POST, project=project, user=request.user)
        file_form = ProjectFileUploadForm(request.POST, request.FILES) # Initialize file form with POST data and files
        if task_form.is_valid():
            new_task = task_form.save(commit=False)
            new_task.project = project
            new_task.created_by = request.user
            new_task.save()
            
            messages.success(request, f"Task '{new_task.title}' created successfully.")
            return redirect('accounts:project_detail', project_id=project_id)
        elif file_form.is_valid():
            new_file = file_form.save(commit=False)
            new_file.project = project
            new_file.uploaded_by = request.user
            new_file.save()
            messages.success(request, f"File '{new_file.filename()}' uploaded successfully.")
            return redirect('accounts:project_detail', project_id=project_id)
    else:
        task_form = TaskForm(project=project, user=request.user)
        file_form = ProjectFileUploadForm() # Initialize and empty file upload form for GET requests
    context = {
        'project': project,
        "Members":  members,
        "is_member": is_member,
        "whiteboard_content": whiteboard.content,
        "tasks": tasks, # passes the tasks to the template
        "task_form": task_form, # passes the task creation form to the template
        "status_choices": status_choices,
        "file_form": file_form, # passing the file upload form to the template
        "project_files": files, # Passing the list of project files to the templates
    }
    return render(request, "accounts/project_detail.html", context)


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
            step2_data = []  # Temporarily hold safe session data
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    skill_instance = form.cleaned_data['skill']
                    proficiency = form.cleaned_data['proficiency_level']

                    # Only store primitive values (skill_id and proficiency)
                    step2_data.append({
                        'skill_id': skill_instance.id,
                        'proficiency_level': proficiency
                    })
            
            # Store cleaned and serializable data in session
            request.session['project_step2_data'] = step2_data

            return redirect('accounts:create_project_wizard_step3')
    else:
        # Repopulate the formset from session if returning to this step
        if 'project_step2_data' in request.session:
            initial_data = []
            for entry in request.session['project_step2_data']:
                try:
                    skill = Skill.objects.get(id=entry['skill_id'])
                    initial_data.append({
                        'skill': skill,
                        'proficiency_level': entry['proficiency_level']
                    })
                except Skill.DoesNotExist:
                    continue
            formset = ProjectRequiredSkillFormSet(initial=initial_data)
        else:
            formset = ProjectRequiredSkillFormSet()

    context = {
        'formset': formset,
        'step': 2,
        'total_steps': 3
    }
    return render(request, 'accounts/create_project_wizard_step2.html', context)



@login_required
def create_project_wizard_step3(request):
    if request.method == "POST":
        form = CreateProjectStep3Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Convert datetime/date to strings for session storage
            request.session['project_step3_data'] = {
                'objectives': cd.get('objectives', ''),
                'goals': cd.get('goals', ''),
                'start_time': cd['start_time'].isoformat() if cd.get('start_time') else '',
                'operation_days': cd.get('operation_days', ''),
                'deadline': cd['deadline'].isoformat() if cd.get('deadline') else '',
            }
            return redirect('accounts:create_project_wizard_submit')
    else:
        initial = request.session.get('project_step3_data')
        if initial:
            if 'start_time' in initial and initial['start_time']:
                initial['start_time'] = parse_datetime(initial['start_time'])
            if 'deadline' in initial and initial['deadline']:
                initial['deadline'] = parse_date(initial['deadline'])

        form = CreateProjectStep3Form(initial=initial)

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
        try:
            project = Project.objects.create(
                creator=request.user,
                title=step1_data['title'],
                description=step1_data['description'],
                min_members=step1_data['min_members'],
                max_members=step1_data['max_members'],
                objectives=step3_data.get('objectives', ''),
                goals=step3_data.get('goals', ''),
                start_time=datetime.fromisoformat(step3_data.get('start_time')) if step3_data.get('start_time') else None,
                operation_days=step3_data.get('operation_days', ''),
                deadline=datetime.fromisoformat(step3_data.get('deadline')) if step3_data.get('deadline') else None,
            )

            for skill_data in step2_data:
                skill = Skill.objects.get(id=skill_data['skill_id'])
                ProjectRequiredSkill.objects.create(
                    project=project,
                    skill=skill,
                    proficiency_level=skill_data['proficiency_level']
                )

            # Clear wizard session data
            request.session.pop('project_step1_data', None)
            request.session.pop('project_step2_data', None)
            request.session.pop('project_step3_data', None)

            return redirect('accounts:project_submitted')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('accounts:create_project_wizard_step1')

    messages.error(request, "There was an error submitting your project. Please try again.")
    return redirect('accounts:create_project_wizard_step1')


@login_required
def leave_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    try:
        membership = ProjectMembership.objects.get(user=request.user, project=project)
        membership.delete()
        project.current_members = max(0, project.current_members - 1) # Ensure count doesn't go below zero
        project.save()
        messages.success(request, f"You have successfully left the project '{project.title}.")
        return redirect('accounts:project_detail', project_id=project_id)
    except ProjectMembership.DoesNotExist:
        messages.error(request, "You are not a member of this project.")
        return redirect('accounts:project_detail', project_id=project_id)
    
    
@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('accounts:profile') # redirect to profile 


@login_required
@require_POST
def save_whiteboard(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        whiteboard, created = Whiteboard.objects.get_or_create(project=project)
        whiteboard.content = content
        whiteboard.save()
        
        # Adding a success message after the whiteboard is saved
        # messages.success(request, "Whiteboard saved successfully!")
        
        return JsonResponse({'success': True, "message": "Whiteboard saved successfully!"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    
@login_required
@require_POST
def render_whiteboard_content(request):
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        rendered_content = markdown2.markdown(
            content, 
            extras=['fenced-code-blocks', 'tables', 'break-on-newline']
        )
        
        return JsonResponse({'rendered_content': rendered_content})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 
    

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    
    # Ensure the user is a member of the project or the project creator
    if not ProjectMembership.objects.filter(user=request.user, project=project).exists() and project.creator != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this task.")
        return redirect('accounts:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=project, user=task.assigned_to)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, f"Task '{updated_task.title}' updated successfully.")
            return redirect('accounts:project_detail', project_id=project.id)
        
    else:
        form = TaskForm(instance=task, project=project, user=task.assigned_to)
    
    context = {
        'form': form,
        'task': task,
        'project': project
    }
    
    return render(request, 'accounts/edit_task.html', context)


@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    
    # Ensure the user has permission to delete tha task (e.g., creator or admin)
    if task.created_by != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this task.")
        return redirect('accounts:project_detail', project_id=project.id)
    
    task.delete()
    messages.success(request, f"Task '{task.title}' deleted successfully.")
    return redirect('accounts:project_detail', project_id=project.id)


@login_required
@require_POST
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    
    # Ensure the user is a member of the project or the project creator
    if not ProjectMembership.objects.filter(user=request.user, project=project).exists() and project.creator != request.user and not request.user.is_staff:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Permission denied',
                
            }, status=403
        )
        
    new_status = request.POST.get('status')
    if new_status and new_status in dict(Task.status_choices):
        task.status = new_status
        task.save()
        return JsonResponse({
            'status': 'success',
            'new_status_display': task.get_status_display(),
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid status provided',
        }, status=400)
        
        
# File download view
@login_required
def download_file(request, file_id):
    project_file = get_object_or_404(ProjectFile, id=file_id)
    project = project_file.project
    
    # Ensure the user is a member of the project or the project creator
    if not ProjectMembership.objects.filter(user=request.user, project=project).exists() and project.creator != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to download this file.")
        return redirect('accounts:project_detail', project_id=project.id)
    
    file_path = project_file.file.path
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{project_file.filename()}"'
    return response
