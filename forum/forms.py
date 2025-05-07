from .models import ForumPost, ForumTopic
from django.contrib.auth.models import User
from django import forms

# Create your forms here

class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ['title', 'category']


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }


class EditPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3})
        }
        