from django.urls import path
from . import views


app_name = 'task'
urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task_list_create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),


]
