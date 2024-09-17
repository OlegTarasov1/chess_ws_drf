from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    score = models.IntegerField(default = 0)
    games_played = models.IntegerField(default = 0)
    games_won = models.IntegerField(default = 0)
    games_lost = models.IntegerField(default = 0)
