from rest_framework.generics import ListCreateAPIView,CreateAPIView,RetrieveUpdateDestroyAPIView
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


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        projects = Project.objects.filter(Q(owner=self.request.user) | Q(members=self.request.user))
        return projects
    def perform_update(self, serializer):
        project = self.get_object()
        if project.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
