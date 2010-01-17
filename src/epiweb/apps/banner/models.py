from django.db import models
from django.db.models.signals import pre_save

class Category(models.Model):
    name = models.SlugField()
    description = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class Image(models.Model):
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=250)
    image = models.ImageField(upload_to='banner')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(Category, blank=True)

    def __unicode__(self):
        return self.title

# def normalize_name(sender, **kwargs):
#     instance = kwargs.get('instance', None)
#     if instance is not None:
#         instance.name = instance.name.strip().lower()
# 
# pre_save.connect(normalize_name, sender=Category)

