#!/bin/bash
# Create a better PDF Knowledge Extractor Droplet with GUI

APP_NAME="PDF Knowledge Extractor"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$CURRENT_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_PATH/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

echo "Creating $APP_NAME.app..."

# Clean up existing app
rm -rf "$APP_PATH"

# Create app bundle structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist with proper droplet support
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.pdfextractor.app</string>
    <key>CFBundleName</key>
    <string>PDF Knowledge Extractor</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
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
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create the enhanced launch script with GUI support
cat > "$MACOS_DIR/launch" << 'EOF'
#!/bin/bash

# Get the directory where this app is located
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="$APP_DIR"

# Change to source directory
cd "$SOURCE_DIR"

# Function to show GUI selection when no files provided
show_gui() {
    # Try Python GUI first
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os

# Hide the root window initially
root = tk.Tk()
root.withdraw()

try:
    # Ask user to select PDF files
    file_paths = filedialog.askopenfilenames(
        title='Select PDF files to process',
        filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')]
    )
    
    if file_paths:
        # Process each selected file
        for file_path in file_paths:
            print(f'Processing: {file_path}')
            try:
                result = subprocess.run([
                    sys.executable, 'src/app.py', file_path
                ], capture_output=True, text=True, cwd='$SOURCE_DIR')
                
                if result.returncode != 0:
                    print(f'Error processing {file_path}: {result.stderr}')
                else:
                    print(f'Successfully processed: {file_path}')
            except Exception as e:
                print(f'Exception processing {file_path}: {e}')
        
        # Show completion message
        messagebox.showinfo('PDF Knowledge Extractor', 
                          f'Processing completed for {len(file_paths)} file(s).\n\nResults saved to ~/Desktop/PDF knowledge extractor/')
    else:
        print('No files selected')
        
except Exception as e:
    print(f'GUI error: {e}')
    # Fallback to command line
    messagebox.showerror('Error', f'GUI error: {e}\nPlease use command line interface.')

root.destroy()
"
    else
        echo "Python3 not available for GUI"
        return 1
    fi
}

# Check if files were passed as arguments
if [ $# -gt 0 ]; then
    echo "Processing dropped files..."
    for file in "$@"; do
        if [[ "$file" == *.pdf ]]; then
            echo "Processing: $file"
            python3 src/app.py "$file"
        else
            echo "Skipping non-PDF file: $file"
        fi
    done
    
    # Show notification
    osascript -e "display notification \"Processing completed\" with title \"PDF Knowledge Extractor\""
else
    echo "No files provided, showing file selection dialog..."
    show_gui
fi
EOF

chmod +x "$MACOS_DIR/launch"

# Create a simple icon (you can replace this with a custom icon later)
cat > "$RESOURCES_DIR/app_icon.icns" << 'EOF'
# This is a placeholder - in a real app you'd have a proper .icns file
EOF

echo "✅ $APP_NAME.app created successfully at: $APP_PATH"
echo ""
echo "Features:"
echo "1. ダブルクリックでファイル選択GUI起動"
echo "2. PDFファイルのドラッグ&ドロップ対応"
echo "3. 処理完了通知"
echo "4. 全ての要求機能実装済み:"
echo "   - テキスト抽出（見出し構造保持）"
echo "   - 表データ（Markdown形式）"
echo "   - OCR（日本語対応）"
echo "   - ヘッダー、フッター、ページ番号"
echo "   - 脚注・注釈"
echo "   - PDFメタデータ"
echo ""
echo "出力形式: .md, .xlsx, .json, .txt"
echo "保存先: ~/Desktop/PDF knowledge extractor/"
echo ""