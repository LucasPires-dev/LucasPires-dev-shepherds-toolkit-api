from rest_framework import serializers
from .models import ReadingPlanTemplate, UserReadingPlan, ReadingDay
from datetime import timedelta


class ReadingPlanTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingPlanTemplate
        fields = ['id', 'name', 'description', 'plan_type', 'duration_days',
                  'icon', 'color', 'readings_count']


class ReadingDaySerializer(serializers.ModelSerializer):
    readings = serializers.JSONField(source='readings_data', read_only=True)

    class Meta:
        model = ReadingDay
        fields = ['id', 'date', 'day_number', 'readings', 'status',
                  'completed_at', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserReadingPlanSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='plan_type', read_only=True)
    days_completed = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    current_day = serializers.SerializerMethodField()

    class Meta:
        model = UserReadingPlan
        fields = ['id', 'name', 'description', 'type', 'start_date', 'end_date',
                  'total_days', 'days_completed', 'progress_percentage',
                  'is_active', 'status', 'current_day', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_current_day(self, obj):
        from datetime import date
        today = date.today()
        current_reading = obj.reading_days.filter(date=today).first()
        if current_reading:
            return ReadingDaySerializer(current_reading).data
        return None


class CreateReadingPlanSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    custom_readings = serializers.JSONField(required=False)

    def validate(self, data):
        if not data.get('template_id') and not data.get('custom_readings'):
            raise serializers.ValidationError(
                "É necessário fornecer um template_id ou custom_readings"
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        template_id = validated_data.get('template_id')
        name = validated_data['name']
        start_date = validated_data['start_date']

        # Buscar template
        template = None
        if template_id:
            try:
                template = ReadingPlanTemplate.objects.get(id=template_id)
                readings_data = template.readings_data
                total_days = template.duration_days
                plan_type = template.plan_type
            except ReadingPlanTemplate.DoesNotExist:
                raise serializers.ValidationError("Template não encontrado")
        else:
            # Plano customizado
            readings_data = validated_data.get('custom_readings', [])
            total_days = len(readings_data)
            plan_type = 'custom'

        # Calcular data de término
        end_date = start_date + timedelta(days=total_days - 1)

        # Criar plano
        plan = UserReadingPlan.objects.create(
            user=user,
            template=template,
            name=name,
            description=template.description if template else '',
            plan_type=plan_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            is_active=True
        )

        # Criar dias de leitura
        current_date = start_date
        for day_num, reading in enumerate(readings_data, start=1):
            ReadingDay.objects.create(
                plan=plan,
                date=current_date,
                day_number=day_num,
                readings_data=reading
            )
            current_date += timedelta(days=1)

        return plan


class UpdateReadingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['completed', 'skipped', 'pending'])
    notes = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        if 'notes' in validated_data:
            instance.notes = validated_data['notes']

        if validated_data['status'] == 'completed':
            from django.utils import timezone
            instance.completed_at = timezone.now()
        elif instance.completed_at:
            instance.completed_at = None

        instance.save()
        return instance


class ReadingStatsSerializer(serializers.Serializer):
    total_days = serializers.IntegerField()
    completed_days = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_per_week = serializers.FloatField()