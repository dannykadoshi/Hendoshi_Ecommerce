import sys
from pathlib import Path
from PIL import Image

def optimize_hero_image(input_path: Path):
    img = Image.open(input_path).convert("RGBA")
    base_name = input_path.stem  # e.g., hero-1-gothic

    sizes = [1080, 1920, 2560]
    for width in sizes:
        if img.width > width:
            ratio = width / float(img.width)
            new_height = int(img.height * ratio)
            resized_img = img.resize((width, new_height), Image.LANCZOS)
        else:
            resized_img = img.copy()

        output_path = input_path.parent / f"{base_name}-{width}.webp"
        resized_img.save(output_path, format="WEBP", quality=85, method=6)
        print(f"Generated: {output_path}")

if __name__ == "__main__":
    images_dir = Path("/Users/dannykadoshi/Desktop/Hendoshi_Ecommerce/static/images")
    hero_images = list(images_dir.glob("hero-*.png"))
    for img_path in sorted(hero_images):
        optimize_hero_image(img_path)
    print("All hero images optimized.")