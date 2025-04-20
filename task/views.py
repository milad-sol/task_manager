from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Task
from .serializers import TaskSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample


@extend_schema_view(
    get=extend_schema(
        summary="List all accessible tasks",
        description="Returns a list of all tasks that the user has access to through their projects",
        tags=["Tasks"],
        parameters=[
            OpenApiParameter(
                name='project',
                location=OpenApiParameter.QUERY,
                description='Filter tasks by project ID',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='status',
                location=OpenApiParameter.QUERY,
                description='Filter tasks by status',
                required=False,
                type=str,
                enum=['todo', 'in_progress', 'done']
            ),
            OpenApiParameter(
                name='priority',
                location=OpenApiParameter.QUERY,
                description='Filter tasks by priority',
                required=False,
                type=str,
                enum=['low', 'medium', 'high']
            ),
        ],
        responses={200: TaskSerializer(many=True)},
        auth=["Token"],
    ),
    post=extend_schema(
        summary="Create a new task",
        description="Creates a new task within a project. User must have access to the project.",
        tags=["Tasks"],
        responses={
            201: TaskSerializer,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        examples=[
            OpenApiExample(
                'Task Example',
                value={
                    'title': 'Implement API Documentation',
                    'description': 'Add Swagger documentation to all API endpoints',
                    'status': 'todo',
                    'priority': 'high',
                    'due_date': '2023-12-31',
                    'project': 1,
                    'assigned_to': None
                },
                request_only=True,
            ),
        ],
        auth=["Token"],
    )
)
class TaskListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating tasks.

    GET: Returns a list of tasks that the user has access to through their projects.
    POST: Creates a new task in a project that the user has access to.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Returns tasks accessible to the current user.

        Tasks are filtered by projects where the user is either the owner or a member.
        Additional filtering can be applied through query parameters:
        - project: Filter by project ID
        - status: Filter by task status (todo, in_progress, done)
        - priority: Filter by task priority (low, medium, high)

        Returns:
            QuerySet: Filtered task queryset
        """
        user = self.request.user
        if user.is_superuser:
            return Task.objects.all()
        queryset = Task.objects.filter(
            Q(project__owner=user) | Q(project__members=user) | Q(assigned_to=user)
        ).distinct()

        # Apply filters from query parameters
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def perform_create(self, serializer):
        """
        Creates a new task after verifying project access.

        The authenticated user is set as the creator. The user must have access
        to the project (as owner or member) to create a task in it.

        Args:
            serializer: The validated task serializer

        Raises:
            PermissionDenied: If the user doesn't have access to the project
        """
        project = serializer.validated_data.get('project')
        user = self.request.user

        # Check if user has access to the project
        if not user.is_superuser:
            if not (project.owner == user or project.members.filter(id=user.id).exists()):
                return Response(
                    {'detail': 'You do not have permission to create tasks in this project.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer.save(created_by=user)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve task details",
        description="Get details for a specific task the user has access to",
        tags=["Tasks"],
        responses={
            200: TaskSerializer,
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        auth=["Token"],
    ),
    put=extend_schema(
        summary="Update a task",
        description="Update all fields of a task. User must have appropriate access.",
        tags=["Tasks"],
        responses={
            200: TaskSerializer,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        auth=["Token"],
    ),
    patch=extend_schema(
        summary="Partially update a task",
        description="Update specific fields of a task. User must have appropriate access.",
        tags=["Tasks"],
        responses={
            200: TaskSerializer,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        auth=["Token"],
    ),
    delete=extend_schema(
        summary="Delete a task",
        description="Delete a task. Only available to project owners or task creators.",
        tags=["Tasks"],
        responses={
            204: None,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        auth=["Token"],
    ),
)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting tasks.

    Access is restricted to users who have permission to access the related project.
    Edit/delete operations are further restricted based on user role.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Returns tasks accessible to the current user.

        Tasks are filtered by projects where the user is either the owner or a member,
        or tasks directly assigned to the user.

        Returns:
            QuerySet: Filtered task queryset
        """
        user = self.request.user
        if user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(
            Q(project__owner=user) | Q(project__members=user) | Q(assigned_to=user)
        ).distinct()

    def perform_update(self, serializer):
        """
        Updates a task after verifying permissions.

        Permission checks:
        - Project owners can update any task in their projects
        - Task creators can update tasks they created
        - Assigned users can update status of tasks assigned to them

        Args:
            serializer: The validated task serializer

        Returns:
            Response: 403 Forbidden response if permission check fails
        """
        task = self.get_object()
        user = self.request.user

        # Project owner can do anything
        if task.project.owner == user:
            return serializer.save()

        # Task creator can update the task
        if task.created_by == user:
            return serializer.save()

        # Task assignee can update status only
        if task.assigned_to == user and len(serializer.validated_data) == 1 and 'status' in serializer.validated_data:
            serializer.save()
            return Response({'detail': 'Task status updated successfully.'}, status=status.HTTP_200_OK)

        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )

    def perform_destroy(self, instance):
        if self.request.user == instance.project.owner:
            instance.delete()
            return Response(
                {"message": "Project deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"message": "You do not have permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN
            )


@extend_schema(
    tags=["Task Assignments"],
    summary="Assign or unassign a task",
    description="Assign a task to a user or remove an assignment. Only project owners, task creators, or currently assigned users can perform this action.",
    methods=["PATCH"],
    parameters=[
        OpenApiParameter(
            name='user_id',
            location=OpenApiParameter.QUERY,
            description='ID of the user to assign (or null to unassign)',
            required=False,
            type=int
        ),
    ],
    request=None,
    responses={
        200: TaskSerializer,
        400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        403: {"type": "object", "properties": {"detail": {"type": "string"}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}},
    },
    auth=["Token"],
)
class TaskAssignView(generics.UpdateAPIView):
    """
    API endpoint for assigning or unassigning tasks.

    Allows project owners, task creators, or currently assigned users to:
    - Assign the task to a project member
    - Unassign the task (set assigned_to to null)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Returns tasks accessible to the current user for assignment.

        Tasks are filtered by:
        - Tasks in projects owned by the user
        - Tasks created by the user
        - Tasks currently assigned to the user

        Returns:
            QuerySet: Filtered task queryset
        """
        user = self.request.user
        return Task.objects.filter(
            Q(project__owner=user) | Q(created_by=user) | Q(assigned_to=user)
        ).distinct()

    def patch(self, request, *args, **kwargs):
        """
        Assigns or unassigns a task to a user.

        Args:
            request: HTTP request object containing user_id or null to unassign
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Query Parameters:
            user_id (int, optional): ID of the user to assign, or null to unassign

        Returns:
            Response:
                - 200 OK if the assignment was successful
                - 400 Bad Request for invalid operations
                - 403 Forbidden if the user doesn't have permission
                - 404 Not Found if the user doesn't exist
        """
        task = self.get_object()
        user = request.user
        user_id = request.data.get('user_id')

        # Verify permissions
        if not (task.project.owner == user or task.created_by == user or task.assigned_to == user):
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Unassign task
        if user_id is None:
            task.assigned_to = None
            task.save()
            serializer = self.get_serializer(task)
            return Response(serializer.data)

        try:
            # Verify the assigned user is a project member
            assigned_user = task.project.members.get(id=user_id)
            task.assigned_to = assigned_user
            task.save()
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User is not a member of this project.'},
                status=status.HTTP_400_BAD_REQUEST
            )
