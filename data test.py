import socket

hostname = "localhost"
serverPort = 8082
clientPort = 8083
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0.01)
s.bind(("", clientPort))
print(s)
while True:
    command=input("1 for newConsequence, 2 for clearBoard: ")
    if command=="2":
        s.sendto((bytes(str(["endLesson","",""]), encoding='utf-8')), (hostname, serverPort))
    elif command=="1":
        name=input("Please enter the name: ")
        cons=input("Please enter the consequence: ")
        s.sendto((bytes(str(["newConsequence",name,cons]), encoding='utf-8')), (hostname, serverPort))
