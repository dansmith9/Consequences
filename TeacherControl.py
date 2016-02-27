from tkinter import *
from tkinter import messagebox
from threading import Thread
import socket,os
from python_mysql_dbconfig import read_db_config
from mysql.connector import MySQLConnection, Error

#Variables
clientsConnected = [] #list holding addresses of connected student computers
teacherDisplay=[] #list holding addresses of connected teacher displays
studentArray = [] #
className = ""
consequenceArray= {}
usernames={}

#Socket Server variables
serverPort = 8082
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0.0001)
s.bind(("", serverPort))

def query(q):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute(q)
        rows = cursor.fetchall()
 
        return rows
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

#Functions

def updatedStaff(*args):
    global currentStaff
    global groupValue
    global groupList

    #staffChoice = staffMenu.get()
    staffChoice=staffValue.get()
    if staffChoice!="" and staffChoice!="Select your staff initials":
        groupQuery = query("SELECT DISTINCT class FROM students WHERE staff='"+staffChoice+"'")
        groupList=[]
        for result in groupQuery:
            groupList.append(result[0])
        groupValue.set("Now select your class")
        groupMenu.config(state='normal')
        menu = groupMenu['menu']
        menu.delete(0, 'end')

        for group in groupList:
            menu.add_command(label=group, command=lambda g=group: groupValue.set(g))

def updateSubmitGroupButton(*args):
    #print(groupValue.get())
    if groupValue.get()!= "Now select your class":
        groupSubmit.config(state='normal')

def submitGroupButton():
    global className
    global clientsConnected
    global groupValue
    global consequenceArray
    global usernames
    
    className=groupValue.get()
    label_studentList.config(text="Class: "+className)
    selectGroup.withdraw()
    for i in clientsConnected:
        s.sendto((bytes(str(['consequenceStatus',0]), encoding='utf-8')), (i[0][0], i[0][1]))
    #file = open(fileLocation,'r')
    file = query("SELECT firstname, surname, username, seating FROM students WHERE class='"+className+"' ORDER BY seating")
    clientsConnected = []
    studentArray = []
    consequenceArray = {}
    usernames={}
    for user in file:
        name = str(user[3])+". "+user[0]+" "+user[1]
        usernames[name]=user[2]
        consequenceArray[user[2]]=0
        studentArray.append([name,user[2]])
    #className = studentArray[0]
    #studentArray.pop(0) #remove class ID from list
    studentList.delete(0, END) #listbox in UI
    for name in studentArray:
        studentList.insert(END,name[0])
    #label_studentList.config(text=className)
    #print(usernames)

    #consequenceArray = {}

    #for name in studentArray:
    #    consequenceArray[name] = 0
    updateUI()
    
def cancelGroupButton():
    selectGroup.withdraw()
    
def loadClass():
    global className
    global studentArray
    global consequenceArray
    global clientsConnected
    global staffValue
    global groupValue
    global staffLabel
    global groupMenu
    global groupList
    global groupSubmit
    
    continue_ = True
    if className != "":
        continue_ = messagebox.askyesno ("Proceed?", "Do you wish to proceed? Doing so will remove class: ("+className+") consequence data.")
    if continue_:
        staffQuery = query("SELECT DISTINCT staff FROM students")
        staffList=[]
        
        for result in staffQuery:
            staffList.append(result[0])
            
        #configure new window
        selectGroup.deiconify()
        selectGroup.wm_attributes("-topmost", 1)
        selectGroup.title("Select group")
        selectGroup.config(bg='white')
        selectGroup.columnconfigure(0,minsize=100)
        selectGroup.columnconfigure(1,minsize=200)

        #configure widgets
        #staff select widgets:
        
        staffLabel.grid(row=0,column=0,sticky=W,ipadx=10)
        staffLabel.config(bg='white', fg="#2c255b")
        staffValue.set("Select your staff initials")
        staffValue.trace("w", updatedStaff)
        staffMenu = OptionMenu(selectGroup,staffValue,*staffList)
        staffMenu.config(bg='white',highlightcolor='white')
        staffMenu.grid(row=0,column=1,sticky=W+E)
        
        #group select widgets:
        groupLabel = Label(selectGroup,text="Group:",font=("Gill Sans MT",10),bg='white', fg="#2c255b")
        groupLabel.grid(row=1,column=0,sticky=W,ipadx=10)
        groupValue.set("Please select your staff initials first")
        groupValue.trace("w",updateSubmitGroupButton)
        groupMenu = OptionMenu(selectGroup,groupValue,*groupList)
        groupMenu.grid(row=1,column=1,sticky=W+E)
        groupMenu.config(state='disabled',bg='white')

        #dividing frame
        #divider=Frame(selectGroup)
        #selectGroup.rowconfigure(2,minsize=30)
        #divider.grid(row=2)
        
        #Button widgets
        buttonHolder=Frame(selectGroup,bg='white')
        buttonHolder.grid(row=3,column=0,columnspan=2,sticky=W+E,pady=20)
        buttonHolder.rowconfigure(0,minsize=30)
        buttonHolder.columnconfigure(0,minsize=200)
        buttonHolder.columnconfigure(1,minsize=200)
        groupSubmit = Button(buttonHolder,text="OK",command=submitGroupButton,state='disabled',fg='white', bg="#2c255b")
        groupSubmit.grid(row=0,column=0,padx=5,sticky=W+E)

        groupCancel = Button(buttonHolder,text="Cancel",command=cancelGroupButton,fg='white', bg="#2c255b")
        groupCancel.grid(row=0,column=1,padx=5,sticky=W+E)
        

def increaseConsequence(event=None):
    global consequenceArray
    global usernames
    
    if studentList.curselection() == ():
        messagebox.showwarning("Warning","No Student Selected")
    else:
        studentSelected = studentList.get(studentList.curselection())
        studentUsername = usernames[studentSelected]
        currentConsequence = consequenceArray[studentUsername]
        if currentConsequence == 5:
            messagebox.showwarning("Warning","You cannot increase " + studentSelected + "'s consequences any more.")
        else:
            consequenceArray[studentUsername] = (currentConsequence + 1)
            currentConsequence+=1
        updateUI()
        updateClients()
        updateTeacherDisplay(studentSelected,currentConsequence)
        
def decreaseConsequence(event=None):
    global consequenceArray
    global usernames
    
    if studentList.curselection() == ():
        messagebox.showwarning("Warning","No Student Selected")
    else:
        studentSelected = studentList.get(studentList.curselection())
        studentUsername = usernames[studentSelected]
        currentConsequence = consequenceArray[studentUsername]
        if currentConsequence == 0:
            messagebox.showwarning("Warning","You cannot decrease " + studentSelected + "'s consequences any more.")
        else:
            consequenceArray[studentUsername] = (currentConsequence - 1)
            currentConsequence-=1
        updateUI()
        updateClients()
        updateTeacherDisplay(studentSelected,currentConsequence)

def discardGroup():
    global teacherDisplay
    global clientsConnected
    global studentArray
    global usernames
    global className

    className=""
    label_studentList.config(text="Class:")
    for i in clientsConnected:
        s.sendto((bytes(str(['consequenceStatus',0]), encoding='utf-8')), (i[0][0], i[0][1]))
    #file = open(fileLocation,'r')
    clientsConnected = []
    studentArray = []
    consequenceArray = {}
    usernames={}
        
    studentList.delete(0, END) #listbox in UI

    updateUI()
    
    if teacherDisplay!=[]:
        s.sendto((bytes(str(["endLesson","",""]), encoding='utf-8')), (teacherDisplay[0][0], teacherDisplay[0][1]))

def updateUI(event=None):
    global consequenceArray
    global usernames
    
    if not(studentList.curselection() == ()):
        studentSelected = studentList.get(studentList.curselection())
        studentUsername = usernames[studentSelected]
        label_selectedStudentStatus.config(text=("Status: C"+str(consequenceArray.get(studentUsername))))
        label_selectedStudent.config(text=studentSelected)
    else:
        label_selectedStudentStatus.config(text=("Status: C0"))
        label_selectedStudent.config(text="No Student Selected")

def updateClients():
    global consequenceArray
    global clientsConnected
    for i in clientsConnected:
        s.sendto((bytes(str(['consequenceStatus',consequenceArray.get(i[1])]), encoding='utf-8')), (i[0][0], i[0][1]))

def updateTeacherDisplay(stuName,stuCons):
    global teacherDisplay

    print ("Data sent")
    if teacherDisplay!=[]:
        s.sendto((bytes(str(['newConsequence',stuName,stuCons]), encoding='utf-8')), (teacherDisplay[0][0], teacherDisplay[0][1]))
    

def socket():
    global clientsConnected
    global teacherDisplay
    global consequenceArray
    global className
    global studentsArray
    global studentList
    
    while True:
        try:
            data,addr = s.recvfrom(1024)
            data = str(data)[2:-1]
            data = data.replace("\\'", "'")
            data = eval(data)

            print(data[0])
            if data[0] == 'connect':
                print("connected")
                clientsConnected.append([addr,data[1]]) #append address & username to connected list
                s.sendto((bytes(str(['connectReply','Dan Smith',className]), encoding='utf-8')), (addr[0], addr[1]))
            elif data[0]=='teacherdisplayconnect':
                print("Teacher connected")
                teacherDisplay=[addr,data[1]] #append address & username to connected list
                print("addr[0]:",addr[0])
                print("addr[1]:",addr[1])
                s.sendto((bytes(str(['teacherDisplayReply',"DSM",className]), encoding='utf-8')), (addr[0], addr[1]))
                print(teacherDisplay)

        except:
            pass

    



#Creating main window
mainWindow = Tk()
mainWindow.config(bg="#2c255b")
mainWindow.resizable(width=FALSE, height=FALSE)
mainWindow.geometry('{}x{}'.format(500, 750))
mainWindow.title("Consequences System | Teacher Console")
#mainWindow.attributes('-fullscreen', True)
mainWindowFrame = Frame(mainWindow, bg="white")
mainWindowFrame.columnconfigure(0,minsize=250)
mainWindowFrame.pack(side="top", fill="both", padx=10, pady=10)

#Group selection window
selectGroup = Toplevel()
selectGroup.withdraw()
#selectGroup.overrideredirect(1)

#Seating plan window
seatingPlan = Toplevel()
seatingPlan.withdraw()

#Create toolbar/menu at top
menuBar = Menu(mainWindowFrame,bg='white', fg="#2c255b")
fileMenuList = Menu(menuBar,tearoff=0,bg='white', fg="#2c255b")
fileMenuList.add_command(label="Load Class",command=loadClass)
menuBar.add_cascade(label="File",menu=fileMenuList)
mainWindow.config(menu=menuBar)

#Create Student List Label
label_studentList = Label(mainWindowFrame,text="Class: None",font=("Gill Sans MT",20), fg="#2c255b", bg="white")
label_studentList.grid(row=0,column=0,columnspan=4)

#Create listbox that will contain students
studentList = Listbox(mainWindowFrame,selectmode='single',height=35,selectbackground='#2c255b',selectforeground="white",font=("Gill Sans MT",10))
studentList.config(highlightbackground='#2c255b')
studentList.grid(row=1,column=0,stick=N+S+E+W,padx=5,pady=5,rowspan=10)
studentList.bind('<<ListboxSelect>>', updateUI)

#Label for consequence status
label_consequence = Label(mainWindowFrame,text="Student details:",font=("Gill Sans MT",20), fg="#2c255b",bg="white")
label_consequence.grid(row=1,column=2,columnspan=3)

#Label for selected student name
label_selectedStudent = Label(mainWindowFrame,text="No student selected",font=("Gill Sans MT",16), bg="white")
label_selectedStudent.grid(row=2,column=2,sticky=W,columnspan=3)

#Label for selected student consequence status
label_selectedStudentStatus = Label(mainWindowFrame,text="Status: C0",font=("Gill Sans MT",16), bg="white")
label_selectedStudentStatus.grid(row=3,column=2,sticky=W,columnspan=2)

#Button for increasing consequence
button_increase = Button(mainWindowFrame,text="+",font=("Gill Sans MT",30),bg="#6d659e",fg="white",width=2,height=1,command=increaseConsequence)
button_increase.grid(row=4,column=2,sticky=W+E)
mainWindow.bind('<Up>', increaseConsequence)

#Button for decreasing consequence
button_decrease = Button(mainWindowFrame,text="-",font=("Gill Sans MT",30),bg="#6d659e",fg="white",width=2,height=1,command=decreaseConsequence)
button_decrease.grid(row=4,column=3,sticky=W+E)
mainWindow.bind('<Down>', decreaseConsequence)

#button to save class consequences to DB
labelFrameEndLesson = LabelFrame(mainWindowFrame,text="End Lesson",bg="white",fg="#2c255b")
labelFrameEndLesson.grid(row=10,column=2,columnspan=2,sticky=W+E)
buttonSaveCons = Button(labelFrameEndLesson,text="Save details",height=4,bg="#6d659e",fg="white")
buttonSaveCons.grid(sticky=W+E,padx=5,pady=5)
buttonDiscardCons = Button(labelFrameEndLesson,command=discardGroup,text="Discard details",height=4,bg="#6d659e",fg="white")
buttonDiscardCons.grid(row=0,column=1,sticky=W+E,padx=5,pady=5)

staffValue = StringVar()
groupValue = StringVar()
currentStaff = ""
staffLabel = Label(selectGroup,text="Staff:",font=("Gill Sans MT",10))
groupMenu = ""
groupList=['']
groupSubmit = ""
selectedClass = ""

#teacherName = messagebox.askquestion("Teacher Name","Your name is?",message)



socketThread = Thread(target=socket)
socketThread.start()

