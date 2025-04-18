from .models import Task
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
        'id', 'title', 'description', 'status', 'priority', 'due_date', 'project', 'created_by', 'assigned_to',
        'created_at', 'updated_at')
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def validate_project(self,value):
        if value.owner != self.context['request'].user:
            raise serializers.ValidationError("Project does not belong to the user")
        return value