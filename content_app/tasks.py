import subprocess
import os
from .models import Video
from django.conf import settings


def convert480p(source):
    new_file_name = os.path.splitext(source)[0]
    new_file = new_file_name + "_480p.mp4"
    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd480',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        new_file,
    ]
    subprocess.run(cmd, capture_output=True)


def convert720p(source):
    new_file_name = os.path.splitext(source)[0]
    new_file = new_file_name + "_720p.mp4"
    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd720',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        new_file,
    ]
    subprocess.run(cmd, capture_output=True)


def convert1080p(source):
    new_file_name = os.path.splitext(source)[0]
    new_file = new_file_name + "_1080p.mp4"
    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', 'hd1080',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        new_file,
    ]
    subprocess.run(cmd, capture_output=True)


def thumbnail(pk, source):
    base = os.path.splitext(os.path.basename(source))[0]
    thumb_path = os.path.join(
        settings.MEDIA_ROOT, "thumbnails", base + "_thumb.jpg")
    cmd = [
        'ffmpeg',
        '-i', source,
        '-ss',
        '00:00:01',
        '-vframes',
        '1',
        thumb_path]
    subprocess.run(cmd, capture_output=True)
    rel = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
    Video.objects.filter(pk=pk).update(thumbnail=rel)


def convert_hls(source, movie_id, resolution):
    out_dir = os.path.join(settings.MEDIA_ROOT, "hls",
                           str(movie_id), resolution)
    os.makedirs(out_dir, exist_ok=True)
    cmd = [
        'ffmpeg', '-i', source,
        '-codec:', 'copy',
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-hls_segment_filename', os.path.join(out_dir, '%03d.ts'),
        '-f', 'hls',
        os.path.join(out_dir, 'index.m3u8'),
    ]
    subprocess.run(cmd, capture_output=True)
