# PDFKE Icon Generator - Usage Instructions

## Overview
The icon generator has been successfully set up and tested. It creates macOS-compliant app icons with:
- White background
- 85% scaled icon content (with padding around edges)
- Rounded corners
- All required macOS icon sizes (16x16 to 1024x1024)

## Quick Usage

When you have your PDFKE.png file ready, run:

```bash
cd /Users/hideki/pdf_knowledge_extractor_mac/icon_temp
python3 create_icon.py /path/to/your/PDFKE.png
```

## What the script does:

1. **Loads your source PNG file**
2. **Creates white backgrounds** for each required icon size
3. **Scales your icon to 85%** of the target size (leaving 15% for padding)
4. **Centers the scaled icon** on the white background
5. **Applies rounded corners** (10% of the icon size as radius)
6. **Generates all macOS icon sizes**: 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
7. **Creates the .icns file** using macOS iconutil
8. **Automatically copies** the .icns file to your app's Resources folder
9. **Cleans up** temporary files

## Customization Options

```bash
# Custom scale factor (default is 0.85 = 85%)
python3 create_icon.py /path/to/PDFKE.png --scale 0.8

# Custom corner radius (default is 0.1 = 10% of icon size)
python3 create_icon.py /path/to/PDFKE.png --corner-radius 0.15

# Custom output directory
python3 create_icon.py /path/to/PDFKE.png --output-dir /custom/path
```

## Test Results

The script has been tested with your existing icon source file and successfully:
- ✅ Generated all 7 required icon sizes
- ✅ Created the app_icon.icns file (1.7MB)
- ✅ Copied it to your app's Resources folder
- ✅ Applied proper white background, scaling, and rounded corners

## Files in this directory:

- `create_icon.py` - Main icon generation script
- `cleanup.py` - Cleans up temporary files after processing
- `app_icon.icns` - The generated icon file (ready to use)
- `INSTRUCTIONS.md` - This file

## Ready to use!

Your icon generation system is ready. Just provide the path to your PDFKE.png file when you have it.