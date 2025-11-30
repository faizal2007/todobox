import cairosvg
from pathlib import Path

SIZES = [192, 256, 384, 512]
BASE_DIR = Path(__file__).resolve().parent.parent
SVG_PATH = BASE_DIR / 'app' / 'static' / 'assets' / 'images' / 'logo.svg'
OUT_DIR = BASE_DIR / 'app' / 'static' / 'assets' / 'icons'

def main():
    if not SVG_PATH.exists():
        raise SystemExit(f'SVG logo not found at {SVG_PATH}')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        png_path = OUT_DIR / f'icon-{size}x{size}.png'
        cairosvg.svg2png(url=str(SVG_PATH), write_to=str(png_path), output_width=size, output_height=size)
        print(f'Generated {png_path}')

if __name__ == '__main__':
    main()
