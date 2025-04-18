from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from . import models
from .models import Project
from rest_framework.response import Response
from django.db.models import Q
from .serializers import ProjectSerializer
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample


@extend_schema_view(
    post=extend_schema(
        summary="Create a new project",
        description="Creates a new project with the authenticated user as the owner",
        tags=["Projects"],
        responses={201: ProjectSerializer},
        examples=[
            OpenApiExample(
                'Project Example',
                value={
                    'name': 'Sample Project',
                    'description': 'This is an example project',
                },
                request_only=True,
            ),
        ],
        auth=["Token"],
    )
)
class ProjectCreateView(CreateAPIView):
    """
    Creates a new project for the authenticated user.

    The authenticated user is automatically set as the project owner.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Returns projects accessible to the current user.

        Includes projects where the user is either the owner or a member.

        Returns:
            QuerySet: Filtered project queryset
        """
        projects = Project.objects.filter(Q(owner=self.request.user) | Q(members=self.request.user))
        return projects

    def perform_create(self, serializer):
        """
        Saves a new project with the current user as owner.

        Args:
            serializer: The validated project serializer
        """
        serializer.save(owner=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve project details",
        description="Get details for a specific project the user has access to",
        tags=["Projects"],
        responses={200: ProjectSerializer},
        auth=["Token"],
    ),
    put=extend_schema(
        summary="Update a project",
        description="Update a project (only available to the project owner)",
        tags=["Projects"],
        responses={
            200: ProjectSerializer,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        auth=["Token"],
    ),
    patch=extend_schema(
        summary="Partially update a project",
        description="Partially update a project (only available to the project owner)",
        tags=["Projects"],
        responses={
            200: ProjectSerializer,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        auth=["Token"],
    ),
    delete=extend_schema(
        summary="Delete a project",
        description="Delete a project (only available to the project owner)",
        tags=["Projects"],
        responses={
            204: None,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        auth=["Token"],
    ),
)
class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project instance.

    Access is restricted to users who either own the project or are members.
    Update and delete operations are further restricted to the project owner only.
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Returns projects accessible to the current user.

        Includes projects where the user is either the owner or a member.

        Returns:
            QuerySet: Filtered project queryset
        """
        projects = Project.objects.filter(Q(owner=self.request.user) | Q(members=self.request.user))
        return projects

    def perform_update(self, serializer):
        """
        Updates a project after verifying owner permissions.

        Only the project owner can update a project. Returns a 403 Forbidden
        response if the user is not the owner.

        Args:
            serializer: The validated project serializer

        Returns:
            Response: 403 Forbidden response if permission check fails
        """
        project = self.get_object()
        if project.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """
        Deletes a project after verifying owner permissions.

        Only the project owner can delete a project. Returns a 403 Forbidden
        response if the user is not the owner.

        Args:
            instance: The project instance to delete

        Returns:
            Response: 403 Forbidden response if permission check fails
        """
        if instance.owner != self.request.user:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()


@extend_schema(
    tags=["Project Members"],
    summary="Manage project members",
    description="Add or remove members from a project. Only the project owner can perform these actions.",
    methods=["PATCH"],
    parameters=[
        OpenApiParameter(
            name='member_id',
            location=OpenApiParameter.QUERY,
            description='ID of the user to add/remove',
            required=True,
            type=int
        ),
        OpenApiParameter(
            name='action',
            location=OpenApiParameter.QUERY,
            description='Action to perform',
            required=True,
            type=str,
            enum=['add', 'remove']
        ),
    ],
    responses={
        200: {"type": "object", "properties": {"detail": {"type": "string"}}},
        400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}},
    },
    auth=["Token"],
)
class ProjectMemberView(UpdateAPIView):
    """
    API endpoint for managing project members.

    Allows project owners to add or remove members from their projects.
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Returns projects owned by the current user.

        Only project owners can manage project members.

        Returns:
            QuerySet: Projects owned by the user
        """
        return Project.objects.filter(owner=self.request.user)

    def patch(self, request, *args, **kwargs):
        """
        Adds or removes a user as a project member.

        Args:
            request: HTTP request object containing member_id and action
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Query Parameters:
            member_id (int): ID of the user to add/remove
            action (str): Action to perform ('add' or 'remove')

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
