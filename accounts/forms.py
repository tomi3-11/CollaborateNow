from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Project, UserProfile, ProjectRequiredSkill, Task, User

class RegistrationForm(UserCreationForm):
    class Meta:
        model = UserCreationForm.Meta.model
        fields = UserCreationForm.Meta.fields + ('email',)


class LoginForm(AuthenticationForm):
    pass 


class ProjectCreationForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 
            'description', 
            'min_members', 
            'max_members', 
            'required_skills',
            'objectives',
            'goals',
            'start_time',
            'operation_days',
            'deadline',
            'status',
            'project_type',
            'visibility',
            'location',
            ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'required skills': forms.Textarea(attrs={'rows': 3}),
            'objectives': forms.Textarea(attrs={'rows': 3}),
            'goals': forms.Textarea(attrs={'row': 3}),
        }

    
    def clean_min_members(self):
        min_members = self.cleaned_data['min_members']
        if min_members < 4:
            raise forms.ValidationError("Minimum team size must be atleast 4.")
        return min_members
    

    def clean_max_members(self):
        max_members = self.cleaned_data['max_members']
        if max_members > 7:
            raise forms.ValidationError("Maximum team size cannot exceed 7.")
        return max_members
    

    def clean(self):
        cleaned_data = super().clean()
        min_members = cleaned_data.get('min_members')
        max_members = cleaned_data.get('max_members')

        if min_members is not None and max_members is not None and min_members > max_members:
            raise forms.ValidationError("Minimum team size cannot be greater than maximum team size.")
        return cleaned_data


ProjectRequiredSkillFormSet = inlineformset_factory(
    Project,
    ProjectRequiredSkill,
    fields = ('skill', 'proficiency_level'),
    extra=3, # Number of initial empty forms
    can_delete = True
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['skills', 'bio', 'portfolio_url', 'experience_level']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 2}),
            'bio': forms.Textarea(attrs={'rows': 5}),
        }


class CreateProjectStep1Form(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'min_members',
            'max_members'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5})
        }

    def clean_min_members(self):
        min_members = self.cleaned_data['min_members']
        if min_members < 4:
            raise forms.ValidationError("Minimum team size must be atleast 4.")
        return min_members
    
    def clean_max_members(self):
        max_members = self.cleaned_data['max_members']
        if max_members > 7:
            raise forms.ValidationError("Maximum team size cannot exceed 7.")
        return max_members
    
    def clean(self):
        cleaned_data = super().clean()
        min_members = cleaned_data.get('min_members')
        max_members = cleaned_data.get('max_members')

        if min_members is not None and max_members is not None and min_members > max_members:
            raise forms.ValidationError("Minimun team size cannot be greater than the maximum team size.")
        
        return cleaned_data
    

ProjectRequiredSkillFormSet = inlineformset_factory(
    Project,
    ProjectRequiredSkill,
    fields=('skill', 'proficiency_level'),
    extra=3,
    can_delete=True
)


class CreateProjectStep2Form(forms.Form):
    pass # We'll handle the required skills with the formset in the view


class CreateProjectStep3Form(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'objectives',
            'goals',
            'start_time',
            'operation_days',
            'deadline',
        ]
        widgets = {
            'objectives': forms.Textarea(attrs={'rows': 3}),
            'goals': forms.Textarea(attrs={'rows': 3}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'deadline': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
        }
        

# Task form
class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local'
    }), required=False)
    assigned_to = forms.ModelChoiceField(queryset=None, required=False, label="Assign To")
    status = forms.ChoiceField(choices=Task.status_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'due_date', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }
        
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assigned_to'].queryset = project.projectmembership_set.select_related('user').values_list('user', flat=True)
        else:
            self.fields['assigned_to'].queryset = User.objects.none()
        
        if user:
            self.fields['assigned_to'].initial = user


TaskFormSet = inlineformset_factory(
    Project,
    Task,
    form=TaskForm,
    extra=1,
    can_delete=True
)    