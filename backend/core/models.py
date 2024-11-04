from django.db import models
from django.contrib.auth.models import User
from models.models import Business
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    biz = models.ForeignKey(Business, on_delete=models.CASCADE)

