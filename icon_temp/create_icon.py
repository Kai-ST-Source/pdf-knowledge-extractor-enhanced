#!/usr/bin/env python3
"""
PDFKE Icon Generator
Creates a macOS-compliant icon with white background, scaled content, and rounded corners.
"""

import os
import sys
from PIL import Image, ImageDraw
import subprocess
import argparse

# macOS icon sizes for .icns file
ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]

def create_rounded_rectangle_mask(size, radius):
    """Create a mask for rounded rectangle"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)
    return mask

def process_icon(source_path, output_dir, scale_factor=0.85, corner_radius_factor=0.1):
    """
    Process the source icon to create a macOS-compliant version
    
    Args:
        source_path: Path to source PNG file
        output_dir: Directory to save processed icons
        scale_factor: How much to scale down the original icon (0.85 = 85%)
        corner_radius_factor: Corner radius as a factor of image size (0.1 = 10%)
    """
    
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Load the original image
    original = Image.open(source_path).convert('RGBA')
    print(f"Original image size: {original.size}")
    
    # Create icons for each required size
    icon_files = []
    
    for size in ICON_SIZES:
        # Create white background
        background = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        
        # Calculate scaled size for the original icon
        scaled_size = int(size * scale_factor)
        
        # Resize original image to scaled size
        resized_original = original.resize((scaled_size, scaled_size), Image.Resampling.LANCZOS)
        
        # Calculate position to center the scaled image
        x = (size - scaled_size) // 2
        y = (size - scaled_size) // 2
        
        # Paste the scaled image onto the white background
        background.paste(resized_original, (x, y), resized_original)
        
        # Apply rounded corners
        corner_radius = int(size * corner_radius_factor)
        mask = create_rounded_rectangle_mask((size, size), corner_radius)
        
        # Apply the mask to create rounded corners
        final_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        final_image.paste(background, (0, 0))
        final_image.putalpha(mask)
        
        # Save the processed icon
        output_path = os.path.join(output_dir, f"icon_{size}x{size}.png")
        final_image.save(output_path, 'PNG')
        icon_files.append(output_path)
        print(f"Created {size}x{size} icon: {output_path}")
    
    return icon_files

def create_icns_file(icon_files, output_path):
    """Create .icns file from PNG files using iconutil"""
    
    # Create iconset directory
    iconset_dir = output_path.replace('.icns', '.iconset')
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Copy files to iconset directory with proper naming
    iconset_files = []
    for icon_file in icon_files:
        size = os.path.basename(icon_file).split('_')[1].split('.')[0]  # Extract size from filename
        size_num = int(size.split('x')[0])
        
        # Standard naming convention for iconset
        if size_num <= 32:
            iconset_name = f"icon_{size}.png"
        else:
            # For larger sizes, also create @2x versions for retina displays
            iconset_name = f"icon_{size_num//2}x{size_num//2}@2x.png"
            
        iconset_path = os.path.join(iconset_dir, iconset_name)
        subprocess.run(['cp', icon_file, iconset_path], check=True)
        iconset_files.append(iconset_path)
        
        # Also create standard size versions
        if size_num > 32:
            standard_name = f"icon_{size}.png"
            standard_path = os.path.join(iconset_dir, standard_name)
            subprocess.run(['cp', icon_file, standard_path], check=True)
            iconset_files.append(standard_path)
    
    # Create .icns file using iconutil
    try:
        result = subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', output_path], 
                              check=True, capture_output=True, text=True)
        print(f"Successfully created .icns file: {output_path}")
        
        # Clean up iconset directory
        subprocess.run(['rm', '-rf', iconset_dir], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating .icns file: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def find_app_resources_folder():
    """Find the app's Resources folder"""
    possible_paths = [
        "/Users/hideki/pdf_knowledge_extractor_mac/PDF Knowledge Extractor.app/Contents/Resources",
        "/Users/hideki/pdf_knowledge_extractor_mac/build/PDF Knowledge Extractor.app/Contents/Resources",
        "/Users/hideki/pdf_knowledge_extractor_mac/dist/PDF Knowledge Extractor.app/Contents/Resources"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Create macOS app icon from source PNG')
    parser.add_argument('source', help='Path to source PNG file')
    parser.add_argument('--scale', type=float, default=0.85, help='Scale factor for icon content (default: 0.85)')
    parser.add_argument('--corner-radius', type=float, default=0.1, help='Corner radius factor (default: 0.1)')
    parser.add_argument('--output-dir', default='.', help='Output directory for processed icons')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        print(f"Processing icon from: {args.source}")
        print(f"Scale factor: {args.scale}")
        print(f"Corner radius factor: {args.corner_radius}")
        
        # Process the icon
        icon_files = process_icon(args.source, args.output_dir, args.scale, args.corner_radius)
        
        # Create .icns file
        icns_path = os.path.join(args.output_dir, 'app_icon.icns')
        if create_icns_file(icon_files, icns_path):
            print(f"\n✓ Successfully created .icns file: {icns_path}")
            
            # Try to copy to app's Resources folder
            resources_folder = find_app_resources_folder()
            if resources_folder:
                app_icon_path = os.path.join(resources_folder, 'app_icon.icns')
                try:
                    subprocess.run(['cp', icns_path, app_icon_path], check=True)
                    print(f"✓ Copied icon to app Resources folder: {app_icon_path}")
                except subprocess.CalledProcessError as e:
                    print(f"⚠ Could not copy to Resources folder: {e}")
            else:
                print("⚠ Could not find app Resources folder")
        
        print(f"\n✓ Icon processing complete!")
        print(f"Generated {len(icon_files)} icon sizes")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()