from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class CreatePost(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class DeletePost(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('image', 'pub_date', 'location', 'title', 'text')


class EditUser(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
