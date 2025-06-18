#!/bin/bash

echo "最終版PDF知見抽出ワークフローを作成中..."

# ワークフローディレクトリを作成
WORKFLOW_DIR=~/Library/Services/PDF知見抽出.workflow
CONTENTS_DIR="$WORKFLOW_DIR/Contents"

mkdir -p "$CONTENTS_DIR"

# Info.plistを作成
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>com.apple.Automator.PDF知見抽出</string>
	<key>CFBundleName</key>
	<string>PDF知見抽出</string>
	<key>NSServices</key>
	<array>
		<dict>
			<key>NSMenuItem</key>
			<dict>
				<key>default</key>
				<string>PDF知見抽出</string>
			</dict>
			<key>NSMessage</key>
			<string>runWorkflowAsService</string>
			<key>NSRequiredContext</key>
			<dict>
				<key>NSApplicationIdentifier</key>
				<string>com.apple.finder</string>
			</dict>
			<key>NSSendFileTypes</key>
			<array>
				<string>com.adobe.pdf</string>
			</array>
		</dict>
	</array>
</dict>
</plist>
EOF

# document.wflowを作成（直接実行方式）
cat > "$CONTENTS_DIR/document.wflow" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AMApplicationBuild</key>
	<string>523</string>
	<key>AMApplicationVersion</key>
	<string>2.10</string>
	<key>AMDocumentVersion</key>
	<string>2</string>
	<key>actions</key>
	<array>
		<dict>
			<key>action</key>
			<dict>
				<key>AMAccepts</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Optional</key>
					<true/>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.path</string>
					</array>
				</dict>
				<key>AMActionVersion</key>
				<string>1.1.2</string>
				<key>AMApplication</key>
				<array>
					<string>Automator</string>
				</array>
				<key>AMParameterProperties</key>
				<dict>
					<key>COMMAND_STRING</key>
					<dict/>
					<key>CheckedForUserDefaultShell</key>
					<dict/>
					<key>inputMethod</key>
					<dict/>
					<key>shell</key>
					<dict/>
					<key>source</key>
					<dict/>
				</dict>
				<key>AMProvides</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.string</string>
					</array>
				</dict>
				<key>ActionBundlePath</key>
				<string>/System/Library/Automator/Run Shell Script.action</string>
				<key>ActionName</key>
				<string>シェルスクリプトを実行</string>
				<key>ActionParameters</key>
				<dict>
					<key>COMMAND_STRING</key>
					<string>#!/bin/bash

# PDF知見抽出スクリプト（直接実行版）

show_notification() {
    osascript -e "display notification \"$2\" with title \"$1\"" 2>/dev/null || true
}

show_alert() {
    osascript -e "display alert \"PDF知見抽出\" message \"$1\" buttons {\"OK\"} default button \"OK\"" 2>/dev/null || true
}

for file in "$@"
do
    # PDFファイルチェック
    if [[ "$file" != *.pdf ]]; then
        continue
    fi
    
    # ファイル存在確認
    if [[ ! -f "$file" ]]; then
        show_alert "ファイルが見つかりません: $file"
        continue
    fi
    
    # アプリケーション実行ファイルのパス
    APP_PATH="/Applications/PDF Knowledge Extractor.app/Contents/MacOS/pdf_knowledge_extractor"
    
    # アプリ存在確認
    if [[ ! -f "$APP_PATH" ]]; then
        show_alert "PDF Knowledge Extractorアプリが見つかりません。\n\nアプリケーションフォルダにインストールされているか確認してください。"
        exit 1
    fi
    
    # 設定ファイルのパス設定
    CONFIG_PATH1="/Users/hideki/pdf_knowledge_extractor_mac/src/config.json"
    CONFIG_PATH2="$(dirname "$APP_PATH")/config.json"
    
    CONFIG_ARG=""
    if [[ -f "$CONFIG_PATH1" ]]; then
        CONFIG_ARG="--config $CONFIG_PATH1"
    elif [[ -f "$CONFIG_PATH2" ]]; then
        CONFIG_ARG="--config $CONFIG_PATH2"
    fi
    
    # 処理開始通知
    show_notification "PDF知見抽出" "処理を開始しました: $(basename "$file")"
    
    # バックグラウンドで実行
    (
        cd "$(dirname "$file")" || exit 1
        "$APP_PATH" $CONFIG_ARG "$file" > /dev/null 2>&1
        
        if [[ $? -eq 0 ]]; then
            show_notification "PDF知見抽出" "処理が完了しました: $(basename "$file")"
        else
            show_notification "PDF知見抽出" "エラーが発生しました: $(basename "$file")"
        fi
    ) &
    
done

# 全体完了通知（複数ファイルの場合）
if [[ $# -gt 1 ]]; then
    show_notification "PDF知見抽出" "全ファイルの処理を開始しました"
fi</string>
					<key>CheckedForUserDefaultShell</key>
					<true/>
					<key>inputMethod</key>
					<integer>1</integer>
					<key>shell</key>
					<string>/bin/bash</string>
					<key>source</key>
					<string></string>
				</dict>
				<key>BundleIdentifier</key>
				<string>com.apple.RunShellScript</string>
				<key>CFBundleVersion</key>
				<string>1.1.2</string>
				<key>CanShowSelectedItemsWhenRun</key>
				<false/>
				<key>CanShowWhenRun</key>
				<true/>
				<key>Category</key>
				<array>
					<string>AMCategoryUtilities</string>
				</array>
				<key>Class Name</key>
				<string>RunShellScriptAction</string>
				<key>InputUUID</key>
				<string>E5FD7B5D-8DCE-4F77-8D3C-81A7A14E55B0</string>
				<key>Keywords</key>
				<array>
					<string>シェル</string>
					<string>スクリプト</string>
					<string>コマンド</string>
					<string>実行</string>
					<string>Unix</string>
				</array>
				<key>OutputUUID</key>
				<string>32E3D7B0-6F47-4A87-8B7C-9E5F5A5C5C5C</string>
				<key>UUID</key>
				<string>1F5A6F5C-8F5D-4F77-8D3C-81A7A14E55B0</string>
				<key>UnlocalizedApplications</key>
				<array>
					<string>Automator</string>
				</array>
			</dict>
		</dict>
	</array>
	<key>connectors</key>
	<dict/>
	<key>workflowMetaData</key>
	<dict>
		<key>applicationBundleIDsByPath</key>
		<dict/>
		<key>applicationPaths</key>
		<array/>
		<key>inputTypeIdentifier</key>
		<string>com.apple.Automator.fileSystemObject.PDF</string>
		<key>outputTypeIdentifier</key>
		<string>com.apple.Automator.nothing</string>
		<key>presentationMode</key>
		<integer>15</integer>
		<key>processesInput</key>
		<integer>0</integer>
		<key>serviceInputTypeIdentifier</key>
		<string>com.apple.Automator.fileSystemObject.PDF</string>
		<key>serviceOutputTypeIdentifier</key>
		<string>com.apple.Automator.nothing</string>
		<key>serviceProcessesInput</key>
		<integer>0</integer>
		<key>systemImageName</key>
		<string>NSActionTemplate</string>
		<key>useAutomaticInputType</key>
		<integer>0</integer>
		<key>workflowTypeIdentifier</key>
		<string>com.apple.Automator.servicesMenu</string>
	</dict>
</dict>
</plist>
EOF

echo "最終版ワークフローが作成されました: $WORKFLOW_DIR"
echo ""
echo "改善点:"
echo "- 外部Pythonスクリプト不要（セキュリティ問題解決）"
echo "- 直接シェルスクリプト実行"
echo "- 設定ファイル自動検出"
echo "- 詳細なエラーハンドリング"
echo "- ファイル毎の進捗通知"
echo ""
echo "使用方法:"
echo "1. FinderでPDFファイルを右クリック"
echo "2. 'クイックアクション' → 'PDF知見抽出' を選択"