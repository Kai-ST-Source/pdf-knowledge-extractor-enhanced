#!/usr/bin/env python3
"""
Adjust icon ratios: 80% canvas boundary, 99% content within boundary
"""

from PIL import Image, ImageDraw
import os
import subprocess

def create_adjusted_ratio_icon(source_path, output_dir):
    """
    Create icon with 80% canvas boundary and 99% content within boundary
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
        # Start with transparent background
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Use 80% of canvas for boundary (as requested)
        visible_area_ratio = 0.80
        visible_size = int(size * visible_area_ratio)
        
        # Create the visible icon
        visible_icon = Image.new('RGBA', (visible_size, visible_size), (255, 255, 255, 255))
        
        # Use 99% of the visible area for content (as requested)
        content_ratio_in_visible = 0.99
        content_size = int(visible_size * content_ratio_in_visible)
        
        # Resize PDFKE to content size
        resized_content = original.resize((content_size, content_size), Image.Resampling.LANCZOS)
        
        # Center content in visible icon
        content_x = (visible_size - content_size) // 2
        content_y = (visible_size - content_size) // 2
        visible_icon.paste(resized_content, (content_x, content_y), resized_content)
        
        # Keep the 22% corner radius
        corner_radius = max(1, int(visible_size * 0.22))
        
        mask = Image.new('L', (visible_size, visible_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, visible_size, visible_size], radius=corner_radius, fill=255)
        
        # Apply mask to visible icon
        masked_icon = Image.new('RGBA', (visible_size, visible_size), (0, 0, 0, 0))
        masked_icon.paste(visible_icon, (0, 0))
        masked_icon.putalpha(mask)
        
        # Center the visible icon on the full canvas
        icon_x = (size - visible_size) // 2
        icon_y = (size - visible_size) // 2
        canvas.paste(masked_icon, (icon_x, icon_y), masked_icon)
        
        # Save
        output_path = os.path.join(iconset_dir, filename)
        canvas.save(output_path, 'PNG')
        
        print(f"Created {filename}: boundary {visible_size}x{visible_size} (80% of {size}), content {content_size}x{content_size} (99% of boundary)")
    
    # Create .icns
    icns_path = os.path.join(output_dir, "PDFKE_adjusted.icns")
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
        print("Creating icon with adjusted ratios...")
        print("Strategy: 80% canvas boundary, 99% content within boundary")
        print()
        
        icns_file = create_adjusted_ratio_icon(source_file, ".")
        if icns_file:
            print(f"\n✓ Created adjusted icon: {icns_file}")
            print("Boundary: 80% of canvas, Content: 99% of boundary")
        else:
            print("✗ Failed to create icon")
    else:
        print(f"Source file not found: {source_file}")