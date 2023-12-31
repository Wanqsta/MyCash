from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    chat_id = models.CharField(max_length=19,blank=True,null=True)
    
    def __str__(self):
        return self.username
