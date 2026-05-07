

from django.db import models


class City(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100)
    latitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    def __str__(self):
        return f"{self.id}, {self.name}, {self.state}"

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']


class Edge(models.Model):
    from_city    = models.ForeignKey(City, on_delete=models.CASCADE, related_name='edges_from')
    to_city      = models.ForeignKey(City, on_delete=models.CASCADE, related_name='edges_to')
    distance_km  = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}: {self.from_city.name} → {self.to_city.name} ({self.distance_km} km)"

    class Meta:
        unique_together = ('from_city', 'to_city')


class SearchHistory(models.Model):
    source         = models.ForeignKey(City, on_delete=models.CASCADE, related_name='searches_as_source')
    destination    = models.ForeignKey(City, on_delete=models.CASCADE, related_name='searches_as_destination')
    path_json      = models.JSONField()          # ordered list of city names  e.g. ["Delhi", "Agra", "Jaipur"]
    total_distance = models.PositiveIntegerField()
    searched_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source.name} → {self.destination.name} ({self.total_distance} km) at {self.searched_at:%d %b %Y %H:%M}"

    class Meta:
        verbose_name_plural = "Search Histories"
        ordering = ['-searched_at']

# Create your models here.
