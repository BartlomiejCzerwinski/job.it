from rest_framework import serializers
from .models import SocialLink

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