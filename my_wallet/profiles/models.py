from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    name = models.CharField(max_length=300, default='test')
