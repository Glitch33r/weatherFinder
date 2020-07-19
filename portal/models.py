from django.db import models


class City(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Weather(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    lon = models.FloatField()
    lat = models.FloatField()
    weather = models.CharField(max_length=64)
    date = models.DateField()
    temp = models.IntegerField()
    pressure = models.IntegerField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()

    class Meta:
        ordering = ['city_id', 'date', ]
