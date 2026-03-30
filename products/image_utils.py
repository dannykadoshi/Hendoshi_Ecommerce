import os
import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)


def optimize_product_images(product):
    """
    Safely optimize product images without overwriting originals.
    Creates optimized versions alongside originals.
    """
    optimized_count = 0
    errors = []

    try:
        # Optimize main image
        if product.main_image:
            result = optimize_single_image(product.main_image.path)
            if result['success']:
                optimized_count += 1
                logger.info(f"Optimized main image for product {product.name}: {result}")
            else:
                errors.append(f"Main image failed: {result['error']}")

        # Optimize additional images
        for product_image in product.images.all():
            result = optimize_single_image(product_image.image.path)
            if result['success']:
                optimized_count += 1
                logger.info(f"Optimized gallery image for product {product.name}: {result}")
            else:
                errors.append(f"Gallery image {product_image.id} failed: {result['error']}")

    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        logger.error(f"Error optimizing images for product {product.name}: {str(e)}")

    return {
        'optimized_count': optimized_count,
        'errors': errors,
        'success': len(errors) == 0
    }


def optimize_single_image(image_path):
    """
    Optimize a single image file safely.
    Returns dict with success status and details.
    """
    try:
        if not os.path.exists(image_path):
            return {'success': False, 'error': 'File does not exist'}

        # Open and validate image
        with Image.open(image_path) as img:
            img.verify()  # Verify it's a valid image

        # Re-open for processing
        with Image.open(image_path) as img:
            original_size = os.path.getsize(image_path)

            # Convert to RGBA for consistent processing
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Resize if too large (max 1200px width for products)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # Create optimized versions
            path_obj = Path(image_path)
            base_name = path_obj.stem
            directory = path_obj.parent

            # Save optimized PNG
            png_path = directory / f"{base_name}_optimized.png"
            img.save(png_path, 'PNG', optimize=True)

            # Save WebP version for modern browsers
            webp_path = directory / f"{base_name}_optimized.webp"
            img.save(webp_path, 'WEBP', quality=85, method=6)

            new_size = os.path.getsize(png_path)
            webp_size = os.path.getsize(webp_path)

            return {
                'success': True,
                'original_path': str(image_path),
                'png_path': str(png_path),
                'webp_path': str(webp_path),
                'original_size': original_size,
                'optimized_size': new_size,
                'webp_size': webp_size,
                'savings_percent': round((1 - new_size/original_size) * 100, 1)
            }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_optimized_image_urls(product):
    """
    Get URLs for optimized versions of product images.
    Returns dict with original and optimized URLs.
    """
    optimized_urls = {}

    try:
        if product.main_image:
            path_obj = Path(product.main_image.path)
            base_name = path_obj.stem
            directory = str(path_obj.parent)

            # Check if optimized versions exist
            png_path = Path(directory) / f"{base_name}_optimized.png"
            webp_path = Path(directory) / f"{base_name}_optimized.webp"

            optimized_urls['main_image'] = {
                'original': product.main_image.url,
                'png': f"{product.main_image.url.rsplit('.', 1)[0]}_optimized.png" if png_path.exists() else None,
                'webp': f"{product.main_image.url.rsplit('.', 1)[0]}_optimized.webp" if webp_path.exists() else None,
            }

        # Handle gallery images
        optimized_urls['gallery'] = []
        for product_image in product.images.all():
            path_obj = Path(product_image.image.path)
            base_name = path_obj.stem
            directory = str(path_obj.parent)

            png_path = Path(directory) / f"{base_name}_optimized.png"
            webp_path = Path(directory) / f"{base_name}_optimized.webp"

            optimized_urls['gallery'].append({
                'original': product_image.image.url,
                'png': f"{product_image.image.url.rsplit('.', 1)[0]}_optimized.png" if png_path.exists() else None,
                'webp': f"{product_image.image.url.rsplit('.', 1)[0]}_optimized.webp" if webp_path.exists() else None,
            })

    except Exception as e:
        logger.error(f"Error getting optimized URLs for product {product.name}: {str(e)}")

    return optimized_urls
