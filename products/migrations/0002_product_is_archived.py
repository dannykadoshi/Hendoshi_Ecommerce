from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_archived',
            field=models.BooleanField(default=False, help_text='If true, product is archived and hidden from frontend.'),
        ),
    ]
