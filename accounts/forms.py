from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Project, UserProfile

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
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['skills', 'bio', 'portfolio_url', 'experience_level']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 2}),
            'bio': forms.Textarea(attrs={'rows': 5}),
        }
    