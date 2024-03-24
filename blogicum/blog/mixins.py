from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView
)


class PostsFilter(ListView):
    def get_filtred_posts(self, model):
        return model.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


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
