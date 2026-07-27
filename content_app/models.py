from django.db import models


class Video(models.Model):
    CATEGORY_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('scifi', 'Scifi'),
        ('romance', 'Romance'),


    ]

    title = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True)
    video = models.FileField(upload_to="videos/", null=False)

    def __str__(self):
        return f"{self.title} | {self.category} | {self.created_at}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
