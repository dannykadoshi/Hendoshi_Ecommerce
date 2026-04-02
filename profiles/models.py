from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    User profile model for maintaining default delivery information
    and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # User display name
    name = models.CharField(max_length=100, null=True, blank=True)

    # Default delivery information
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='(Select Country)', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    """
    Model to store user addresses for checkout and profile
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100)
    state_or_county = models.CharField(max_length=100)
    country = CountryField()
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"


class SavedPaymentMethod(models.Model):
    """
    Model to store saved payment methods for users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_payment_methods')
    card_number = models.CharField(max_length=19)  # Masked except last 4 digits
    card_holder = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=5)  # MM/YY format
    card_type = models.CharField(
        max_length=20,
        choices=[
            ('visa', 'Visa'),
            ('mastercard', 'Mastercard'),
            ('amex', 'American Express'),
            ('discover', 'Discover'),
        ],
        default='visa'
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Saved Payment Methods'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.card_type.title()} ending in {self.card_number[-4:]}"

    def get_display_name(self):
        """Return a display-friendly name for the card"""
        return f"{self.card_type.title()} ending in {self.card_number[-4:]}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # For existing users, create profile if it doesn't exist
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
