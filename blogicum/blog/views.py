from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CreateCommentForm, CreatePost, DeletePost, EditUser
from .models import Category, Comment, Post

User = get_user_model()


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class ProfileDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User, username=self.kwargs['username']
        )
        if self.request.user.is_authenticated:
            posts = Post.objects.filter(
                is_published=True,
                category__is_published=True,
                author__username=self.kwargs['username']
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
            paginator = Paginator(posts, 10)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj
        context['profile'] = profile
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = EditUser
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        print(self.request.user.username)
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return super().get_context_data(**kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePost
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = CreatePost
    template_name = 'blog/create.html'
    slug_url_kwarg = 'post_id'
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = Post.objects.filter(pk=self.kwargs['post_id'])
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    slug_url_kwarg = 'post_id'
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_values = Post.objects.get(pk=self.kwargs['post_id'])
        context['form'] = DeletePost(instance=post_values)
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = Comment.objects.filter(
            post__id=self.kwargs['post_id']
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_id'] = Comment.objects.filter(
            pk=self.kwargs['comment_id']
        )
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        context['comment_id'] = Comment.objects.filter(
            pk=self.kwargs['comment_id']
        )
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CategoryPostView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Post.objects.all().filter(
            category__slug=self.kwargs['category_slug']
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        paginator = Paginator(categories, 10)
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
