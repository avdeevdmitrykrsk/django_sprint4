from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView
)

from .forms import CreateComment, CreatePost, EditUser
from .mixins import (
    PostsFilter, SuccessRedirectToProfile, SuccessRedirectToPost
)
from .models import Category, Comment, Post

User = get_user_model()

NUMBER_OF_POSTS = 10


class IndexListView(PostsFilter):
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        posts = self.get_filtred_posts(Post)
        return posts


class ProfileDetailView(PostsFilter):
    template_name = 'blog/profile.html'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        posts = Post.objects.filter(author__username=self.kwargs['username'])
        if self.request.user.username == self.kwargs['username']:
            return posts.annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        return self.get_filtred_posts(Post)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = profile
        return context


class ProfileEditView(LoginRequiredMixin, SuccessRedirectToProfile, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = EditUser
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return super().get_context_data(**kwargs)


class PostCreateView(LoginRequiredMixin, SuccessRedirectToProfile, CreateView):
    model = Post
    form_class = CreatePost
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, SuccessRedirectToPost, UpdateView):
    model = Post
    form_class = CreatePost
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, SuccessRedirectToProfile, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    slug_url_kwarg = 'post_id'
    slug_field = 'id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context['form'] = CreatePost(instance=post)
        return context


class PostDetailView(ListView):
    model = Comment
    template_name = 'blog/detail.html'
    paginate_by = NUMBER_OF_POSTS
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(Post.objects.filter(
            category__is_published=True,
            is_published=True,
            pub_date__lte=timezone.now()
        ), pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateComment()
        context['post'] = self.get_object()
        context['comments'] = Comment.objects.filter(
            post__id=self.kwargs['post_id']
        )
        return context


class CommentCreateView(LoginRequiredMixin, SuccessRedirectToPost, CreateView):
    model = Comment
    form_class = CreateComment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditView(LoginRequiredMixin, SuccessRedirectToPost, UpdateView):
    model = Comment
    form_class = CreateComment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if self.request.user != comment.author:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_id'] = Comment.objects.filter(
            pk=self.kwargs['comment_id']
        )
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, SuccessRedirectToPost, DeleteView):
    model = Comment
    form_class = CreateComment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if self.request.user != comment.author:
            return redirect(
                reverse(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        context['comment_id'] = Comment.objects.filter(
            pk=self.kwargs['comment_id']
        )
        return context


class CategoryPostView(PostsFilter):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = NUMBER_OF_POSTS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.get_filtred_posts(Post).filter(
            category__slug=self.kwargs['category_slug'],
        )
        paginator = Paginator(categories, NUMBER_OF_POSTS)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['category'] = get_object_or_404(
            Category.objects.values(
                'title', 'description'
            ).filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return context
