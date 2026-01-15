import sys
from pathlib import Path
from PIL import Image

# Usage: python scripts/optimize_images.py <input_path> [--width 1000] [--quality 80]

def optimize_image(input_path: Path, max_width: int = 1000, quality: int = 80):
    img = Image.open(input_path).convert("RGBA")
    # Resize if wider than max_width
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    # Save optimized PNG (overwrite) preserving alpha
    png_params = {}
    if input_path.suffix.lower() == ".png":
        try:
            img.save(input_path, optimize=True)
        except Exception:
            img.save(input_path)
    # Also save WebP alongside for better compression with alpha
    webp_path = input_path.with_suffix('.webp')
    img.save(webp_path, format="WEBP", quality=quality, method=6)
    return webp_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/optimize_images.py <input_path> [--width N] [--quality Q]")
        sys.exit(1)
    path = Path(sys.argv[1])
    max_width = 1000
    quality = 80
    if "--width" in sys.argv:
        i = sys.argv.index("--width")
        max_width = int(sys.argv[i+1])
    if "--quality" in sys.argv:
        i = sys.argv.index("--quality")
        quality = int(sys.argv[i+1])
    out = optimize_image(path, max_width=max_width, quality=quality)
    print(f"Optimized: {path}\nWebP: {out}")