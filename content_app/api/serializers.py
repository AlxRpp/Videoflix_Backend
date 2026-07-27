from rest_framework import serializers
from ..models import Video


class ListVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title',
                  'description', 'thumbnail_url', 'category']

    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')
    thumbnail_url = serializers.FileField(source='thumbnail')
    category = serializers.CharField(source='get_category_display')
