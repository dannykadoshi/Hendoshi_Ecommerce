from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_sale_end_product_sale_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.ProductType'),
        ),
    ]
