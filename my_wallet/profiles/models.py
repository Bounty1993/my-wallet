from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from django.urls import reverse


class Profile(AbstractUser):

    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=30, blank=True)
    zip_code = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='profile_pics/', default='default.png',
                              blank=True)

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        output_size = (125, 125)
        img.thumbnail(output_size)
        img.save(self.image.path)

    def get_absolute_url(self):
        return reverse('profiles:profile')

    def __str__(self):
        return self.username
