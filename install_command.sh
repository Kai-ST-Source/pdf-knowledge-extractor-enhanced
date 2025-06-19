#!/bin/bash
# Install a global command for PDF extraction

# Create the command script
cat > /usr/local/bin/pdf-extract << 'EOF'
#!/bin/bash
cd /Users/hideki/pdf_knowledge_extractor_mac
python3 src/app.py "$@"
EOF

# Make it executable
chmod +x /usr/local/bin/pdf-extract

echo "pdf-extractコマンドがインストールされました。"
echo ""
echo "使用方法:"
echo "  pdf-extract file.pdf"
echo "  pdf-extract file1.pdf file2.pdf file3.pdf"
echo ""
echo "ターミナルからどこでも使用できます。"