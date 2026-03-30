from django.contrib import admin
from .models import VaultPhoto


@admin.register(VaultPhoto)
class VaultPhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'status', 'created_at', 'likes_count')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'caption')
    readonly_fields = ('created_at',)
    actions = ['approve_photos', 'reject_photos']

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"

    def approve_photos(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} photo(s) approved.")
    approve_photos.short_description = "Approve selected photos"

    def reject_photos(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} photo(s) rejected.")
    reject_photos.short_description = "Reject selected photos"
