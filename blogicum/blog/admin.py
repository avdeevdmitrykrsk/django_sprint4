from django.contrib import admin

from .models import Category, Location, Post

admin.site.empty_value_display = 'Не задано'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'category'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)