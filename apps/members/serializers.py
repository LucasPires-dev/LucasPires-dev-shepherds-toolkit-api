from rest_framework import serializers
from .models import Member, PastoralVisit


class MemberSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'user', 'full_name', 'email', 'phone',
                  'birth_date', 'age', 'address', 'member_since',
                  'baptism_date', 'status', 'ministry', 'cell_group',
                  'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_age(self, obj):
        if obj.birth_date:
            from datetime import date
            today = date.today()
            return today.year - obj.birth_date.year - (
                    (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
            )
        return None


class PastoralVisitSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)

    class Meta:
        model = PastoralVisit
        fields = ['id', 'user', 'member', 'member_name', 'visit_date',
                  'visit_type', 'notes', 'follow_up_needed', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']