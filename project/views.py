from rest_framework.generics import ListCreateAPIView,CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Project
from rest_framework.response import Response
from django.db.models import Q
from .serializers import ProjectSerializer
from rest_framework import status


class ProjectCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        projects = Project.objects.filter(Q(owner=self.request.user) | Q(members=self.request.user))
        return projects

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
