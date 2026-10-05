Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
currentDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

p1 = currentDir & "\.venv\Scripts\pythonw.exe"
p2 = FSO.GetParentFolderName(currentDir) & "\.venv\Scripts\pythonw.exe"
mainScript = currentDir & "\main.py"

If FSO.FileExists(p1) Then
    WshShell.Run """" & p1 & """ """ & mainScript & """", 0, False
ElseIf FSO.FileExists(p2) Then
    WshShell.Run """" & p2 & """ """ & mainScript & """", 0, False
Else
    WshShell.Run "pythonw """ & mainScript & """", 0, False
End If
