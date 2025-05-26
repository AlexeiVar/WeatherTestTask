from django.db import models

# Create your models here.
class CheckedCity(models.Model):
    city = models.TextField()
    date = models.TextField()


class CityCounter(models.Model):
    city = models.TextField()
    count = models.IntegerField()
