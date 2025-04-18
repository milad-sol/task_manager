from django.contrib import admin
from .models import Task


# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'project', 'status','priority', 'created_by', 'created_at')
    list_filter = ('project', 'status', 'created_by', 'created_at', 'updated_at', 'priority')
    search_fields = ('title', 'description')

