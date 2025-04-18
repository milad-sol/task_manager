from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from . import models
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
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class ProjectMemberView(UpdateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def patch(self, request, *args, **kwargs):
        project = self.get_object()
        member_id =request.data.get('member_id')
        action = request.data.get('action')

        try:
            user = project.members.get(id=member_id)
            if action == 'add':
                project.members.add(user)
            elif action == 'remove':
                project.members.remove(user)
            else:
                return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Member action successful.'}, status=status.HTTP_200_OK)
        except models.User.DoesNotExist:
            return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
