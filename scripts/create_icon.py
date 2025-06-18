#!/usr/bin/env python3
"""
Create app icon for PDF Knowledge Extractor.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw
import shutil


class IconCreator:
    """Create macOS app icon."""
    
    def __init__(self):
        """Initialize icon creator."""
        self.project_root = Path(__file__).parent.parent
        self.docs_dir = self.project_root / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
    def create_base_icon(self, size: int = 1024) -> Path:
        """Create base icon image from ChatGPT source with macOS rounded corners.
        
        Args:
            size: Icon size in pixels
            
        Returns:
            Path to created icon image
        """
        # Check if source image exists
        source_path = self.docs_dir / "icon_source.png"
        if not source_path.exists():
            print(f"❌ Source image not found: {source_path}")
            print("Please copy the ChatGPT image to docs/icon_source.png")
            return None
            
        try:
            # Load and process the source image
            source_img = Image.open(source_path)
            
            # Convert to RGBA if needed
            if source_img.mode != 'RGBA':
                source_img = source_img.convert('RGBA')
            
            # Resize to target size while maintaining aspect ratio
            source_img = source_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Apply macOS-style rounded corners
            rounded_img = self._apply_macos_rounded_corners(source_img, size)
            
            # Save processed icon
            icon_path = self.docs_dir / "icon.png"
            rounded_img.save(icon_path, 'PNG')
            print(f"✅ Created base icon from ChatGPT source with macOS rounded corners: {icon_path}")
            
            return icon_path
            
        except Exception as e:
            print(f"❌ Error processing source image: {e}")
            return None
    
    def _apply_macos_rounded_corners(self, img: Image.Image, size: int) -> Image.Image:
        """Apply macOS-style rounded corners to an image.
        
        Args:
            img: Source image
            size: Target size
            
        Returns:
            Image with rounded corners
        """
        # Create a mask with rounded corners
        # macOS uses approximately 22% corner radius for app icons
        corner_radius = int(size * 0.22)
        
        # Create mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle on mask
        mask_draw.rounded_rectangle(
            [0, 0, size-1, size-1], 
            radius=corner_radius, 
            fill=255
        )
        
        # Create output image with transparency
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Apply the mask to the source image
        # Convert mask to RGBA for compositing
        mask_rgba = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        mask_rgba.paste(img, (0, 0))
        
        # Apply alpha mask
        mask_rgba.putalpha(mask)
        
        return mask_rgba
        
    def create_iconset(self, base_icon: Path) -> Path:
        """Create iconset for macOS.
        
        Args:
            base_icon: Path to base icon image
            
        Returns:
            Path to iconset directory
        """
        iconset_dir = self.docs_dir / "AppIcon.iconset"
        if iconset_dir.exists():
            shutil.rmtree(iconset_dir)
        iconset_dir.mkdir()
        
        # macOS icon sizes
        sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]
        
        # Load base image
        base_img = Image.open(base_icon)
        
        for size, filename in sizes:
            resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
            output_path = iconset_dir / filename
            resized.save(output_path, 'PNG')
            print(f"   Created {filename} ({size}x{size})")
            
        print(f"✅ Created iconset: {iconset_dir}")
        return iconset_dir
        
    def create_icns(self, iconset_dir: Path) -> Path:
        """Create .icns file from iconset.
        
        Args:
            iconset_dir: Path to iconset directory
            
        Returns:
            Path to created .icns file
        """
        icns_path = self.docs_dir / "icon.icns"
        
        try:
            # Use iconutil to create .icns file
            subprocess.run([
                'iconutil', '-c', 'icns', '-o', str(icns_path), str(iconset_dir)
            ], check=True)
            
            print(f"✅ Created .icns file: {icns_path}")
            return icns_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating .icns file: {e}")
            return None
        except FileNotFoundError:
            print("❌ iconutil not found. Please ensure you're running on macOS.")
            return None
            
    def create_icon(self):
        """Create complete app icon."""
        print("🎨 Creating PDF Knowledge Extractor app icon from ChatGPT source...")
        
        # Create base icon
        base_icon = self.create_base_icon()
        if not base_icon:
            return
        
        # Create iconset
        iconset_dir = self.create_iconset(base_icon)
        if not iconset_dir:
            return
        
        # Create .icns file
        icns_path = self.create_icns(iconset_dir)
        
        if icns_path and icns_path.exists():
            print(f"\n🎉 App icon created successfully from ChatGPT source!")
            print(f"   Source: {self.docs_dir / 'icon_source.png'}")
            print(f"   Base icon: {base_icon}")
            print(f"   .icns file: {icns_path}")
            print(f"\nThe new icon will be used in the next app build.")
        else:
            print("\n❌ Failed to create .icns file.")


def main():
    """Main function."""
    creator = IconCreator()
    creator.create_icon()


if __name__ == '__main__':
    main()