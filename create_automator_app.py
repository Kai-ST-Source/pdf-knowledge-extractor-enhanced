#!/usr/bin/env python3
"""
Create an Automator-based application using Python
"""

import os
import tempfile
import subprocess

# Create a temporary AppleScript
applescript_content = '''
on run {input, parameters}
    try
        repeat with anItem in input
            set itemPath to POSIX path of anItem
            do shell script "cd /Users/hideki/pdf_knowledge_extractor_mac && python3 src/app.py '" & itemPath & "'"
            display notification "PDFの処理が完了しました: " & (name of (info for (anItem as alias))) with title "PDF Knowledge Extractor"
        end repeat
    on error errorMessage
        display dialog "エラーが発生しました: " & errorMessage buttons {"OK"} default button 1
    end try
    return input
end run
'''

def create_automator_app():
    # Create temporary AppleScript file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
        f.write(applescript_content)
        script_path = f.name
    
    try:
        # Compile AppleScript to application
        app_path = "/Applications/PDF Extractor (Automator).app"
        cmd = [
            'osacompile', 
            '-o', app_path,
            script_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Automatorアプリケーションが作成されました: {app_path}")
            
            # Make the app accept PDF files
            info_plist = f"{app_path}/Contents/Info.plist"
            if os.path.exists(info_plist):
                # Add PDF file association to the plist
                plist_addition = '''
defaults write "{}" CFBundleDocumentTypes -array '{{
    CFBundleTypeExtensions = (pdf);
    CFBundleTypeName = "PDF Document";
    CFBundleTypeRole = "Viewer";
    LSItemContentTypes = ("com.adobe.pdf");
    LSHandlerRank = "Alternate";
}}'
'''.format(app_path.replace(' ', '\\ '))
                
                os.system(plist_addition)
                print("PDFファイルの関連付けを追加しました")
        else:
            print(f"エラー: {result.stderr}")
            
    finally:
        # Clean up temporary file
        os.unlink(script_path)

if __name__ == "__main__":
    create_automator_app()