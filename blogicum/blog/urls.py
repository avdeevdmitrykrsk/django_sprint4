from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path(
        'profile/<slug:username>/', views.ProfileDetailView.as_view(), name='profile'
    ),
    path('profile/edit/<slug:username>', views.ProfileEditView.as_view(), name='edit_profile'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        '<slug:category_slug>/',
        views.CategoryPostView.as_view(), name='category_posts',
    ),
]
