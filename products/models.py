from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    """
    Model for product collections (Skulls & Death, Weird Animals, etc.)
    """
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='collections/', null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Collections'
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name