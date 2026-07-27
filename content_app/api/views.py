from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
from django.conf import settings
from .serializers import ListVideoSerializer
from ..models import Video
import os


class ListAllVideosView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListVideoSerializer
    queryset = Video.objects.all()


class HLSPlayListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        path = os.path.join(settings.MEDIA_ROOT, "hls", str(
            movie_id), resolution, "index.m3u8")
        if not os.path.isfile(path):
            raise Http404("Manifest not found")
        return FileResponse(open(path, "rb"), content_type="application/vnd.apple.mpegurl")


class HLSSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        path = os.path.join(settings.MEDIA_ROOT, "hls",
                            str(movie_id), resolution, segment)
        if not os.path.isfile(path):
            raise Http404("Segment not found")
        return FileResponse(open(path, "rb"), content_type="video/MP2T")
