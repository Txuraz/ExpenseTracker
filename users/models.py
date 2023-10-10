from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255, choices=[
        ('salary', 'Salary'),
        ('borrow', 'Borrow'),
        ('extra_income', 'Extra Income'),
        ('pocket_money', 'Pocket Money'),
    ])
    date = models.DateField()


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255, choices=[
        ('food', 'Food'),
        ('clothing', 'Clothing'),
        ('education', 'Education'),
        ('shopping', 'Shopping'),
        ('hospital', 'Hospital'),
    ])
    date = models.DateField()
