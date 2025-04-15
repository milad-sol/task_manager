from django.urls import path
from . import views

app_name = 'project'
urlpatterns = [
    path('', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),

]
