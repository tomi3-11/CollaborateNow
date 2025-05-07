from django.contrib import admin
from .models import ForumPost, ForumTopic, ForumCategory

# Register your models here.
admin.site.register(ForumCategory)


class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'category')
    list_filter = ('category',)

admin.site.register(ForumTopic, ForumTopicAdmin)


class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('author', 'topic', 'created_at')

admin.site.register(ForumPost, ForumPostAdmin)
