from django.urls import path
from .views import ListAllVideosView, HLSPlayListView, HLSSegmentView

urlpatterns = [
    path('video/', ListAllVideosView.as_view(), name='videos'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8',
         HLSPlayListView.as_view(), name='video-resolution'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/',
         HLSSegmentView.as_view(), name='video-segment')
]
