from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView
)

from .forms import CreateComment, CreatePost, EditUser
from .mixins import (
    PostsFilter,
    SuccessRedirectToProfileMixin,
    SuccessRedirectToPostMixin,
    PostMixin,
    CommentMixin,
)
from .models import Category, Comment, Post

User = get_user_model()

NUMBER_OF_POSTS = 10


class IndexListView(PostsFilter, ListView):
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        return self.get_annotate(self.get_filtred_posts(Post.objects))


class ProfileDetailView(PostsFilter, ListView):
    template_name = 'blog/profile.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        posts = Post.objects.filter(author__username=self.kwargs['username'])
        if self.request.user.username == self.kwargs['username']:
            return self.get_annotate(posts)
        return self.get_annotate(
            self.get_filtred_posts(posts)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = profile
        return context


class ProfileEditView(
    LoginRequiredMixin,
    SuccessRedirectToProfileMixin,
    UpdateView
):
    model = User
    template_name = 'blog/user.html'
    form_class = EditUser
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return super().get_context_data(**kwargs)


class PostCreateView(
    LoginRequiredMixin,
    SuccessRedirectToProfileMixin,
    CreateView
):
    model = Post
    form_class = CreatePost
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(
    LoginRequiredMixin,
    PostMixin,
    SuccessRedirectToPostMixin,
    UpdateView
):
    pass


class PostDeleteView(
    LoginRequiredMixin,
    PostMixin,
    SuccessRedirectToProfileMixin,
    DeleteView
):
    pass


class PostDetailView(PostsFilter, ListView):
    model = Comment
    template_name = 'blog/detail.html'
    paginate_by = NUMBER_OF_POSTS
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            self.get_filtred_posts(Post.objects),
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateComment()
        context['post'] = self.get_object()
        context['comments'] = Comment.objects.filter(
            post__id=self.kwargs['post_id']
        )
        return context


class CommentCreateView(
    LoginRequiredMixin,
    SuccessRedirectToPostMixin,
    CreateView
):
    model = Comment
    form_class = CreateComment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditView(
    PostsFilter,
    LoginRequiredMixin,
    CommentMixin,
    SuccessRedirectToPostMixin,
    UpdateView
):
    pass


class CommentDeleteView(
    LoginRequiredMixin,
    CommentMixin,
    SuccessRedirectToPostMixin,
    DeleteView
):
    pass


class CategoryPostView(PostsFilter, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        categories = self.get_filtred_posts(Post.objects).filter(
            category__slug=self.kwargs['category_slug'],
        )
        return categories
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.values(
                'title', 'description'
            ).filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return context
