from django.contrib import admin
from .models import Idea, DevTool, IdeaStar


@admin.register(DevTool)
class DevToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'kind', 'created_at']
    list_filter = ['kind', 'created_at']
    search_fields = ['name', 'content']
    ordering = ['-created_at']


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'devtool', 'interest', 'created_at']
    list_filter = ['devtool', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
    
    def get_star_count(self, obj):
        return obj.stars.count()
    get_star_count.short_description = '찜 개수'


@admin.register(IdeaStar)
class IdeaStarAdmin(admin.ModelAdmin):
    list_display = ['user', 'idea', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'idea__title']
    ordering = ['-created_at']