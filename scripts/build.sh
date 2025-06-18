#!/bin/bash

set -e  # Exit on any error

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$PROJECT_DIR/src"
DIST_DIR="$PROJECT_DIR/dist"
APP_NAME="PDF Knowledge Extractor"

echo "=== PDF Knowledge Extractor Build Script ==="
echo "Project Directory: $PROJECT_DIR"
echo "Source Directory: $SRC_DIR"
echo "Distribution Directory: $DIST_DIR"

# Check if we're in the right directory
if [ ! -f "$SRC_DIR/pdf_knowledge_extractor.py" ]; then
    echo "Error: pdf_knowledge_extractor.py not found in $SRC_DIR"
    exit 1
fi

if [ ! -f "$SRC_DIR/config.json" ]; then
    echo "Error: config.json not found in $SRC_DIR"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

# Check Python and PyInstaller
echo "Checking Python version..."
python3 --version

if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf "$DIST_DIR"
rm -rf build/
rm -rf *.spec

# Create dist directory
mkdir -p "$DIST_DIR"

# Build the executable
echo "Building executable with PyInstaller..."

pyinstaller \
    --name="pdf_knowledge_extractor" \
    --onefile \
    --windowed \
    --add-data "$SRC_DIR/config.json:." \
    --hidden-import="PIL._tkinter_finder" \
    --hidden-import="google.generativeai" \
    --hidden-import="pdf2image" \
    --hidden-import="fitz" \
    --hidden-import="openpyxl" \
    --hidden-import="yaml" \
    --hidden-import="pathvalidate" \
    --hidden-import="tqdm" \
    --collect-all="google.generativeai" \
    --noupx \
    "$SRC_DIR/pdf_knowledge_extractor.py"

if [ ! -f "$DIST_DIR/pdf_knowledge_extractor" ]; then
    echo "Error: Executable not created"
    exit 1
fi

echo "Executable created successfully!"

# Create macOS app bundle
echo "Creating macOS app bundle..."

APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Create app bundle structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy executable with proper name
cp "$DIST_DIR/pdf_knowledge_extractor" "$MACOS_DIR/PDF Knowledge Extractor"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.pdfextractor.app</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>PDF Knowledge Extractor</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>pdf</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>PDF Document</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
        </dict>
    </array>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

# No launcher script needed - the PyInstaller executable handles everything

# Create simple app icon (if none exists)
if [ ! -f "$RESOURCES_DIR/app_icon.icns" ]; then
    echo "Creating default app icon..."
    # Create a simple colored square as placeholder
    cat > "$RESOURCES_DIR/app_icon.icns" << 'EOF'
# Placeholder icon file
# In a real application, this would be a proper .icns file
EOF
fi

echo "App bundle created at: $APP_BUNDLE"

# Set executable permissions
chmod +x "$APP_BUNDLE/Contents/MacOS/PDF Knowledge Extractor"

# Verify the build
echo "=== Build Verification ==="
echo "Executable size: $(du -h "$DIST_DIR/pdf_knowledge_extractor" | cut -f1)"
echo "App bundle created: $APP_BUNDLE"

if [ -d "$APP_BUNDLE" ]; then
    echo "✅ macOS app bundle created successfully"
else
    echo "❌ Failed to create app bundle"
    exit 1
fi

echo "=== Build Complete ==="
echo "Standalone executable: $DIST_DIR/pdf_knowledge_extractor"
echo "macOS App: $APP_BUNDLE"
echo ""
echo "To install the app:"
echo "  cp -R \"$APP_BUNDLE\" /Applications/"
echo ""
echo "To test the executable:"
echo "  \"$DIST_DIR/pdf_knowledge_extractor\" --help"