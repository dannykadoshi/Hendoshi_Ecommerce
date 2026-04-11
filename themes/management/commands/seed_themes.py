from django.core.management.base import BaseCommand
from themes.models import SeasonalTheme


THEMES = [
    {
        "name": "Christmas2026",
        "theme_type": "christmas",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": False,
        "strip_messages": "",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "New Years",
        "theme_type": "new_years",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": False,
        "strip_messages": "",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Valentine's Day 2026",
        "theme_type": "valentines",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": True,
        "strip_messages": "HAPPY VALENTINE'S DAY | LOVE FULLY | SPREAD THE LOVE | STAY WEIRD",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Saint Patrick's Day",
        "theme_type": "st_patricks",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": True,
        "strip_messages": "HAPPY SAINT PATRICK'S DAY | LOVE FROM IRELAND",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Mother's Day",
        "theme_type": "mothers_day",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": False,
        "strip_messages": "",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Father's Day",
        "theme_type": "fathers_day",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": False,
        "strip_messages": "",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "4th July",
        "theme_type": "fourth_july",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": False,
        "strip_messages": "",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Rock'N'Roll Day",
        "theme_type": "rock_n_roll",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": False,
        "strip_messages": "",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Daily Theme",
        "theme_type": "everyday",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": True,
        "strip_messages": "WEAR YOUR WEIRD | SALE NOW ON",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Celebration",
        "theme_type": "celebration",
        "is_active": True,
        "is_paused": True,
        "priority": 100,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": True,
        "strip_messages": "HAPPY LIFE | LOVE FULLY | SPREAD THE LOVE",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
    {
        "name": "Thanksgiving",
        "theme_type": "thanksgiving",
        "is_active": True,
        "is_paused": True,
        "priority": 0,
        "animation_speed": "normal",
        "particle_density": "medium",
        "show_message_strip": True,
        "strip_messages": "HAPPY THANKSGIVING | GRATEFUL FOR YOU",
        "strip_color_scheme": "theme",
        "strip_scroll_speed": "normal",
    },
]


class Command(BaseCommand):
    help = "Seed all seasonal themes using update_or_create (safe to run multiple times)"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for data in THEMES:
            theme_type = data.pop("theme_type")
            obj, created = SeasonalTheme.objects.update_or_create(
                theme_type=theme_type,
                defaults=data,
            )
            data["theme_type"] = theme_type  # restore for next iteration safety

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {obj.name} ({theme_type})"))
            else:
                updated_count += 1
                self.stdout.write(f"  Updated: {obj.name} ({theme_type})")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created_count} created, {updated_count} updated."
            )
        )
