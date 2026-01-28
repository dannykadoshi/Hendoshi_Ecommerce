from django.contrib import admin
from .models import SeasonalTheme


@admin.register(SeasonalTheme)
class SeasonalThemeAdmin(admin.ModelAdmin):
    """Django admin configuration for SeasonalTheme model"""

    list_display = [
        'name', 'theme_type', 'get_status', 'priority',
        'animation_speed', 'particle_density', 'start_date', 'end_date', 'updated_at'
    ]
    list_filter = ['is_active', 'is_paused', 'theme_type', 'animation_speed', 'particle_density']
    search_fields = ['name', 'theme_type']
    ordering = ['-priority', 'name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'theme_type')
        }),
        ('Activation', {
            'fields': ('is_active', 'is_paused', 'priority'),
            'description': 'Control whether this theme is active and its priority over other themes.'
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date'),
            'description': 'Optional date range for automatic activation.'
        }),
        ('Animation Settings', {
            'fields': ('animation_speed', 'particle_density'),
            'description': 'Configure the animation behavior.'
        }),
        ('Advanced', {
            'fields': ('custom_css',),
            'classes': ('collapse',),
            'description': 'Custom CSS for advanced customization.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['activate_themes', 'deactivate_themes', 'pause_themes', 'resume_themes']

    def get_status(self, obj):
        """Display current status with color coding"""
        status = obj.get_status_display_text()
        colors = {
            'Active': 'green',
            'Inactive': 'gray',
            'Paused': 'orange',
            'Scheduled': 'blue',
            'Expired': 'red',
        }
        color = colors.get(status, 'gray')
        return f'<span style="color: {color}; font-weight: bold;">{status}</span>'
    get_status.short_description = 'Status'
    get_status.allow_tags = True

    @admin.action(description='Activate selected themes')
    def activate_themes(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} theme(s) activated.')

    @admin.action(description='Deactivate selected themes')
    def deactivate_themes(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} theme(s) deactivated.')

    @admin.action(description='Pause selected themes')
    def pause_themes(self, request, queryset):
        count = queryset.update(is_paused=True)
        self.message_user(request, f'{count} theme(s) paused.')

    @admin.action(description='Resume selected themes')
    def resume_themes(self, request, queryset):
        count = queryset.update(is_paused=False)
        self.message_user(request, f'{count} theme(s) resumed.')
