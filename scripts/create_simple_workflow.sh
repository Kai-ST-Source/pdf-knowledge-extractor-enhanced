#!/bin/bash

echo "シンプルなPDF知見抽出ワークフローを作成中..."

# まずPythonスクリプトを作成
SCRIPT_PATH=~/Documents/pdf_extractor_simple.py

cat > "$SCRIPT_PATH" << 'EOF'
#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
from pathlib import Path

def show_notification(title, message):
    """macOS通知を表示"""
    try:
        subprocess.run([
            'osascript', '-e',
            f'display notification "{message}" with title "{title}"'
        ], check=True)
    except:
        pass

def show_alert(message):
    """macOSアラートを表示"""
    try:
        subprocess.run([
            'osascript', '-e',
            f'display alert "PDF知見抽出" message "{message}" buttons {{"OK"}} default button "OK"'
        ], check=True)
    except:
        print(message)

def main():
    if len(sys.argv) < 2:
        show_alert("PDFファイルが指定されていません。")
        return
    
    pdf_path = sys.argv[1]
    
    # PDFファイルかチェック
    if not pdf_path.lower().endswith('.pdf'):
        show_alert("PDFファイルを選択してください。")
        return
    
    if not os.path.exists(pdf_path):
        show_alert("ファイルが見つかりません。")
        return
    
    # アプリケーションの実行ファイルを確認
    app_path = "/Applications/PDF Knowledge Extractor.app/Contents/MacOS/pdf_knowledge_extractor"
    
    if not os.path.exists(app_path):
        show_alert("PDF Knowledge Extractorアプリが見つかりません。\\n\\nアプリケーションフォルダにインストールされているか確認してください。")
        return
    
    try:
        # バックグラウンドで実行
        show_notification("PDF知見抽出", "処理を開始しました...")
        
        # 作業ディレクトリを設定（設定ファイルのため）
        work_dir = os.path.expanduser("~/pdf_knowledge_extractor_mac/src")
        if not os.path.exists(work_dir):
            work_dir = os.path.dirname(app_path)
        
        # アプリを実行
        subprocess.Popen([
            app_path,
            pdf_path
        ], cwd=work_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    except Exception as e:
        show_alert(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
EOF

chmod +x "$SCRIPT_PATH"

echo "Pythonスクリプトを作成しました: $SCRIPT_PATH"

# 次にAutomatorワークフローを作成
osascript << 'APPLESCRIPT'
tell application "Automator"
    -- 新しいサービスワークフローを作成
    set newWorkflow to make new service
    
    -- サービスの設定
    set service receives to {"PDF files"}
    set service input to "files and folders" of newWorkflow
    
    -- "Run Shell Script"アクションを追加
    tell newWorkflow
        set shellAction to make new action with properties {name:"Run Shell Script"}
        
        -- スクリプトの設定
        set shell to "/bin/bash" of shellAction
        set pass input to "as arguments" of shellAction
        set script to "#!/bin/bash
for file in \"$@\"
do
    python3 ~/Documents/pdf_extractor_simple.py \"$file\"
done" of shellAction
    end tell
    
    -- ワークフローを保存
    set savePath to (path to library folder from user domain as text) & "Services:PDF知見抽出.workflow"
    save newWorkflow in file savePath
    
    quit
end tell
APPLESCRIPT

echo "Automatorワークフローが作成されました。"
echo ""
echo "使用方法:"
echo "1. FinderでPDFファイルを右クリック"
echo "2. 'サービス' → 'PDF知見抽出' を選択"
echo ""
echo "トラブルシューティング:"
echo "- 'サービス' メニューが表示されない場合は、システム環境設定 > 機能拡張 > Finder拡張 を確認"
echo "- ワークフローが表示されない場合は、一度ログアウト/ログインしてください"