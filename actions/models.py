from django.db import models


# Create your models here.
class authed_user(models.Model):
    id = models.CharField(max_length=20, unique=True, primary_key=True)
    scope = models.TextField(null=True)
    access_token = models.CharField(max_length=80, unique=True)
    token_type = models.TextField(null=True)
