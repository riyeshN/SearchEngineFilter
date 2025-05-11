from tkinter.constants import CASCADE

from django.db import models

# Create your models here.
class SearchEngine(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    baseUrl = models.CharField(max_length=150)

class SearchTermMapping(models.Model):
    id = models.AutoField(primary_key=True)
    searchEngineName = models.ForeignKey(SearchEngine, on_delete=models.CASCADE)
    searchTerm = models.CharField(max_length=150)
    time_searched = models.DateTimeField()
    
class SearchUrls(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=500)
    desc = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    ad = models.BooleanField()
    promo = models.BooleanField()
    data_scrape_time = models.DateTimeField(null=True)
    searchTermId = models.ForeignKey(SearchTermMapping, on_delete=models.CASCADE)

class UrlData(models.Model):
    id = models.AutoField(primary_key=True)
    searchUrls = models.ForeignKey(SearchUrls, on_delete=models.CASCADE)
    count_of_appearance = models.BigIntegerField()
    html_data = models.TextField()
