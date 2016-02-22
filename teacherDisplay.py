from tkinter import *
import os, getpass, sys, socket, time
from threading import Thread
from random import randint
from tkinter import messagebox



def connectToHost():
    global serverPort
    global clientPort
    global s
    global hostname
    
    connected = False
    while not connected:
        try:
            #Send message out to server    
            connectArray = ['teacherdisplayconnect', "ICT-221-CON"]
            connectArray = str(connectArray)
            print(hostname)
            print(serverPort)
            print(connectArray)
            s.sendto((bytes(connectArray, encoding='utf-8')), (hostname, serverPort))
        except:
            print("except")
            pass
        
        #Wait 5 secs for response
        timeout = time.time() + 5 #5 seconds from now
        while time.time() < timeout:
            #Wait to recieve a up message back form server
            try:
                data, addr = s.recvfrom(1024)
                data = str(data)[2:-1]
                data = eval(data)
                print(data)
                print(addr)
                
                if (data[0] == "teacherDisplayReply"):
                    #User Connected to Server
                    connected = True
                    teacher = data[1]
                    className = data[2]
                    #mainProgram(teacher, className)
                    return(teacher,className)
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

def mainProgram(teacher, className):

    #Initial Vars
    global root
    global add
    global update
    global consFrame
    global serverPort
    global clientPort
    global s
    global hostname
    global consLabels

    currentStatus = 0

    def mainLoop():
        #Infinite Loop to Recieve Messages from Server
        while True:
            #Wait to recieve a up message back form server
            try:
                data, addr = s.recvfrom(1024)
                data = str(data)[2:-1]
                data = eval(data)

                print(data)
                
                if (data[0] == "newConsequence" and data[2] > 0):
                    print(data[1])
                    print(consLabels)
                    if data[1] not in consLabels:
                        print("in")
                        addCons(data[1],data[2])
                        
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

    def addCons(name,consequence):
        global i
        global bgcolour
        global consFrame

        print("in add")
        if bgcolour:
            background="white"
            bgcolour = False
        else:
            background="#d6d6d6"
            bgcolour=True

        newNameValue = name
        newConsValue="C"+str(consequence)
        
        rowHolder=Frame(consFrame,bg=background)
        rowHolder.grid(sticky=W+E)

        rowHolder.columnconfigure(0,weight=1)
        rowHolder.columnconfigure(1,weight=1)
        
        lb=Label(rowHolder,text=newNameValue,font=("Gill Sans MT",30),bg=background,fg='#2c255b')
        lb.grid(row=i,column=0,sticky=W,ipadx=10)

        lb=Label(rowHolder,text=newConsValue,font=("Gill Sans MT",30),bg=background,fg='#2c255b')
        lb.grid(row=i,column=1,sticky=E,ipadx=10)
        i+=1

    def updateCons():
        global consLabels

        consLabels["Fred"].config(text="C5")

    root = Tk()
    root.config(bg='#2c255b')
    root.columnconfigure(0,minsize=768,weight=1)

##    add=Button(root,text="Add",command=addCons)
##    add.grid()
##


    consFrame= LabelFrame(root,text="Consequences",bg='white',fg="#2c255b",font=("Gill Sans MT",50))
    consFrame.columnconfigure(0,minsize=760, weight=1)
    consFrame.grid(padx=5,pady=5)

    update=Button(consFrame,text="Update",command=updateCons)
    update.grid()

    mainLoopThread=Thread(target=mainLoop)
    mainLoopThread.start()

hostname = "192.168.0.3"
serverPort = 8082
clientPort = randint(0,65535) #0-65535
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0.01)
s.bind(("", clientPort))
print(s)

root=''
add=''
update=''
consFrame=''


#root.attributes('-fullscreen',True)

#dummyNames = {"Fred":"C0","This is a really long name":"C0","Bob":"C0","Clive":"C0","Ethel":"C0","Sue":"C0","Joe":"C0"}
bgcolour=False
consLabels={}
i=0

connectToHost()



##for name in dummyNames:
##    print("bgcolour: ",bgcolour)    
##    if bgcolour:
##        background="white"
##        bgcolour = False
##    else:
##        background="#d6d6d6"
##        bgcolour=True
##    print(name)
##    labelnameValue=name
##    labelConsValue=dummyNames[name]
##
##    rowHolder=Frame(consFrame,bg=background)
##    rowHolder.grid(sticky=W+E)
##
##    rowHolder.columnconfigure(0,weight=1)
##    rowHolder.columnconfigure(1,weight=1)
##    
##    lb=Label(rowHolder,text=labelnameValue,font=("Gill Sans MT",30),bg=background,fg='#2c255b')
##    lb.grid(row=i,column=0,sticky=W,ipadx=10)
##
##    lb=Label(rowHolder,text=labelConsValue,font=("Gill Sans MT",30),bg=background,fg='#2c255b')
##    lb.grid(row=i,column=1,sticky=E,ipadx=10)
##    consLabels[name]=lb
##    i+=1
##
##print(consLabels)
