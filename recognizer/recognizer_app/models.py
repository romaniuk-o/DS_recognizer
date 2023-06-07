from django.contrib.auth.models import User
from django.db import models

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Model(models.Model):
    name = models.CharField(max_length=80, null=True)