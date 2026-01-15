from django.contrib import admin
from .models import UserProfile, Address


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_country', 'default_postcode')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'country', 'is_default', 'user')
    list_filter = ('country', 'is_default', 'created_at')
    search_fields = ('full_name', 'city', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Address Information', {
            'fields': ('full_name', 'phone', 'address', 'address_line_2', 'city', 'state_or_county', 'country', 'postal_code')
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
