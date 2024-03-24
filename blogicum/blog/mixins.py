from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import ListView

from .forms import CreateComment, CreatePost
from .models import Comment, Post


class SuccessRedirectToProfile:
    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class SuccessRedirectToPost:
    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostsFilter(ListView):
    def get_filtred_posts(self, model):
        return model.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_annotate(self, queryset):
        return queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class PostMixin(LoginRequiredMixin):
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


class CommentMixin(LoginRequiredMixin):
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
