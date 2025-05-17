from rest_framework import serializers
from .models import SocialLink, Project
import json

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['id', 'platform', 'url', 'display_name']
        read_only_fields = ['id']

    def validate_platform(self, value):
        valid_platforms = [choice[0] for choice in SocialLink.PLATFORM_CHOICES]
        if value not in valid_platforms:
            raise serializers.ValidationError(f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
        return value

class ProjectSerializer(serializers.ModelSerializer):
    technologies = serializers.JSONField(required=False)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'technologies', 'github_link', 'demo_link', 'order']
        read_only_fields = ['id']

    def create(self, validated_data):
        if 'technologies' in validated_data and validated_data['technologies']:
            validated_data['technologies'] = json.dumps(validated_data['technologies'])
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['technologies'] = instance.get_technologies()
        return representation 