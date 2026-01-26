from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_migrate_product_types_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_type',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='product_type_fk',
            new_name='product_type',
        ),
    ]
