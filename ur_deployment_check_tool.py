import math
import datetime
import os
import sys
from reportlab.pdfgen.canvas import Canvas as canv
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red, green, orange, black
from tkinter import *
from tkinter import filedialog

log_label_text = "Awaiting File Selection"
input_filename = ""

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

image_path = resource_path('urlogo.png')

# Function for opening the  
# file explorer window 
def browseFiles(): 
    global input_filename
    input_filename = filedialog.askopenfilename(initialdir = "./", 
                                          title = "Select a URScript File", 
                                          filetypes = (("URScript files", 
                                                        "*.script*"), 
                                                       ("all files", 
                                                        "*.*"))) 
       
    # Change label contents
    log_label_text = "File Opened: \n"+input_filename+"\n" 
    label_log.configure(text=log_label_text)
    #print("File Opened: "+filename) 


def generateReport():
    global input_filename
    global log_label_text
    #print('input filename'+input_filename)    
    #LOAD SCRIPT PROGRAM INTO LIST
    try:
        lines = []
        with open(input_filename, encoding='utf-8') as file:
            lines = [line.strip() for line in file]
    except:
        log_label_text = "Could not process file, please try another\n"
        label_log.configure(text=log_label_text)
        return        

    #REMOVE COMMENTED LINES AND LABELS
    for line in lines:
        if len(line)>0:
            if line[0]=='#' or line[0]=='$': lines.remove(line)
        else:
            lines.remove(line)
    compliant=True
    readError=False

    #CREATE PDF AND WRITE TITLE
    today = str(datetime.date.today())
    title = lines[0].split(' ',2)[1].split('(')[0]
    output_filename = 'ur_config_check_'+title+'_'+today+'.pdf'
    canvas = canv(output_filename)
    canvas.setFillColor(black)
    linepos = 24*cm
    leftmargin = 2*cm
    linespace = 0.6*cm
    fontsize = 12
    canvas.drawImage(image_path,leftmargin, linepos, width=250, preserveAspectRatio=True)
    leftmargin = 3.1*cm

    canvas.setTitle(output_filename)
    canvas.setFillColor(black)
    canvas.setFont('Helvetica-Bold', fontsize)
    linepos = 25*cm
    canvas.drawString(leftmargin, linepos, "UR DEPLOYMENT CONFIGURATION CHECK")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)
    canvas.drawString(leftmargin, linepos, 'Program Name: '+title)
    linepos-=linespace
    canvas.drawString(leftmargin, linepos, 'Report Generation Date: '+today)
    linepos-=linespace

    #GET PAYLOAD SUMMARY
    payloads = [ele for ele in lines if('set_payload' in ele)]
    payloadCount = len(payloads)-1
    initPayload = payloads[0].split(',')
    initMassVal=0
    initMassVal=float(initPayload[0].split('(')[1].split(')')[0])

    if len(initPayload)>1:
        initCog=True
        if float(initPayload[0].split('(')[1])>0:
            initMass=True
        else:
            initMass=False
    else:
        initCog=False
        if initMassVal>0:
            initMass=True
        else:
            initMass=False

    canvas.setFillColor(black)
    linepos-=linespace
    canvas.setFont('Helvetica-Bold', fontsize)
    canvas.drawString(leftmargin, linepos, "PAYLOAD CONFIGURATION")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)

    if initMass:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(red)
        compliant=False
    canvas.drawString(leftmargin, linepos, 'Initial Payload Mass Set: '+str(initMass))
    linepos-=linespace
    canvas.drawString(leftmargin, linepos, 'Initial Payload Mass Value: '+str(initMassVal)+'kg')
    linepos-=linespace

    if initCog:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(red)
        compliant=False    
    canvas.drawString(leftmargin, linepos, 'Initial Payload CoG Set: '+str(initCog))
    linepos-=linespace

    if payloadCount>0:
        canvas.setFillColor(black)
    else:
        canvas.setFillColor(orange)
    canvas.drawString(leftmargin, linepos, 'Dynamic Payload Changes in Program: '+str(payloadCount))
    linepos-=linespace

    #GET TCP SUMMARY
    tcps = [ele for ele in lines if('set_tcp' in ele)]
    tcpCount = 0
    initTCP = tcps[0].split('[')[1].split(']')[0].split(',')
    TCPsum=0
    for val in initTCP:
        TCPsum+=float(val)

    for tcp in tcps:
        if len(tcp)>0:
            TCP = tcp.split('[')[1].split(']')[0].split(',')
            for val in TCP:
                TCPsum+=float(val)
            if TCPsum>0:
                tcpCount+=1
    tcpCount = 0 if tcpCount==0 else tcpCount-1

    canvas.setFillColor(black)
    linepos-=linespace
    canvas.setFont('Helvetica-Bold', fontsize)
    canvas.drawString(leftmargin, linepos, "TCP CONFIGURATION")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)

    if TCPsum!=0:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(red)
        compliant=False
    canvas.drawString(leftmargin, linepos, 'Installation TCP Set: '+str(TCPsum!=0))
    linepos-=linespace

    if tcpCount>0:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(orange)
    canvas.drawString(leftmargin, linepos, 'Dynamic TCP Changes in Program: '+str(tcpCount))
    linepos-=linespace

    #GET MOVEJ SUMMARY
    movejs = [ele for ele in lines if('movej' in ele)]
    movejCount = len(movejs)
    jAccLimit = 800
    jOverAccCount = 0
    jMaxAcc = 0
    jBlends = 0
    acc = 0
    acc1 = 0

    for i in movejs:
        jointmove = i.split(',')
        if len(jointmove) > 1:
            acc1 = jointmove[len(jointmove)-2].split('=')
            if acc1[0].strip()[0]=='a':
                #acc = math.degrees(float(acc1[1]))
                try:
                    acc = math.degrees(float(acc1[1]))
                except ValueError:
                    readError = True
            else:
                acc1 = jointmove[len(jointmove)-3].split('=')
                if acc1[0].strip()[0]=='a':
                    acc = math.degrees(float(acc1[1]))
                    try:
                        acc = math.degrees(float(acc1[1]))
                    except ValueError:
                        readError = True
                    jBlends+=1
            if acc>jAccLimit: jOverAccCount+=1 
            if acc>jMaxAcc: jMaxAcc=acc


    canvas.setFillColor(black)
    linepos-=linespace
    canvas.setFont('Helvetica-Bold', fontsize)
    canvas.drawString(leftmargin, linepos, "MOVEJ CONFIGURATION")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)

    if movejCount == 0:
        canvas.setFillColor(orange)
    else:
        canvas.setFillColor(black)
    canvas.drawString(leftmargin, linepos, 'Total Number of MoveJ Commands: '+str(movejCount))
    linepos-=linespace

    if jOverAccCount > 0:
        canvas.setFillColor(red)
        compliant=False
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'MoveJ Exceeding Recommended Acc: '+str(jOverAccCount))
    linepos-=linespace


    if movejCount == 0:
        canvas.setFillColor(black)
    elif jBlends > 0:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(orange)
        compliant=False
    canvas.drawString(leftmargin, linepos, 'Number of MoveJ with Blends: '+str(jBlends))
    linepos-=linespace

    canvas.setFillColor(black)
    canvas.drawString(leftmargin, linepos, 'Recommended Max Acc for MoveJ: '+str(jAccLimit)+'\u00B0/s\u00B2')
    linepos-=linespace

    if movejCount > 0 and jMaxAcc == 0:
        canvas.setFillColor(orange)
    elif jOverAccCount > 0:
        canvas.setFillColor(red)
        compliant=False
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'Highest MoveJ Acc in Program: '+str(round(jMaxAcc))+'\u00B0/s\u00B2')
    linepos-=linespace

    #GET MOVEL SUMMARY
    movels = [ele for ele in lines if('movel' in ele)]
    movelCount = len(movels)
    lAccLimit = 2.5
    lOverAccCount = 0
    lMaxAcc = 0
    lBlends = 0
    acc = 0
    acc1 = 0

    for i in movels:
        linearmove = i.split(',')
        if len(linearmove) > 1:
            acc1 = linearmove[len(linearmove)-2].split('=')
            if acc1[0].strip()[0]=='a':
                #acc = float(acc1[1])
                try:
                    acc = float(acc1[1])
                except ValueError:
                    readError = True
            else:
                acc1 = linearmove[len(linearmove)-3].split('=')
                if acc1[0].strip()[0]=='a':
                    #acc = float(acc1[1])
                    try:
                        acc = float(acc1[1])
                    except ValueError:
                        readError = True
                    lBlends+=1
            if acc>lAccLimit: lOverAccCount+=1 
            if acc>lMaxAcc: lMaxAcc=acc

    canvas.setFillColor(black)
    linepos-=linespace
    canvas.setFont('Helvetica-Bold', fontsize)
    canvas.drawString(leftmargin, linepos, "MOVEL CONFIGURATION")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)

    if movelCount == 0:
        canvas.setFillColor(orange)
    else:
        canvas.setFillColor(black)
    canvas.drawString(leftmargin, linepos, 'Total Number of MoveL Commands: '+str(movelCount))
    linepos-=linespace

    if lOverAccCount > 0:
        canvas.setFillColor(red)
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'MoveL Exceeding Recommended Acc: '+str(lOverAccCount))
    linepos-=linespace

    if movelCount == 0:
        canvas.setFillColor(black)
    elif lBlends > 0:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(orange)
        compliant=False
    canvas.drawString(leftmargin, linepos, 'Number of MoveL with Blends: '+str(lBlends))
    linepos-=linespace

    canvas.setFillColor(black)
    canvas.drawString(leftmargin, linepos, 'Recommended Max Acc for MoveL: '+str(round(lAccLimit*1000))+'mm/s\u00B2')
    linepos-=linespace

    if movelCount > 0 and lMaxAcc == 0:
        canvas.setFillColor(orange)
    elif lOverAccCount > 0:
        canvas.setFillColor(red)
        compliant=False
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'Highest MoveL Acc in Program: '+str(round(lMaxAcc*1000))+'mm/s\u00B2')
    linepos-=linespace


    #GET MOVEP SUMMARY
    moveps = [ele for ele in lines if('movep' in ele)]
    movepCount = len(moveps)
    pAccLimit = 2.5
    pOverAccCount = 0
    pMaxAcc = 0
    pBlends = 0
    acc = 0
    acc1 = 0

    for i in moveps:
        processmove = i.split(',')
        if len(processmove) > 1:
            acc1 = processmove[len(processmove)-2].split('=')
            if acc1[0].strip()[0]=='a':
                #acc = float(acc1[1])
                try:
                    acc = float(acc1[1])
                except ValueError:
                    readError = True
            else:
                acc1 = processmove[len(processmove)-3].split('=')
                if acc1[0].strip()[0]=='a':
                    #acc = float(acc1[1])
                    try:
                        acc = float(acc1[1])
                    except ValueError:
                        readError = True
                    pBlends+=1
            if acc>pAccLimit: pOverAccCount+=1 
            if acc>pMaxAcc: pMaxAcc=acc

    canvas.setFillColor(black)
    linepos-=linespace
    canvas.setFont('Helvetica-Bold', fontsize)
    canvas.drawString(leftmargin, linepos, "MOVEP CONFIGURATION")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)



    if movepCount == 0:
        canvas.setFillColor(black)
    else:
        canvas.setFillColor(orange)
    canvas.drawString(leftmargin, linepos, 'Total Number of MoveP Commands: '+str(movepCount))
    linepos-=linespace

    if pOverAccCount > 0:
        canvas.setFillColor(red)
        compliant=False
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'MoveP Exceeding Recommended Acc: '+str(pOverAccCount))
    linepos-=linespace

    canvas.setFillColor(black)
    canvas.drawString(leftmargin, linepos, 'Recommended Max Acc for MoveP: '+str(round(pAccLimit*1000))+'mm/s\u00B2')
    linepos-=linespace

    if movepCount > 0 and pMaxAcc == 0:
        canvas.setFillColor(orange)
    elif pOverAccCount > 0:
        canvas.setFillColor(red)
        compliant=False
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'Highest MoveP Acc in Program: '+str(round(pMaxAcc*1000))+'mm/s\u00B2')
    linepos-=linespace

    #PRINT SUMMARY

    canvas.setFillColor(black)
    linepos-=linespace
    canvas.setFont('Helvetica-Bold', fontsize)
    canvas.drawString(leftmargin, linepos, "CHECK SUMMARY")
    linepos-=linespace
    canvas.setFont('Helvetica', fontsize)

    if compliant:
        canvas.setFillColor(green)
    else:
        canvas.setFillColor(red)
    canvas.drawString(leftmargin, linepos, 'Program Compliant with Guidelines: '+str(compliant))
    linepos-=linespace

    if readError:
        canvas.setFillColor(red)
    else:
        canvas.setFillColor(green)
    canvas.drawString(leftmargin, linepos, 'Some Config Unreadable: '+str(readError))
    linepos-=linespace

    canvas.save()

    log_label_text += "\nReport Successfully Exported to: "+output_filename
    log_label_text += '\nProgram Compliant with Guidelines: '+str(compliant)
    log_label_text += '\nSome Config Unreadable: '+str(readError)

    label_log.configure(text=log_label_text)
    print('Report Successfully Exported to: '+output_filename)



def exitNow():
    sys.exit(1)       
                                                                                                   
# Create the root window 
window = Tk() 
   
# Set window title 
window.title('UR Deployment Check') 
   
# Set window size 
window.geometry("330x400") 
   
#Set window background color 
window.config(background = "white") 
   
# Create a File Explorer label 
label_file_explorer = Label(window,  
                            text = 'UR Deployment Configuration Check Tool\n\nSelect URScript File for analysis\nthen click Generate Report', 
                            width = 100, height = 5,  
                            bg = "white", fg = "black") 
   
       
button_explore = Button(window,  
                        text = "Select Script File", 
                        command = browseFiles)  

button_generate = Button(window,  
                     text = "Generate Report", 
                     command = generateReport) 

button_exit = Button(window,  
                     text = "Exit", 
                     command = exitNow) 

label_log = Label(window,  
                            text = log_label_text, 
                            width = 100, height = 7,  
                            bg = "white", wraplength=280) 
   
# Grid method is chosen for placing 
# the widgets at respective positions  
# in a table like structure by 
# specifying rows and columns 
label_file_explorer.grid(column = 1, row = 1, pady=(5,5)) 
   
button_explore.grid(column = 1, row = 2, pady=(5,5)) 

button_generate.grid(column = 1, row = 3, pady=(5,5)) 

button_exit.grid(column = 1, row = 4, pady=(5,5)) 

label_log.grid(column = 1, row = 5, pady=(5,5))
window.grid_columnconfigure(1, weight = 1)
# Let the window wait for any events 
window.mainloop() 

