from tkinter import *
from tkinter import messagebox
from threading import Thread
import socket,os


#Functions
def loadClass():
    global className
    global studentArray
    global consequenceArray
    global clientsConnected
    continue_ = True
    if not(className == ""):
        continue_ = messagebox.askyesno ("Proceed?", "Do you wish to proceed? Doing so will remove class: ("+className+") consequence data.")
    if continue_:
        fileLocation = filedialog.askopenfilename(filetypes=[("Consequence stystem compatible text file",".txt")])
        if not(fileLocation == ""):
            for i in clientsConnected:
                s.sendto((bytes(str(['consequenceStatus',0]), encoding='utf-8')), (i[0][0], i[0][1]))
            file = open(fileLocation,'r')
            clientsConnected = []
            studentArray = []
            for user in file:
                studentArray.append(user.rstrip())
            className = studentArray[0]
            studentArray.pop(0)
            studentList.delete(0, END)
            for name in studentArray:
                studentList.insert(END,name)
            label_studentList.config(text=className)

            consequenceArray = {}

            for name in studentArray:
                consequenceArray[name] = 0
            updateUI()

def increaseConsequence(event=None):
    global consequenceArray
    if studentList.curselection() == ():
        messagebox.showwarning("Warning","No Student Selected")
    else:
        studentSelected = studentList.get(studentList.curselection())
        currentConsequence = consequenceArray[studentSelected]
        if currentConsequence == 5:
            messagebox.showwarning("Warning","You cannot increase " + studentSelected + "'s consequences any more.")
        else:
            consequenceArray[studentSelected] = (currentConsequence + 1)
        updateUI()
        updateClients()
        
def decreaseConsequence(event=None):
    global consequenceArray
    if studentList.curselection() == ():
        messagebox.showwarning("Warning","No Student Selected")
    else:
        studentSelected = studentList.get(studentList.curselection())
        currentConsequence = consequenceArray[studentSelected]
        if currentConsequence == 0:
            messagebox.showwarning("Warning","You cannot decrease " + studentSelected + "'s consequences any more.")
        else:
            consequenceArray[studentSelected] = (currentConsequence - 1)
        updateUI()
        updateClients()

def updateUI(event=None):
    global consequenceArray
    if not(studentList.curselection() == ()):
        studentSelected = studentList.get(studentList.curselection())
        label_selectedStudentStatus.config(text=("Status: C"+str(consequenceArray.get(studentSelected))))
        label_selectedStudent.config(text=studentSelected)
    else:
        label_selectedStudentStatus.config(text=("Status: C0"))
        label_selectedStudent.config(text="Student Account")

def updateClients():
    global consequenceArray
    global clientsConnected
    for i in clientsConnected:
        s.sendto((bytes(str(['consequenceStatus',consequenceArray.get(i[1])]), encoding='utf-8')), (i[0][0], i[0][1]))
    
#Variables
clientsConnected = []
studentArray = []
className = ""
consequenceArray= {}

#Socket Server variables
serverPort = 8082
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0.000000001)
s.bind(("", serverPort))


#Creating main window
mainWindow = Tk()
mainWindow.title("Consequences System | Teacher Console")
mainWindowFrame = Frame(mainWindow)
mainWindowFrame.pack(side="top", fill="both", expand=False, padx=10, pady=10)


#Create toolbar/menu at top
menuBar = Menu(mainWindowFrame)
fileMenuList = Menu(menuBar,tearoff=0)
fileMenuList.add_command(label="Load Class",command=loadClass)
menuBar.add_cascade(label="File",menu=fileMenuList)
mainWindow.config(menu=menuBar)


#Create Student List Label
label_studentList = Label(mainWindowFrame,text="",font=("Helvetica",20), fg="red")
label_studentList.grid(row=0,column=0)

#Create listbox that will contain students
studentList = Listbox(mainWindowFrame,selectmode='single')
studentList.grid(row=1,column=0,stick=N,padx=5,rowspan=4)
studentList.bind('<<ListboxSelect>>', updateUI)

#Label for consequence status
label_consequence = Label(mainWindowFrame,text="Consequence Status",font=("Helvetica",20), fg="red")
label_consequence.grid(row=0,column=2,columnspan=2)

#Label for selected student name
label_selectedStudent = Label(mainWindowFrame,text="Student Account",font=("Helvetica",16))
label_selectedStudent.grid(row=1,column=2,sticky=W,columnspan=2)

#Label for selected student consequence status
label_selectedStudentStatus = Label(mainWindowFrame,text="Status: C0",font=("Helvetica",16))
label_selectedStudentStatus.grid(row=2,column=2,sticky=W,columnspan=2)

#Button for increasing consequence
button_increase = Button(mainWindowFrame,text="+",font=("Helvetica",30),width=2,height=1,command=increaseConsequence)
button_increase.grid(row=3,column=2,columnspan=2)
mainWindow.bind('<Up>', increaseConsequence)

#Button for decreasing consequence
button_decrease = Button(mainWindowFrame,text="-",font=("Helvetica",30),width=2,height=1,command=decreaseConsequence)
button_decrease.grid(row=3,column=3,columnspan=2)
mainWindow.bind('<Down>', decreaseConsequence)

#teacherName = messagebox.askquestion("Teacher Name","Your name is?",message)


def socket():
    global clientsConnected
    global className
    while True:
        try:
            data,addr = s.recvfrom(1024)
            data = str(data)[2:-1]
            data = data.replace("\\'", "'")
            data = eval(data)

            if data[0] == 'connect':
                clientsConnected.append([addr,data[1]])
                s.sendto((bytes(str(['connectReply','Dan Smith',className]), encoding='utf-8')), (addr[0], addr[1]))
        except:
            pass

socketThread = Thread(target=socket)
socketThread.start()

