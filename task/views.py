from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db import models
from rest_framework import filters
from .models import Task
from .serializers import TaskSerializer

from django_filters.rest_framework import DjangoFilterBackend


class TaskListCreateView(generics.ListCreateAPIView):
    """
    API view that allows users to list and create tasks.

    GET: Returns a list of tasks that the user has access to, which includes:
        - Tasks from projects the user owns
        - Tasks from projects where the user is a member
        - Tasks assigned to the user

    POST: Creates a new task with the authenticated user as the creator.

    Filtering:
        - status: Filter by task status (todo, in_progress, done)
        - priority: Filter by task priority (low, medium, high)
        - due_date: Filter by task due date
        - project: Filter by associated project
        - assigned_to: Filter by assigned user

    Ordering:
        - due_date: Order by task due date
        - priority: Order by task priority
        - created_at: Order by task creation date
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = ['status', 'priority', 'due_date', 'project', 'assigned_to']
    ordering_fields = ['due_date', 'priority', 'created_at']

    def get_queryset(self):
        """
        Returns tasks filtered to only show those the user has access to.
        This includes tasks from projects the user owns or is a member of,
        or tasks directly assigned to the user.
        """
        return Task.objects.filter(
            models.Q(project__owner=self.request.user) |
            models.Q(project__members=self.request.user) |
            models.Q(assigned_to=self.request.user))

    def perform_create(self, serializer):
        """
        Sets the authenticated user as the creator when saving a new task.

        Args:
            serializer: The validated task serializer instance
        """
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view that allows users to retrieve, update, and delete a specific task.

    GET: Retrieves the detail of a specific task
    PUT/PATCH: Updates a specific task
    DELETE: Deletes a specific task

    Permissions:
        - Users can only access tasks from projects they own or are members of,
          or tasks assigned to them.
        - Only the project owner or the task creator can update or delete tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns tasks filtered to only show those the user has access to.
        This includes tasks from projects the user owns or is a member of,
        or tasks directly assigned to the user.

        The distinct() method is used to eliminate duplicate results.
        """
        return Task.objects.filter(
            models.Q(project__owner=self.request.user) |
            models.Q(project__members=self.request.user) |
            models.Q(assigned_to=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        """
        Updates a task after checking if the user has permission.

        Only the project owner or the task creator can update a task.
        Raises PermissionDenied if the user doesn't have permission.

        Args:
            serializer: The validated task serializer instance

        Raises:
            PermissionDenied: If the user doesn't have permission to update the task
        """
        task = self.get_object()

        if not (task.project.owner == self.request.user or task.created_by == self.request.user):
            raise PermissionDenied("You don't have permission to update this task")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Deletes a task after checking if the user has permission.

        Only the project owner or the task creator can delete a task.
        Raises PermissionDenied if the user doesn't have permission.

        Args:
            instance: The task instance to be deleted

        Raises:
            PermissionDenied: If the user doesn't have permission to delete the task
        """
        if not (instance.project.owner == self.request.user or instance.created_by == self.request.user):
            raise PermissionDenied("You don't have permission to delete this task")
        instance.delete()
