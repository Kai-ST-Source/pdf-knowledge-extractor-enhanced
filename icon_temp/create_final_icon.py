#!/usr/bin/env python3
"""
Create final icon that matches macOS standards exactly
Based on analysis: Safari uses 88% content ratio with subtle positioning
"""

from PIL import Image, ImageDraw
import os
import subprocess

def create_standard_macos_icon(source_path, output_dir):
    """Create icon that exactly matches macOS system app standards"""
    
    # Load source
    original = Image.open(source_path).convert('RGBA')
    
    # macOS icon sizes and their iconset naming
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
    
    # Create iconset directory
    iconset_dir = os.path.join(output_dir, "PDFKE.iconset")
    os.makedirs(iconset_dir, exist_ok=True)
    
    for size, filename in icon_configs:
        # Create white background
        background = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        
        # Calculate content size - using 85% to be slightly more conservative than Safari's 88%
        # This ensures our icon won't appear larger than system apps
        content_size = int(size * 0.85)
        
        # Resize original to content size
        resized_original = original.resize((content_size, content_size), Image.Resampling.LANCZOS)
        
        # Center the content
        x = (size - content_size) // 2
        y = (size - content_size) // 2
        
        # Paste content onto background
        background.paste(resized_original, (x, y), resized_original)
        
        # Apply standard macOS rounded corners
        # Use smaller radius for more subtle rounding
        corner_radius = max(1, int(size * 0.075))  # Even more subtle
        
        # Create mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=255)
        
        # Apply mask
        final_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        final_image.paste(background, (0, 0))
        final_image.putalpha(mask)
        
        # Save to iconset
        output_path = os.path.join(iconset_dir, filename)
        final_image.save(output_path, 'PNG')
        print(f"Created: {filename} ({size}x{size})")
    
    # Create .icns file
    icns_path = os.path.join(output_dir, "PDFKE.icns")
    try:
        result = subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path], 
                              check=True, capture_output=True, text=True)
        print(f"\n✓ Created PDFKE.icns")
        
        # Clean up iconset
        subprocess.run(['rm', '-rf', iconset_dir], check=True)
        
        return icns_path
    except subprocess.CalledProcessError as e:
        print(f"Error creating .icns: {e}")
        return None

if __name__ == "__main__":
    source_file = "/Users/hideki/Downloads/PDFKE.png"
    if os.path.exists(source_file):
        print("Creating final icon with exact macOS standards...")
        icns_file = create_standard_macos_icon(source_file, ".")
        if icns_file:
            print(f"✓ Final icon ready: {icns_file}")
        else:
            print("✗ Failed to create icon")
    else:
        print(f"Source file not found: {source_file}")