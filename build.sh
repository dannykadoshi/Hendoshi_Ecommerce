#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_initial_data

# Load fixtures if they exist
if [ -d "fixtures" ]; then
    echo "Loading fixtures..."
    python manage.py loaddata fixtures/collections.json
    python manage.py loaddata fixtures/product_types.json
    python manage.py loaddata fixtures/shipping_rates.json
    python manage.py loaddata fixtures/seasonal_themes.json
    python manage.py loaddata fixtures/products.json

    # Copy media files if they exist
    if [ -d "fixtures/media" ]; then
        echo "Copying media files..."
        mkdir -p media
        cp -r fixtures/media/* media/ 2>/dev/null || true
    fi
fi