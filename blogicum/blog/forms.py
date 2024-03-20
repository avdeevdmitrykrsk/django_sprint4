from django import forms
from django.contrib.auth import get_user_model

from .models import Post

User = get_user_model()


class CreatePost(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class EditUser(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
