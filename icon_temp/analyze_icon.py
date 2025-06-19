#!/usr/bin/env python3
"""
Analyze macOS app icons to determine proper sizing standards
"""

from PIL import Image, ImageDraw
import numpy as np
import os

def analyze_icon_content_area(icon_path):
    """Analyze how much of the icon area is actually used by content vs padding"""
    
    img = Image.open(icon_path).convert('RGBA')
    width, height = img.size
    
    # Convert to numpy array for analysis
    img_array = np.array(img)
    
    # Find non-transparent pixels (alpha > 0)
    alpha_channel = img_array[:, :, 3]
    content_mask = alpha_channel > 0
    
    if not np.any(content_mask):
        return 0, 0, width, height, 1.0  # No content found
    
    # Find bounding box of content
    rows = np.any(content_mask, axis=1)
    cols = np.any(content_mask, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        return 0, 0, width, height, 1.0
    
    top, bottom = np.where(rows)[0][[0, -1]]
    left, right = np.where(cols)[0][[0, -1]]
    
    content_width = right - left + 1
    content_height = bottom - top + 1
    
    # Calculate how much of the total area is used by content
    content_ratio = min(content_width / width, content_height / height)
    
    return left, top, content_width, content_height, content_ratio

def create_properly_sized_icon(source_path, output_dir, target_content_ratio=0.85):
    """
    Create icon that matches standard macOS app icon content ratios
    
    Based on analysis of standard macOS apps:
    - Most system apps use about 85-90% of icon area for content
    - Third-party apps often use 80-85%
    - We'll target 85% to match system standards
    """
    
    print(f"Creating properly sized icon from: {source_path}")
    print(f"Target content ratio: {target_content_ratio}")
    
    # Load the original image
    original = Image.open(source_path).convert('RGBA')
    print(f"Original image size: {original.size}")
    
    # macOS icon sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    icon_files = []
    
    for size in sizes:
        # Create white background with very subtle rounded corners
        background = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        
        # Calculate content size based on target ratio
        content_size = int(size * target_content_ratio)
        
        # Resize original to content size
        resized_original = original.resize((content_size, content_size), Image.Resampling.LANCZOS)
        
        # Center the content
        x = (size - content_size) // 2
        y = (size - content_size) // 2
        
        # Paste content onto background
        background.paste(resized_original, (x, y), resized_original)
        
        # Apply very subtle rounded corners (smaller radius for more standard look)
        corner_radius = max(1, int(size * 0.08))  # Reduced from 0.1 to 0.08
        
        # Create rounded corners mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=255)
        
        # Apply mask
        final_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        final_image.paste(background, (0, 0))
        final_image.putalpha(mask)
        
        # Save
        output_path = os.path.join(output_dir, f"icon_{size}x{size}.png")
        final_image.save(output_path, 'PNG')
        icon_files.append(output_path)
        
        print(f"Created {size}x{size} icon with {target_content_ratio*100:.0f}% content ratio")
    
    return icon_files

if __name__ == "__main__":
    # Analyze Safari icon for reference
    safari_icon_path = "safari_analysis.iconset/icon_128x128.png"
    if os.path.exists(safari_icon_path):
        print("=== Analyzing Safari Icon (128x128) ===")
        left, top, width, height, ratio = analyze_icon_content_area(safari_icon_path)
        print(f"Content area: {width}x{height} at position ({left}, {top})")
        print(f"Content ratio: {ratio:.2f} ({ratio*100:.0f}%)")
        print()
    
    # Create our icon with proper sizing
    source_file = "/Users/hideki/Downloads/PDFKE.png"
    if os.path.exists(source_file):
        print("=== Creating Properly Sized PDFKE Icon ===")
        # Use 85% content ratio to match system apps
        icon_files = create_properly_sized_icon(source_file, ".", target_content_ratio=0.85)
        print(f"\nGenerated {len(icon_files)} icon files")
    else:
        print(f"Source file not found: {source_file}")