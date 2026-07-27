from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Video
from .tasks import convert480p, convert720p, convert1080p, thumbnail, convert_hls
import django_rq
import os
from django.conf import settings


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """On a new upload, queue the thumbnail plus the three resolutions and
    their HLS conversion as background jobs."""
    if created:
        video = instance.video.path
        base = os.path.splitext(video)[0]
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(thumbnail, instance.pk, video)
        queue.enqueue(convert480p, video)
        queue.enqueue(convert_hls, base + "_480p.mp4", instance.pk, "480p")
        queue.enqueue(convert720p, video)
        queue.enqueue(convert_hls, base + "_720p.mp4", instance.pk, "720p")
        queue.enqueue(convert1080p, video)
        queue.enqueue(convert_hls, base + "_1080p.mp4", instance.pk, "1080p")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """Clean up the files of a deleted video: the original, the three
    converted resolutions and the thumbnail."""
    video = instance.video.path
    base = os.path.splitext(os.path.basename(video))[0]
    thumb_path = os.path.join(
        settings.MEDIA_ROOT, "thumbnails", base + "_thumb.jpg")
    pure_video_name = os.path.splitext(video)[0]
    video480 = pure_video_name + "_480p.mp4"
    video720 = pure_video_name + "_720p.mp4"
    video1080 = pure_video_name + "_1080p.mp4"

    if video:
        if os.path.isfile(video):
            os.remove(video)
        if os.path.isfile(video480):
            os.remove(video480)
        if os.path.isfile(video720):
            os.remove(video720)
        if os.path.isfile(video1080):
            os.remove(video1080)
        if os.path.isfile(thumb_path):
            os.remove(thumb_path)
