from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class CreatePost(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'format': '%Y-%m-%d %H:%M'
                }
            )
        }


class CreateComment(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ('author', 'post', 'is_published')


class EditUser(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
