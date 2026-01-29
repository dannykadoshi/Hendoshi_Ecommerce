# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0012_add_shippingrate_is_standard'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingrate',
            name='estimated_delivery',
            field=models.CharField(blank=True, default='', help_text='e.g. "5-7 business days" or "2-3 business days"', max_length=100),
        ),
    ]
