on run
	set pythonPath to "/Users/hideki/Documents/10_Applications/pdf_knowledge_extractor_mac/venv/bin/python3"
	set appScript to "/Users/hideki/Documents/10_Applications/pdf_knowledge_extractor_mac/src/app.py"
	set workDir to "/Users/hideki/Documents/10_Applications/pdf_knowledge_extractor_mac"

	do shell script "cd " & quoted form of workDir & " && " & quoted form of pythonPath & " " & quoted form of appScript & " > /dev/null 2>&1 &"
end run

on open droppedFiles
	set pythonPath to "/Users/hideki/Documents/10_Applications/pdf_knowledge_extractor_mac/venv/bin/python3"
	set appScript to "/Users/hideki/Documents/10_Applications/pdf_knowledge_extractor_mac/src/app.py"
	set workDir to "/Users/hideki/Documents/10_Applications/pdf_knowledge_extractor_mac"

	repeat with aFile in droppedFiles
		set filePath to POSIX path of aFile
		if filePath ends with ".pdf" then
			do shell script "cd " & quoted form of workDir & " && " & quoted form of pythonPath & " " & quoted form of appScript & " " & quoted form of filePath & " > /dev/null 2>&1 &"
		end if
	end repeat
end open
