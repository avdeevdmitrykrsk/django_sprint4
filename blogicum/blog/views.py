from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CreatePost, EditUser
from .models import Category, Post

User = get_user_model()

def posts_queryset_get() -> QuerySet:
    """Функция получает необходимый(ые)/пост(ы) и передает во view-функции."""
    return Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lte=now(),
        is_published=True,
        category__is_published=True
    )


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10


class ProfileDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User, username=self.kwargs['username']
        )
        context['profile'] = profile
        context['page_obj'] = profile.posts.all()
        return context


class ProfileEditView(UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = EditUser
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        print(self.request.user.username)
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return super().get_context_data(**kwargs)


class PostCreateView(CreateView):
    model = Post
    form_class = CreatePost
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """View-функция рендерит страницу с описанием конкретного товара."""
    template_name: str = 'blog/detail.html'
    post: object = get_object_or_404(posts_queryset_get().filter(pk=post_id))
    context: dict = {
        'post': post
    }
    return render(request, template_name, context)


class CategoryPostView(ListView):
    model = Post
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = Post.objects.all().filter(category__slug=self.kwargs['category_slug'])
        context['category'] = get_object_or_404(
            Category.objects.all().filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return context
