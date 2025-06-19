#!/bin/bash
# Create a drag-and-drop app for PDF extraction

cat > /tmp/PDFExtractor.applescript << 'EOF'
on open theItems
    repeat with anItem in theItems
        set itemPath to POSIX path of anItem
        if itemPath ends with ".pdf" then
            do shell script "cd /Users/hideki/pdf_knowledge_extractor_mac && python3 src/app.py '" & itemPath & "'"
            display notification "PDFの処理が完了しました: " & itemPath with title "PDF Knowledge Extractor"
        else
            display dialog "PDFファイルのみ処理できます。" buttons {"OK"} default button 1
        end if
    end repeat
end open

on run
    display dialog "PDFファイルをこのアプリケーションにドラッグ&ドロップしてください。" buttons {"OK"} default button 1
end run
EOF

# Compile the AppleScript to an app
osacompile -o "/Applications/PDF Extractor Droplet.app" /tmp/PDFExtractor.applescript

echo "ドロップレットアプリが作成されました: /Applications/PDF Extractor Droplet.app"