from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from . import models
from .models import Project
from rest_framework.response import Response
from django.db.models import Q
from .serializers import ProjectSerializer
from rest_framework import status


class ProjectCreateView(CreateAPIView):
    """
    API view that allows authenticated users to create new projects.

    POST: Creates a new project with the authenticated user set as the owner.

    Permissions:
        - User must be authenticated to create a project.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Returns projects filtered to only show those the user has access to.
        This includes projects the user owns or is a member of.

        Returns:
            QuerySet: Filtered projects the user can access
        """
        projects = Project.objects.filter(Q(owner=self.request.user) | Q(members=self.request.user))
        return projects

    def perform_create(self, serializer):
        """
        Sets the authenticated user as the owner when saving a new project.

        Args:
            serializer: The validated project serializer instance
        """
        serializer.save(owner=self.request.user)


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    """
    API view that allows users to retrieve, update, and delete specific projects.

    GET: Retrieves the detail of a specific project
    PUT/PATCH: Updates a specific project (only project owner can perform this action)
    DELETE: Deletes a specific project (only project owner can perform this action)

    Permissions:
        - User must be authenticated
        - User must be the owner or a member of the project to view it
        - Only the project owner can update or delete the project
    """
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Returns projects filtered to only show those the user has access to.
        This includes projects the user owns or is a member of.

        Returns:
            QuerySet: Filtered projects the user can access
        """
        projects = Project.objects.filter(Q(owner=self.request.user) | Q(members=self.request.user))
        return projects

    def perform_update(self, serializer):
        """
        Updates a project after checking if the user has permission.

        Only the project owner can update a project. Returns a 403 Forbidden
        response if the user doesn't have permission.

        Args:
            serializer: The validated project serializer instance

        Returns:
            Response: 403 Forbidden if the user doesn't have permission
        """
        project = self.get_object()
        if project.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """
        Deletes a project after checking if the user has permission.

        Only the project owner can delete a project. Returns a 403 Forbidden
        response if the user doesn't have permission.

        Args:
            instance: The project instance to be deleted

        Returns:
            Response: 403 Forbidden if the user doesn't have permission
        """
        if instance.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class ProjectMemberView(UpdateAPIView):
    """
    API view that allows project owners to manage project members.

    PATCH: Adds or removes a user as a member of the project

    Request Parameters:
        - member_id: The ID of the user to add or remove
        - action: The action to perform ('add' or 'remove')

    Permissions:
        - User must be authenticated
        - Only the project owner can manage project members
    """
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Returns projects filtered to only show those the user owns.
        Only project owners can manage members.

        Returns:
            QuerySet: Projects owned by the user
        """
        return Project.objects.filter(owner=self.request.user)

    def patch(self, request, *args, **kwargs):
        """
        Adds or removes a user as a member of the project.

        Args:
            request: The HTTP request
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Request Parameters:
            - member_id: The ID of the user to add or remove
            - action: The action to perform ('add' or 'remove')

        Returns:
            Response:
                - 200 OK if the action was successful
                - 400 Bad Request if the action is invalid
                - 404 Not Found if the user doesn't exist
        """
        project = self.get_object()
        member_id = request.data.get('member_id')
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