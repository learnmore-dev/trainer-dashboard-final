from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='trainer')

    def is_trainer(self):
        return self.role == 'trainer'

    def is_admin(self):
        return self.role == 'admin'
