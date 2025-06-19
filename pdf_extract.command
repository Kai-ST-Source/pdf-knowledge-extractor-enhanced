#!/bin/bash
# PDF Knowledge Extractor - Command Line Interface

cd "$(dirname "$0")"

echo "================================"
echo "PDF Knowledge Extractor"
echo "================================"
echo ""
echo "PDFファイルをこのウィンドウにドラッグ&ドロップして、Enterキーを押してください。"
echo "または、PDFファイルのパスを入力してください。"
echo ""
echo "終了するには 'q' を入力してください。"
echo ""

while true; do
    echo -n "PDFファイル: "
    read -r pdf_path
    
    # Remove quotes if present (from drag and drop)
    pdf_path="${pdf_path%\'}"
    pdf_path="${pdf_path#\'}"
    pdf_path="${pdf_path%\"}"
    pdf_path="${pdf_path#\"}"
    
    if [ "$pdf_path" = "q" ] || [ "$pdf_path" = "Q" ]; then
        echo "終了します。"
        break
    fi
    
    if [ -z "$pdf_path" ]; then
        echo "ファイルパスを入力してください。"
        continue
    fi
    
    if [ ! -f "$pdf_path" ]; then
        echo "エラー: ファイルが見つかりません: $pdf_path"
        continue
    fi
    
    echo ""
    echo "処理中: $pdf_path"
    python3 src/app.py "$pdf_path"
    
    echo ""
    echo "処理が完了しました。結果は ~/Desktop/PDF knowledge extractor/ に保存されました。"
    echo ""
    echo "別のファイルを処理する場合は、ファイルをドラッグ&ドロップしてください。"
    echo ""
done