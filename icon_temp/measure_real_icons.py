#!/usr/bin/env python3
"""
Actually measure real macOS app icons to determine exact content sizing
"""

from PIL import Image, ImageDraw
import numpy as np
import os
import subprocess

def extract_and_analyze_app_icon(app_path, app_name):
    """Extract and analyze an app's icon"""
    
    # Common icon file names
    icon_files = [
        "AppIcon.icns",
        "app.icns", 
        "icon.icns",
        f"{app_name}.icns"
    ]
    
    resources_path = os.path.join(app_path, "Contents", "Resources")
    if not os.path.exists(resources_path):
        return None
    
    # Find the icon file
    icon_path = None
    for icon_file in icon_files:
        potential_path = os.path.join(resources_path, icon_file)
        if os.path.exists(potential_path):
            icon_path = potential_path
            break
    
    if not icon_path:
        # List all .icns files
        try:
            icns_files = [f for f in os.listdir(resources_path) if f.endswith('.icns')]
            if icns_files:
                icon_path = os.path.join(resources_path, icns_files[0])
        except:
            return None
    
    if not icon_path:
        return None
    
    # Extract iconset
    iconset_dir = f"{app_name}_analysis.iconset"
    try:
        subprocess.run(['iconutil', '-c', 'iconset', icon_path, '-o', iconset_dir], 
                      check=True, capture_output=True)
    except:
        return None
    
    # Analyze 128x128 version (most common size for analysis)
    icon_128_path = os.path.join(iconset_dir, "icon_128x128.png")
    if not os.path.exists(icon_128_path):
        # Try other naming conventions
        possible_names = [
            "icon_128x128@2x.png",
            "icon_64x64@2x.png"
        ]
        for name in possible_names:
            test_path = os.path.join(iconset_dir, name)
            if os.path.exists(test_path):
                icon_128_path = test_path
                break
    
    if not os.path.exists(icon_128_path):
        subprocess.run(['rm', '-rf', iconset_dir], capture_output=True)
        return None
    
    # Analyze the icon
    img = Image.open(icon_128_path).convert('RGBA')
    width, height = img.size
    
    # Find actual content bounds
    img_array = np.array(img)
    alpha_channel = img_array[:, :, 3]
    
    # Find non-transparent and non-white pixels (actual content)
    rgb_channels = img_array[:, :, :3]
    white_pixels = np.all(rgb_channels > 250, axis=2)  # Nearly white
    content_mask = (alpha_channel > 10) & (~white_pixels)  # Content that's not white/transparent
    
    if np.any(content_mask):
        rows = np.any(content_mask, axis=1)
        cols = np.any(content_mask, axis=0)
        
        if np.any(rows) and np.any(cols):
            top, bottom = np.where(rows)[0][[0, -1]]
            left, right = np.where(cols)[0][[0, -1]]
            
            content_width = right - left + 1
            content_height = bottom - top + 1
            content_ratio = min(content_width / width, content_height / height)
        else:
            content_ratio = 0
    else:
        content_ratio = 0
    
    # Clean up
    subprocess.run(['rm', '-rf', iconset_dir], capture_output=True)
    
    return {
        'app_name': app_name,
        'size': f"{width}x{height}",
        'content_ratio': content_ratio,
        'content_percentage': content_ratio * 100
    }

def analyze_multiple_apps():
    """Analyze multiple standard macOS apps"""
    
    standard_apps = [
        ("/Applications/Safari.app", "Safari"),
        ("/Applications/Mail.app", "Mail"),
        ("/Applications/Calendar.app", "Calendar"),
        ("/Applications/Contacts.app", "Contacts"),
        ("/Applications/Notes.app", "Notes"),
        ("/Applications/Calculator.app", "Calculator"),
        ("/Applications/TextEdit.app", "TextEdit"),
        ("/System/Applications/System Preferences.app", "System Preferences"),
    ]
    
    results = []
    
    print("Analyzing standard macOS app icons...")
    print("=" * 50)
    
    for app_path, app_name in standard_apps:
        if os.path.exists(app_path):
            result = extract_and_analyze_app_icon(app_path, app_name)
            if result:
                results.append(result)
                print(f"{app_name:20} | Content: {result['content_percentage']:5.1f}%")
            else:
                print(f"{app_name:20} | Failed to analyze")
    
    if results:
        content_ratios = [r['content_ratio'] for r in results]
        avg_ratio = np.mean(content_ratios)
        min_ratio = np.min(content_ratios)
        max_ratio = np.max(content_ratios)
        
        print("=" * 50)
        print(f"Average content ratio: {avg_ratio:.2f} ({avg_ratio*100:.0f}%)")
        print(f"Range: {min_ratio:.2f} - {max_ratio:.2f} ({min_ratio*100:.0f}% - {max_ratio*100:.0f}%)")
        print("=" * 50)
        
        # Recommend a conservative ratio
        recommended_ratio = min_ratio * 0.95  # Be 5% more conservative than the smallest
        print(f"Recommended ratio for PDFKE: {recommended_ratio:.2f} ({recommended_ratio*100:.0f}%)")
        
        return recommended_ratio
    
    return 0.65  # Very conservative fallback

def create_correctly_sized_icon(source_path, output_dir, content_ratio):
    """Create icon with the exact content ratio of real macOS apps"""
    
    print(f"\nCreating icon with {content_ratio*100:.0f}% content ratio...")
    
    original = Image.open(source_path).convert('RGBA')
    
    # macOS icon configs
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
        # White background
        background = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        
        # Calculate content size using measured ratio
        content_size = int(size * content_ratio)
        
        # Resize and center
        resized = original.resize((content_size, content_size), Image.Resampling.LANCZOS)
        x = (size - content_size) // 2
        y = (size - content_size) // 2
        
        background.paste(resized, (x, y), resized)
        
        # Very subtle corners
        corner_radius = max(1, int(size * 0.06))  # Even more subtle
        
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=255)
        
        final_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        final_image.paste(background, (0, 0))
        final_image.putalpha(mask)
        
        output_path = os.path.join(iconset_dir, filename)
        final_image.save(output_path, 'PNG')
    
    # Create .icns
    icns_path = os.path.join(output_dir, "PDFKE_correct.icns")
    try:
        subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path], check=True)
        subprocess.run(['rm', '-rf', iconset_dir], check=True)
        return icns_path
    except:
        return None

if __name__ == "__main__":
    # Analyze real apps first
    recommended_ratio = analyze_multiple_apps()
    
    # Create icon with correct ratio
    source_file = "/Users/hideki/Downloads/PDFKE.png"
    if os.path.exists(source_file):
        icns_file = create_correctly_sized_icon(source_file, ".", recommended_ratio)
        if icns_file:
            print(f"\n✓ Created properly sized icon: {icns_file}")
            print(f"Content ratio: {recommended_ratio*100:.0f}% (matches real macOS apps)")
        else:
            print("✗ Failed to create icon")
    else:
        print(f"Source file not found: {source_file}")