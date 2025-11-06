#!/usr/bin/env python3
"""Render PDF forms to PNG images for preview/documentation."""

import os
import fitz


def render_pdf_to_png(pdf_path: str, png_path: str, zoom: float = 2.0):
    """Render a PDF page to PNG at specified zoom level.

    Args:
        pdf_path: Path to input PDF
        png_path: Path to output PNG
        zoom: Zoom factor (2.0 = 2x resolution, good for screen display)
    """
    doc = fitz.open(pdf_path)
    page = doc[0]

    # Create transformation matrix for zoom
    mat = fitz.Matrix(zoom, zoom)

    # Render page to pixmap
    pix = page.get_pixmap(matrix=mat)

    # Save as PNG
    pix.save(png_path)

    doc.close()

    return pix.width, pix.height


def main():
    """Render all food license forms to PNG."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    forms = [
        ('food_license_us.pdf', 'food_license_us.png'),
        ('food_license_es.pdf', 'food_license_es.png'),
        ('food_license_th.pdf', 'food_license_th.png'),
        ('food_license_ja.pdf', 'food_license_ja.png'),
        ('food_license_pl.pdf', 'food_license_pl.png'),
    ]

    print("=" * 70)
    print("Rendering PDF forms to PNG images")
    print("Using PyMuPDF native rendering (no external dependencies)")
    print("=" * 70)
    print()

    for pdf_file, png_file in forms:
        pdf_path = os.path.join(script_dir, pdf_file)
        png_path = os.path.join(script_dir, png_file)

        if not os.path.exists(pdf_path):
            print(f"⚠ Skipping {pdf_file} (not found)")
            continue

        width, height = render_pdf_to_png(pdf_path, png_path, zoom=2.0)

        # Get file size
        file_size = os.path.getsize(png_path) / 1024

        print(f"✓ {pdf_file} → {png_file}")
        print(f"  Resolution: {width} x {height} pixels")
        print(f"  File size: {file_size:.1f} KB")
        print()

    print("=" * 70)
    print("✓ All forms rendered successfully!")
    print()
    print("PNG files are 2x resolution (zoom=2.0) for clear screen display.")
    print("Adjust zoom parameter in render_pdf_to_png() for different sizes.")


if __name__ == "__main__":
    main()
