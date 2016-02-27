from tkinter import *
import socket, time
from random import randint
from threading import Thread

def connectToServer():
    connected=False
    global hostname
    global serverPort
    
    while not connected:
        try:
            #Send message out to server    
            connectArray = ["teacherdisplayconnect","",""]
            connectArray = str(connectArray)
            print("connecting...")
            s.sendto((bytes(str(connectArray), encoding='utf-8')), (hostname, serverPort))
        except:
            print(e)
            pass

        timeout = time.time() + 5 #5 seconds from now
        while time.time() < timeout:
            #Wait to recieve a up message back form server
            try:
                data, addr = s.recvfrom(1024)
                data = str(data)[2:-1]
                data = eval(data)
                
                if (data[0] == "teacherDisplayReply"):
                    #User Connected to Server 
                    connected = True
                    print("Connected!")
                    #teacher = data[1]
                    #className = data[2]
                    
                    break
            except:
                #print("except")
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


def updateLabel(name,cons):
    print("Update")
##    global studentLabels
##    
##    studentLabels[name][0].config(text=name)
##    studentLabels[name][1].config(text="C"+str(cons))

    global emptyLabels


    found=False
    for l in range(len(emptyLabels)):
        bgcolour=emptyLabels[l][0].cget("bg")
        if not found:
            print("Text: ",emptyLabels[l][0].cget("text"))
            print("Cons: ",cons)
            if emptyLabels[l][0].cget("text")==name:
                print("Found name")
                if cons==0:
                    print("Cons = 0")
                    print("BGColour:",bgcolour)
                    emptyLabels[l][0].config(text="")
                    emptyLabels[l][1].config(text="",bg=bgcolour,fg="black")
                else:
                    print("Cons!=0")
                    emptyLabels[l][0].config(text=name)
                    emptyLabels[l][1].config(text="C"+str(cons))
                    if cons==1:
                        emptyLabels[l][1].config(bg=bgcolour,fg="black")
                    if cons==2:
                        emptyLabels[l][1].config(bg="orange",fg="black")
                    elif cons==3:
                        emptyLabels[l][1].config(bg="red",fg="black")
                    elif cons==4:
                        emptyLabels[l][1].config(bg="black",fg="white")
                    elif cons==5:
                        emptyLabels[l][1].config(bg="black",fg="red")
                found=True
            elif emptyLabels[l][0].cget("text")=="" or emptyLabels[l][0].cget("text")=="Nobody on consequences!":
                emptyLabels[l][0].config(text=name)
                emptyLabels[l][1].config(text="C"+str(cons))
                found=True
    

def clearBoard():
    print("Clear")
    global emptyLabels
    
    for j in range(35):
        if j==0:
            emptyLabels[j][0].config(text="Nobody on consequences!")
            emptyLabels[j][1].config(text="")
        else:
            emptyLabels[j][0].config(text="")
            emptyLabels[j][1].config(text="")

def awaitData():
    #global root
    #Infinite Loop to Recieve Messages from Server
    while True:
        try:
            data, addr = s.recvfrom(1024)
            data = str(data)[2:-1]
            data=eval(data)
            print("Data:",data)
            if data[0] == "newConsequence":# and data[2] > 0):
                updateLabel(data[1],data[2])
            elif data[0]=="endLesson":
                clearBoard()
                    
        except:
            #No Message
            pass


hostname = "192.168.43.23"
serverPort = 8082
clientPort = randint(0,65535)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0.01)
s.bind(("", clientPort))
print(s)
print("Hostname: ",hostname)
print("Client port:",clientPort)

connectToServer()

root = Tk()
root.config(bg='#2c255b')
root.columnconfigure(0,minsize=768,weight=1)
root.attributes('-fullscreen',True)

consFrame= LabelFrame(root,text="Consequences",bg='white',fg="#2c255b",font=("Gill Sans MT",100))
consFrame.columnconfigure(0,minsize=760, weight=1)
consFrame.grid(padx=5,pady=5,sticky=W+E)

bgcolour=True
emptyLabels={}

for i in range(35):    
    if bgcolour:
        background="white"
        bgcolour = False
    else:
        background="#d6d6d6"
        bgcolour=True

    rowHolder=Frame(consFrame,bg=background)
    rowHolder.grid(sticky=W+E)

    rowHolder.columnconfigure(0,weight=1)
    rowHolder.columnconfigure(1,weight=1)

    if i==0:
        nameLabel=Label(rowHolder,text="Nobody on consequences!",font=("Gill Sans MT",60),bg=background,fg='#2c255b')
        nameLabel.grid(row=i,column=0,sticky=W,ipadx=10)
    else:
        nameLabel=Label(rowHolder,text="",font=("Gill Sans MT",60),bg=background,fg='#2c255b')
        nameLabel.grid(row=i,column=0,sticky=W,ipadx=10)

    consLabel=Label(rowHolder,text="",font=("Gill Sans MT",60),bg=background,fg='#2c255b')
    consLabel.grid(row=i,column=1,sticky=E,ipadx=10)
    emptyLabels[i]=[nameLabel,consLabel]

mainLoopThread=Thread(target=awaitData)
mainLoopThread.start()

root.mainloop()

