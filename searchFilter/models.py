from tkinter.constants import CASCADE

from django.db import models

# Create your models here.
class SearchEngine(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    baseUrl = models.CharField(max_length=150)

class SearchTermMapping(models.Model):
    id = models.AutoField(primary_key=True)
    searchEngineId = models.ForeignKey(SearchEngine, on_delete=models.CASCADE)
    searchTerm = models.CharField(max_length=150)
    
class SearchUrls(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=500)
    desc = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    ad = models.BooleanField()
    searchTermId = models.ForeignKey(SearchTermMapping, on_delete=models.CASCADE)

class UrlData(models.Model):
    id = models.AutoField(primary_key=True)
    searchUrlsId = models.ForeignKey(SearchUrls, on_delete=models.CASCADE)
    count_of_appearance = models.BigIntegerField()