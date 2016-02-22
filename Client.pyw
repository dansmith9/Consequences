from tkinter import *
import os, getpass, sys, socket, time
from threading import Thread
from random import randint
from tkinter import messagebox

#Set Initial Variables
hostname = "DESKTOP-MHHBL44"
#hostname = "ICT-F16-016"
serverPort = 8082
print(hostname)
clientPort = randint(0,65535) #0-65535
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0.01)
s.bind(("", clientPort))

systemUsername = getpass.getuser()
print(systemUsername)

def connectToHost(serverPort, clientPort, s, hostname):
    connected = False
    while not connected:
        try:
            #Send message out to server    
            connectArray = ['connect', systemUsername]
            connectArray = str(connectArray)
            s.sendto((bytes(connectArray, encoding='utf-8')), (hostname, serverPort))
        except:
            pass
        
        #Wait 5 secs for response
        timeout = time.time() + 5 #5 seconds from now
        while time.time() < timeout:
            #Wait to recieve a up message back form server
            try:
                data, addr = s.recvfrom(1024)
                data = str(data)[2:-1]
                data = eval(data)
                
                if (data[0] == "connectReply"):
                    #User Connected to Server 
                    connected = True
                    teacher = data[1]
                    className = data[2]
                    mainProgram(serverPort, clientPort, s, hostname, teacher, className)
                    break
            except:
                #No Reply from Server
                pass

        if not connected:
            if messagebox.askyesno("Error", "Server May Be Down. Try to Reconnect?"):
                #User wants to retry
                pass
            else:
                #User doens't want to retry
                #Best option might be to auto-retry            
                quit()

def mainProgram(serverPort, clientPort, s, hostname, teacher, className):

    #Initial Vars
    currentStatus = 0

    def mainLoop():
        #Infinite Loop to Recieve Messages from Server
        while True:
            #Wait to recieve a up message back form server
            try:
                data, addr = s.recvfrom(1024)
                data = str(data)[2:-1]
                data = eval(data)
                
                if (data[0] == "consequenceStatus" and data[1] > 0):
                    showWindow()
                    global labelRow2
                    global status
                    global disable
                    disable.withdraw()
                    status = data[1]
                    labelRow2.config(text="Current Status: C" + str(data[1]))
                elif (data[0] == "consequenceStatus" and data[1] < 1):
                    hideWindow()
                    global disable
                    disable.withdraw()

                if (status == 4) or (status == 5):
                    global disable
                    global label
                    disable.deiconify()
                    label.config(text="ALERT:\nYou are now on C" + str(status) +" .\nPlease see Mr Smith.")
                    
            except:
                #No Message
                pass

    def hideWindow():
        root.withdraw()

    def showWindow():
        root.deiconify()

    def populateWindow(teacher, className):
        #Username Stuff    
        labelUsername = Label(rootFrame, text="Current User: " + systemUsername, font=("Calibri Light", 12), background=colour)
        labelUsername.grid(row=0, column=0, sticky=EW)

        #Teacher / Class Stuff
        labelRow2 = Label(rootFrame, text="Teacher: " + teacher + " | Class: " + className, font=("Calibri Light", 12), background=colour)
        labelRow2.grid(row=1, column=0, sticky=EW)

        #Current Status
        global labelRow2
        labelRow2 = Label(rootFrame, text="Current Status: N/A", font=("Calibri Light", 14), background=colour)
        labelRow2.grid(row=2, column=0, sticky=EW)

    def disable():
        global disable
        disable = Tk()
        disable.withdraw()
        colour = "#9c87be"
        disable.config(bg=colour)
        disable.attributes("-topmost", True)

        disable.resizable(0,0)

        ws = disable.winfo_screenwidth() # width of the screen
        hs = disable.winfo_screenheight() # height of the screen
        disable.minsize(width=ws, height=hs)

        disable.overrideredirect(1)

        disableFrame = Frame(disable, background=colour)
        disableFrame.pack(side="top", fill="both", expand=False, padx=10, pady=10)

        global label
        label = Label(disable, text="", font=("Helvetica", 30), background="#9c87be")
        label.place(relx=.5, rely=.5, anchor=CENTER)
        #label.grid(row=0, column=0)

        disable.mainloop()
        
    root = Tk()
    colour = "#9c87be"
    root.config(bg=colour)
    hideWindow()
    root.attributes("-topmost", True)

    root.resizable(0,0)

    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    root.geometry('%dx%d+%d+%d' % (300, 100, ws-315, 15))

    root.overrideredirect(1)

    rootFrame = Frame(root, background=colour)
    rootFrame.grid_columnconfigure(0, minsize=280) #Setup Column
    rootFrame.pack(side="top", fill="both", expand=False, padx=10, pady=10)

    mainLoopThread=Thread(target=mainLoop)
    mainLoopThread.start()

    populateWindow(teacher, className)

    disableThread=Thread(target=disable)
    disableThread.start()

    root.mainloop()

connectToHost(serverPort, clientPort, s, hostname)
