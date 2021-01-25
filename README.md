# deployment-check-tool

UR Deployment Check Tool
AJP 2020

Small tool to scan through a URScript file and extract key information about whether deployment configuration is within recommendations or not.

Built with python 3.7
Depends on pyinstaller, tkinter and reportlab libraries

GUI layout spacing designed for Windows10, may look and behave differently on other OS.

compile py into exe with pyinstaller using below command. urlogo.png should be in same directory as pyinstaller specification file for it to be correctly embedded into generated PDFs.
pyinstaller ur_deployment_check_tool.spec

changelog:
1.0.1 initial release, generate PDF, save to exe location
1.0.2 fix index out of range when no tcp or payload commands in script, auto open PDF
1.0.3 fix issue when variable name contains movej movel or movep
