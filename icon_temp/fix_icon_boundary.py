#!/usr/bin/env python3
"""
Fix icon: Make the overall icon boundary smaller while keeping content large
The issue: We need to reduce the total visible icon area (smaller rounded rectangle)
while maximizing the PDFKE content within that smaller area
"""

from PIL import Image, ImageDraw
import os
import subprocess

def create_smaller_boundary_icon(source_path, output_dir):
    """
    Create icon with smaller overall boundary but larger content inside
    
    Strategy:
    1. Create a smaller visible icon area (like other macOS apps)
    2. Fill most of that area with the PDFKE content
    3. Use minimal padding around the PDFKE image
    """
    
    original = Image.open(source_path).convert('RGBA')
    
    icon_configs = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"), 
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]
    
    iconset_dir = os.path.join(output_dir, "PDFKE.iconset")
    os.makedirs(iconset_dir, exist_ok=True)
    
    for size, filename in icon_configs:
        # Start with transparent background (full canvas size)
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Calculate the actual visible icon area (smaller than full canvas)
        # This is the key: make the visible area smaller
        visible_area_ratio = 0.85  # The visible icon will be 85% of the canvas
        visible_size = int(size * visible_area_ratio)
        
        # Create the smaller visible icon
        visible_icon = Image.new('RGBA', (visible_size, visible_size), (255, 255, 255, 255))
        
        # Fill most of the visible area with PDFKE content (minimal padding)
        content_ratio_in_visible = 0.90  # Use 90% of the visible area for content
        content_size = int(visible_size * content_ratio_in_visible)
        
        # Resize PDFKE to content size
        resized_content = original.resize((content_size, content_size), Image.Resampling.LANCZOS)
        
        # Center content in visible icon
        content_x = (visible_size - content_size) // 2
        content_y = (visible_size - content_size) // 2
        visible_icon.paste(resized_content, (content_x, content_y), resized_content)
        
        # Apply rounded corners to the visible icon
        corner_radius = max(1, int(visible_size * 0.12))  # Relative to visible size
        
        mask = Image.new('L', (visible_size, visible_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, visible_size, visible_size], radius=corner_radius, fill=255)
        
        # Apply mask to visible icon
        masked_icon = Image.new('RGBA', (visible_size, visible_size), (0, 0, 0, 0))
        masked_icon.paste(visible_icon, (0, 0))
        masked_icon.putalpha(mask)
        
        # Center the smaller visible icon on the full canvas
        icon_x = (size - visible_size) // 2
        icon_y = (size - visible_size) // 2
        canvas.paste(masked_icon, (icon_x, icon_y), masked_icon)
        
        # Save
        output_path = os.path.join(iconset_dir, filename)
        canvas.save(output_path, 'PNG')
        
        print(f"Created {filename}: visible area {visible_size}x{visible_size}, content {content_size}x{content_size}")
    
    # Create .icns
    icns_path = os.path.join(output_dir, "PDFKE_fixed.icns")
    try:
        subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path], check=True)
        subprocess.run(['rm', '-rf', iconset_dir], check=True)
        return icns_path
    except Exception as e:
        print(f"Error creating icns: {e}")
        return None

if __name__ == "__main__":
    source_file = "/Users/hideki/Downloads/PDFKE.png"
    if os.path.exists(source_file):
        print("Creating icon with smaller boundary and larger content...")
        print("Strategy: 85% visible area of canvas, 90% content within visible area")
        print()
        
        icns_file = create_smaller_boundary_icon(source_file, ".")
        if icns_file:
            print(f"\n✓ Created fixed icon: {icns_file}")
            print("The overall icon boundary is now smaller while PDFKE content is larger within it")
        else:
            print("✗ Failed to create icon")
    else:
        print(f"Source file not found: {source_file}")