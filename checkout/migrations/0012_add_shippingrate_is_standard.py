from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0011_add_shippingrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingrate',
            name='is_standard',
            field=models.BooleanField(default=False, help_text='Mark this as the standard/default shipping rate'),
        ),
    ]
