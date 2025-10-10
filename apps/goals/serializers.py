from rest_framework import serializers
from .models import Goal, GoalTask, GoalComment


class GoalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTask
        fields = ['id', 'goal', 'title', 'description', 'responsible',
                  'status', 'order_index', 'start_date', 'due_date',
                  'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GoalCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = GoalComment
        fields = ['id', 'goal', 'user', 'user_name', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class GoalSerializer(serializers.ModelSerializer):
    tasks = GoalTaskSerializer(many=True, read_only=True)
    comments = GoalCommentSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ['id', 'user', 'title', 'description', 'category',
                  'ministry_type', 'priority', 'status', 'progress_percentage',
                  'start_date', 'end_date', 'created_at', 'updated_at',
                  'completed_at', 'tasks', 'comments', 'task_count',
                  'completed_task_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_completed_task_count(self, obj):
        return obj.tasks.filter(status='completed').count()


class GoalListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ['id', 'title', 'category', 'priority', 'status',
                  'progress_percentage', 'end_date', 'task_count']

    def get_task_count(self, obj):
        return obj.tasks.count()
