#!/bin/bash
# Create a simple "Open With" application

APP_DIR="/Applications/PDF Knowledge Extractor.app"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create Info.plist for file association
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>pdf_extractor</string>
    <key>CFBundleIdentifier</key>
    <string>com.pdf.knowledge.extractor</string>
    <key>CFBundleName</key>
    <string>PDF Knowledge Extractor</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
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
            <key>LSItemContentTypes</key>
            <array>
                <string>com.adobe.pdf</string>
            </array>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
        </dict>
    </array>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create the executable script
cat > "$APP_DIR/Contents/MacOS/pdf_extractor" << 'EOF'
#!/bin/bash

# Change to the project directory
cd /Users/hideki/pdf_knowledge_extractor_mac

# Function to show notification
show_notification() {
    osascript -e "display notification \"$2\" with title \"PDF Knowledge Extractor\" subtitle \"$1\""
}

# Function to show error dialog
show_error() {
    osascript -e "display dialog \"エラー: $1\" buttons {\"OK\"} default button 1 with icon stop"
}

# Function to show success dialog
show_success() {
    osascript -e "display dialog \"PDFの処理が完了しました。\\n\\n結果は以下のフォルダに保存されました:\\n~/Desktop/PDF knowledge extractor/\" buttons {\"フォルダを開く\", \"OK\"} default button 2"
    if [ $? -eq 1 ]; then
        # User clicked "フォルダを開く"
        open ~/Desktop/PDF\ knowledge\ extractor/
    fi
}

if [ $# -eq 0 ]; then
    # No files provided, show file selection dialog
    FILE=$(osascript -e 'tell application "System Events" to set theFile to choose file with prompt "PDFファイルを選択してください:" of type {"pdf"}' -e 'POSIX path of theFile' 2>/dev/null)
    
    if [ -z "$FILE" ]; then
        exit 0  # User cancelled
    fi
    
    set -- "$FILE"
fi

# Process each file
SUCCESS_COUNT=0
TOTAL_COUNT=$#

for file in "$@"; do
    if [[ "$file" == *.pdf ]]; then
        show_notification "$(basename "$file")" "処理中..."
        
        if python3 src/app.py "$file" 2>/dev/null; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            show_notification "$(basename "$file")" "処理完了"
        else
            show_error "ファイルの処理に失敗しました: $(basename "$file")"
        fi
    else
        show_error "PDFファイルのみ処理できます: $(basename "$file")"
    fi
done

if [ $SUCCESS_COUNT -gt 0 ]; then
    if [ $SUCCESS_COUNT -eq 1 ]; then
        show_success
    else
        osascript -e "display dialog \"${SUCCESS_COUNT}個のPDFファイルの処理が完了しました。\\n\\n結果は以下のフォルダに保存されました:\\n~/Desktop/PDF knowledge extractor/\" buttons {\"フォルダを開く\", \"OK\"} default button 2"
        if [ $? -eq 1 ]; then
            open ~/Desktop/PDF\ knowledge\ extractor/
        fi
    fi
fi
EOF

# Make the script executable
chmod +x "$APP_DIR/Contents/MacOS/pdf_extractor"

echo "「開く」アプリケーションが作成されました: $APP_DIR"
echo ""
echo "使用方法:"
echo "1. Finderでhoge.pdfを右クリック"
echo "2. '開く' > 'PDF Knowledge Extractor' を選択"
echo "または"
echo "3. アプリケーションフォルダから 'PDF Knowledge Extractor' をダブルクリックしてファイルを選択"