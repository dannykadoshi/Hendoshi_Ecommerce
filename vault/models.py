from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class VaultPhoto(models.Model):
    """
    Model for user-generated content photos in The Vault gallery
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vault_photos')
    image = models.ImageField(upload_to='vault/', help_text="Upload your photo wearing HENDOSHI gear")
    caption = models.CharField(max_length=800, blank=True, help_text="Optional caption (max 800 characters)")
    tagged_products = models.ManyToManyField(Product, blank=True, related_name='vault_photos', help_text="Tag the HENDOSHI products you're wearing")  # noqa: E501
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='liked_vault_photos', blank=True)

    # Featured photo system
    is_featured = models.BooleanField(default=False, help_text="Is this photo currently featured?")
    featured_date = models.DateTimeField(null=True, blank=True, help_text="When this photo was first featured")
    featured_until = models.DateTimeField(null=True, blank=True, help_text="When the feature period ends")
    feature_score = models.IntegerField(default=0, help_text="Score for determining feature worthiness (likes + engagement)")  # noqa: E501

    # Voting system
    upvotes = models.ManyToManyField(User, related_name='upvoted_vault_photos', blank=True, help_text="Users who upvoted this photo")  # noqa: E501
    downvotes = models.ManyToManyField(User, related_name='downvoted_vault_photos', blank=True, help_text="Users who downvoted this photo")  # noqa: E501
    vote_score = models.IntegerField(default=0, help_text="Net vote score (upvotes - downvotes)")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vault Photo'
        verbose_name_plural = 'Vault Photos'

    def __str__(self):
        return f"{self.user.username} - {self.caption or 'No caption'} ({self.status})"

    def save(self, *args, **kwargs):
        """Compress image on upload"""
        if self.image and hasattr(self.image, 'file'):
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)

    @staticmethod
    def compress_image(image, max_width=1920, quality=85):
        """Compress and resize uploaded images for better performance"""
        try:
            img = Image.open(image)

            # Convert RGBA/P to RGB if needed
            if img.mode in ('RGBA', 'P', 'LA'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if too large
            if img.width > max_width or img.height > max_width:
                img.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)

            # Save compressed
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)

            # Get original filename
            name = image.name.split('.')[0] if hasattr(image, 'name') else 'vault_photo'

            return InMemoryUploadedFile(
                output, 'ImageField',
                f"{name}.jpg",
                'image/jpeg',
                sys.getsizeof(output),
                None
            )
        except Exception as e:
            # If compression fails, return original
            print(f"Image compression failed: {e}")
            return image
