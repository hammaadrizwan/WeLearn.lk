from tkinter import *
from tkinter import messagebox
import random
import firebase_admin
from firebase_admin import credentials, firestore
import socket
import threading
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

cred = credentials.Certificate(resource_path("learn-app-10dec-firebase-adminsdk-ug4cg-09cf050dac.json"))
firebase_admin.initialize_app(cred)
database = firestore.client()

# START SERVER IF TEACHER ONLY!!
CLIENTS = {}
ADDRESSES = {}
EXIT_CHAT = False
USER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
USERNAME = ""
SERVER = ""
PORT = 8080
SIZE = 1024
FORMAT = "utf-8"

#AUTHENTICATION
authWindow = Tk()

rscDict = {
    "iconFile": resource_path(r"assets\mainIcon.ico"),
    "bg_1": PhotoImage(file=resource_path(r"assets\bg_1.png")),
    "bg_2": PhotoImage(file=resource_path(r"assets\bg_2.png")),
    "bg_3": PhotoImage(file=resource_path(r"assets\bg_3.png")),
    "html": "web_v2/index.html"
}

authWindow.resizable(False, False)
authWindow.option_add("*Font", "Calibri")
authWindow.iconbitmap(rscDict.get("iconFile"))
auth_h = 250
auth_w = 450

#Authentication window Geometries and Formats
authWindow.title( "Learn.lk | Desktop Client" ) #Window attributes
authWindow.geometry( str(auth_w) + "x" + str(auth_h) )

bgImage = Label(authWindow, image = rscDict.get("bg_1"))

def get_teacher_info(teacher_username):
    teacherData = []
    teacherWebInfo = list(database.collection(u"teacherInfo").get())

    for teacher in teacherWebInfo:
        if teacher.id == teacher_username:
            teacherData.append(teacher.to_dict())

def get_subjects():
    subjectData = ["None"]
    subjectInfo = list(database.collection(u"subjects").get())
    for subject in subjectInfo:
        subjectData.append(subject.id)

    return subjectData

def write_teacher_info(main_window, teacher_username, subject_selection, display_name, display_image_url, heading_string, info_string, time_1_string, time_2_string, time_3_string, charges_string):
    if subject_selection == "None":
        messagebox.showwarning(title = "Teacher Info", message = "Invalid Subject Selection!")
    else:
        if len(subject_selection) == 0 or len(display_name) == 0 or len(display_image_url) == 0 or len(heading_string) == 0 or len(info_string) == 0 or len(time_1_string) == 0 or len(time_2_string) == 0 or len(time_3_string) == 0 or len(charges_string) == 0:
            messagebox.showwarning(title = "Teacher Info", message = "Certain fields are empty, Please try again!")
        else:
            info_string = info_string.replace("\n", "__")
            database.collection(u"teacherInfo").document(u"%s"%teacher_username).set({
                "subject": subject_selection,
                "displayName": display_name,
                "displayImage": display_image_url,
                "heading": heading_string,
                "information": info_string,
                "time_1": time_1_string,
                "time_2": time_2_string,
                "time_3": time_3_string,
                "charges": charges_string
            })
            messagebox.showinfo(title = "Teacher Info", message = "Website info written successfully!")
            main_window.destroy()

def write_to_firestore(user_firstname, user_lastname, user_username, user_password, user_email, user_integer):
    if user_integer == 1: # 1 means STUDENT | 2 means TEACHERS
        database.collection(u"students").document(u"%s"%user_firstname).set({
            'firstname': user_firstname,
            'lastname': user_lastname,
            "username": user_username,
            "password": user_password,
            "email": user_email,
            "selection": user_integer,
            "teachers": ""
        })

    elif user_integer == 2:
        database.collection(u"teachers").document(u"%s"%user_firstname).set({
            'firstname': user_firstname,
            'lastname': user_lastname,
            "username": user_username,
            "password": user_password,
            "email": user_email,
            "selection": user_integer,
            "students": ""
        })

        database.collection(u"teacherIP").document(u"%s"%user_firstname).set({
            "socket_hostname": socket.gethostname()
        })

        database.collection(u"teacherInfo").document(u"%s"%user_firstname).set({
            "subject": "",
            "displayName": "",
            "displayImage": "",
            "heading": "",
            "information": "",
            "time_1": "",
            "time_2": "",
            "time_3": "",
            "charges": ""
        })

def add_to_string(user_dict, user_integer, new_username):
    if user_integer == 1: # If student; add teachers
        current = user_dict.get(u"teachers")
    else:
        current = user_dict.get(u"students")

    new = current
    users = current.split()
    exists = False
    for user in users:
        if user.lower() == new_username.lower():
            exists = True
            break

    if exists == False: #Adding only if it doesn't exist already
        new = current + " " + new_username

    return new

def write_student(teacher_username, student_name):
    studentInfo = list(database.collection(u'students').get())
    teacherInfo = list(database.collection(u'teachers').get())

    for teacher in teacherInfo:
        single_teacherUsername = teacher.to_dict().get(u"username") # Getting teacher usernames of all database entries
        if single_teacherUsername.lower() == teacher_username.lower(): # Checking if username equals the current username
            teacherID = teacher.id
            new_students = add_to_string(teacher.to_dict(), 2, student_name) # Get a string of new students
            database.collection(u"teachers").document(u"%s"%teacherID).set({
                'firstname':    teacher.to_dict().get("firstname"),
                'lastname':     teacher.to_dict().get("lastname"),
                "username":     teacher.to_dict().get("username"),
                "password":     teacher.to_dict().get("password"),
                "email":        teacher.to_dict().get("email"),
                "selection":    teacher.to_dict().get("selection"),
                "students":     new_students
            })
            break

    for student in studentInfo:
        single_studentUsername = student.to_dict().get(u"firstname")
        if single_studentUsername.lower() == student_name.lower():
            studentID = student.id
            new_teachers = add_to_string(student.to_dict(), 1, teacherID) # Get a string of new students - teacherID IS USED HERE
            database.collection(u"students").document(u"%s"%studentID).set({
                'firstname':    student.to_dict().get("firstname"),
                'lastname':     student.to_dict().get("lastname"),
                "username":     student.to_dict().get("username"),
                "password":     student.to_dict().get("password"),
                "email":        student.to_dict().get("email"),
                "selection":    student.to_dict().get("selection"),
                "teachers":     new_teachers
            })
            break

def read_from_firestore(user_integer):
    userList = []
    if user_integer == 1:
        userInfo = list(database.collection(u'students').get())
        for user in userInfo:
            userList.append(user.to_dict())
    elif user_integer == 2:
        userInfo = list(database.collection(u'teachers').get())
        for user in userInfo:
            userList.append(user.to_dict())

    return userList

def auth_guest_callback():
    a = random.randint( 1000 , 9999 )
    username=("GUEST "+str(a))
    messagebox.showinfo( title="Guest" , message="Welcome " +username + "!" )
    chatwin(username)
    return username

def call_website():
    os.system("start "+rscDict.get("html"))

def auth_login_callback():
    loginWindow = Toplevel()
    loginWindow.resizable( False , False )
    loginWindow.iconbitmap(rscDict.get("iconFile"))

    login_w = 400
    login_h = 250
    sel_int = IntVar()

    loginWindow.geometry(str(login_w) + "x" + str(login_h)) #Opens a new window for the login page
    loginWindow.title( "Login" )

    bgImage         = Label (loginWindow, image = rscDict.get("bg_2"))
    loginHeading    = Label (loginWindow, text = "Login Window")
    usernameLabel   = Label (loginWindow, text = "User Name", width = 10)
    passwordLabel   = Label (loginWindow, text="Password", width = 10)
    usernameEntry   = Entry (loginWindow, textvariable="", width = 22)
    passwordEntry   = Entry (loginWindow, textvariable="", show='*', width = 22)
    radioLabel      = Label (loginWindow, text          = "Select Position"  )
    student_rdButton= Radiobutton(loginWindow, text = "Student", variable = sel_int, value = 1)
    teacher_rdButton= Radiobutton(loginWindow, text = "Teacher", variable = sel_int, value = 2)
    loginButton     = Button(loginWindow, text="LOGIN", command = lambda:checkAuth(loginWindow, usernameEntry.get(), passwordEntry.get(), sel_int.get()), width=15)

    label_offsetX = -40
    entry_offsetX = -30
    startPos = 20
    padding = 45
    loginHeading.config(font = ("Calibri", 16))

    # Specifically placing menu items on the window; avoids errors
    loginHeading.place  (x = 0, y = startPos, anchor = "w", relwidth=1)
    usernameLabel.place (x = (login_w//2)+label_offsetX, y = startPos+padding, anchor = "e")
    usernameEntry.place (x = (login_w//2)+entry_offsetX, y = startPos+padding, anchor = "w")

    passwordLabel.place (x = (login_w//2)+label_offsetX, y = startPos+(padding*2), anchor = "e")
    passwordEntry.place (x = (login_w//2)+entry_offsetX, y = startPos+(padding*2), anchor = "w")

    radioLabel.place    (x = (login_w//2)+label_offsetX,  y = startPos+(padding*3), anchor = "e")
    student_rdButton.place(x = (login_w//2)+entry_offsetX,  y = startPos+(padding*3), anchor = "w")
    teacher_rdButton.place(x = (login_w//2)+entry_offsetX+100,  y = startPos+(padding*3), anchor = "w")

    loginButton.place   (x = (login_w//2), y = startPos+(padding*4), anchor = "center")
    bgImage.place       (x = 0, y = 0, relwidth=1, relheight=1)

def auth_reg_stu_callback(teacher_username):
    studentInfoWindow = Toplevel()
    studentInfoWindow.resizable(False , False)
    studentInfoWindow.iconbitmap(rscDict.get("iconFile"))

    info_w = 400
    info_h = 200

    studentInfoWindow.geometry(str(info_w) + "x" + str(info_h)) #Opens a new window for the login page
    studentInfoWindow.title( "Login" )

    bgImage         = Label (studentInfoWindow, image = rscDict.get("bg_2"))
    loginHeading    = Label (studentInfoWindow, text = "Student Registration")

    nameLabel       = Label (studentInfoWindow, text = "Student First Name", width = 20)
    emailLabel      = Label (studentInfoWindow, text="Student Email", width = 20)

    nameEntry       = Entry (studentInfoWindow, textvariable="", width = 22)
    emailEntry      = Entry (studentInfoWindow, textvariable="", width = 22)

    confirmButton   = Button(studentInfoWindow, text="CONFIRM", command = lambda:registerStudent(studentInfoWindow, teacher_username, nameEntry.get(), emailEntry.get()), width=15)

    label_offsetX = -10
    entry_offsetX = 0
    startPos = 20
    padding = 45
    loginHeading.config(font = ("Calibri", 16))

    # Specifically placing menu items on the window; avoids errors
    loginHeading.place  (x = 0, y = startPos, anchor = "w", relwidth=1)
    nameLabel.place (x = (info_w//2)+label_offsetX, y = startPos+padding, anchor = "e")
    nameEntry.place (x = (info_w//2)+entry_offsetX, y = startPos+padding, anchor = "w")

    emailLabel.place (x = (info_w//2)+label_offsetX, y = startPos+(padding*2), anchor = "e")
    emailEntry.place (x = (info_w//2)+entry_offsetX, y = startPos+(padding*2), anchor = "w")

    confirmButton.place   (x = (info_w//2), y = startPos+(padding*3), anchor = "center")
    bgImage.place       (x = 0, y = 0, relwidth=1, relheight=1)

def auth_reg_callback():
    regWindow = Toplevel()
    regWindow.resizable(False , False)
    regWindow.iconbitmap(rscDict.get("iconFile"))
    reg_w = 400
    reg_h = 580
    sel_int = IntVar()

    regWindow.geometry(str(reg_w) + "x" + str(reg_h))
    regWindow.title("Register")

    bgImage             = Label(regWindow, image = rscDict.get("bg_3"))
    regHeading          = Label(regWindow, text = "Registration Window")
    firstnameLabel      = Label(regWindow, text         = "First Name"       )
    firstnameEntry      = Entry(regWindow, textvariable = ""                 )

    lastnameLabel       = Label(regWindow, text         = "Last Name"        )
    lastnameEntry       = Entry(regWindow, textvariable = ""                 )

    usernameLabel       = Label(regWindow, text         = "Username"         )
    usernameEntry       = Entry(regWindow, textvariable = ""                 )

    con_usernameLabel   = Label(regWindow, text         = "Confirm Username" )
    con_usernameEntry   = Entry(regWindow, textvariable = ""                 )

    passwordLabel       = Label(regWindow, text         = "Password"         )
    passwordEntry       = Entry(regWindow, textvariable = "" , show = "*"    )

    con_passwordLabel   = Label(regWindow, text         = "Confirm Password" )
    con_passwordEntry   = Entry(regWindow, textvariable = "" , show = "*"    )

    emailLabel          = Label(regWindow, text         = "Email"            ) # Email is taken for contacting and promotion purposes
    emailEntry          = Entry(regWindow, textvariable = ""                 )

    con_emailLabel      = Label(regWindow, text         = "Confirm Email"    )
    con_emailEntry      = Entry(regWindow, textvariable = ""                 )

    radioLabel          = Label(regWindow, text          = "Select Position"  )
    student_rdButton    = Radiobutton(regWindow, text = "Student", variable = sel_int, value = 1)
    teacher_rdButton    = Radiobutton(regWindow, text = "Teacher", variable = sel_int, value = 2)

    registerButton      = Button(regWindow, text  = "SIGN UP"  , command = lambda:register(regWindow, firstnameEntry.get(), lastnameEntry.get(), usernameEntry.get() , con_usernameEntry.get(), passwordEntry.get(), con_passwordEntry.get(), emailEntry.get(), con_emailEntry.get(), sel_int.get()) , width=15)
    quitButton          = Button(regWindow, text = "EXIT"      , command = regWindow.destroy     , width=15,  fg= "red" , bg= None )

    #Buttons in Registration Window
    label_offsetX = -40
    entry_offsetX = -20
    entry_width = 180
    startPos = 20
    padding = 40
    regHeading.config(font = ("Calibri", 16))

    regHeading.place        (x = 0, y = startPos, anchor = "w", relwidth=1)
    firstnameLabel.place    (x = (reg_w//2)+label_offsetX,  y = startPos+padding, anchor = "e")
    firstnameEntry.place    (x = (reg_w//2)+entry_offsetX,  y = startPos+padding, anchor = "w", width=entry_width)

    lastnameLabel.place     (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*2), anchor = "e")
    lastnameEntry.place     (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*2), anchor = "w", width=entry_width)

    usernameLabel.place     (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*4), anchor = "e")
    usernameEntry.place     (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*4), anchor = "w", width=entry_width)

    con_usernameLabel.place (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*5), anchor = "e")
    con_usernameEntry.place (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*5), anchor = "w", width=entry_width)

    passwordLabel.place     (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*6), anchor = "e")
    passwordEntry.place     (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*6), anchor = "w", width=entry_width)

    con_passwordLabel.place (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*7), anchor = "e")
    con_passwordEntry.place (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*7), anchor = "w", width=entry_width)

    emailLabel.place        (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*9), anchor = "e")
    emailEntry.place        (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*9), anchor = "w", width=entry_width)

    con_emailLabel.place    (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*10), anchor = "e")
    con_emailEntry.place    (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*10), anchor = "w", width=entry_width)

    radioLabel.place        (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*11), anchor = "e")
    student_rdButton.place  (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*11), anchor = "w")
    teacher_rdButton.place  (x = (reg_w//2)+entry_offsetX+100,  y = startPos+(padding*11), anchor = "w")

    quitButton.place        (x = (reg_w//2)-10,  y = startPos+(padding*13)-20, anchor = "e")
    registerButton.place    (x = (reg_w//2)+10,  y = startPos+(padding*13)-20, anchor = "w")
    bgImage.place           (x = 0, y = 0, relwidth=1, relheight=1)

def auth_infoChange_callback(user_name):
    infoChangeWindow = Toplevel()
    infoChangeWindow.resizable(False , False)
    infoChangeWindow.iconbitmap(rscDict.get("iconFile"))
    reg_w = 480
    reg_h = 550
    subjectsVar = StringVar(infoChangeWindow)
    subjectsArray = get_subjects()
    subjectsVar.set(subjectsArray[0]) # default value

    get_teacher_info(user_name)
    get_subjects()

    infoChangeWindow.geometry(str(reg_w) + "x" + str(reg_h))
    infoChangeWindow.title("Change Teacher Info")

    bgImage             = Label(infoChangeWindow, image = rscDict.get("bg_2"))
    infoHeading         = Label(infoChangeWindow, text = "Change Teacher Information")

    subjectLabel        = Label(infoChangeWindow, text = "Select your subject"      )
    subjectSelect       = OptionMenu(infoChangeWindow, subjectsVar, *subjectsArray  )

    nameLabel           = Label(infoChangeWindow, text = "Display Name"             )
    nameEntry           = Entry(infoChangeWindow, textvariable = ""                 )

    imageLabel          = Label(infoChangeWindow, text = "Display Image URL"        )
    imageEntry          = Entry(infoChangeWindow, textvariable = ""                 )

    headingLabel        = Label(infoChangeWindow, text = "Heading / Title"          )
    headingEntry        = Entry(infoChangeWindow, textvariable = ""                 )

    infoLabel           = Label(infoChangeWindow, text = "Information"              )
    infoEntry           = Text(infoChangeWindow)

    timingsLabel_1      = Label(infoChangeWindow, text = "Class Time 1"             )
    timingsEntry_1      = Entry(infoChangeWindow, textvariable = ""                 )

    timingsLabel_2      = Label(infoChangeWindow, text = "Class Time 2"             )
    timingsEntry_2      = Entry(infoChangeWindow, textvariable = ""                 )

    timingsLabel_3      = Label(infoChangeWindow, text = "Class Time 3"             )
    timingsEntry_3      = Entry(infoChangeWindow, textvariable = ""                 )

    chargesLabel        = Label(infoChangeWindow, text = "Charges per class"        ) # Email is taken for contacting and promotion purposes
    chargesEntry        = Entry(infoChangeWindow, textvariable = ""                 )

    # nameEntry.insert(0, "Mr. Brian Silva")
    # imageEntry.insert(0, "www.google.com")
    # headingEntry.insert(0, "Top Sri Lankan OL / AL Schools Biology Teacher")
    # infoEntry.insert(0.0, "I love Bio\nI hate Chem\nI want to teach your bio\nI want to make you forget Chem")
    # timingsEntry_1.insert(0, "8:30 to 9:30 PM")
    # timingsEntry_2.insert(0, "8:00 to 9:00 PM")
    # timingsEntry_3.insert(0, "5:30 to 6:30 PM")
    # chargesEntry.insert(0, "Rs. 3000 per class")
    confirmButton       = Button(infoChangeWindow, text  = "CONFIRM", command = lambda:write_teacher_info(infoChangeWindow, user_name, subjectsVar.get(), nameEntry.get(), imageEntry.get(), headingEntry.get(), infoEntry.get(0.0, "end"), timingsEntry_1.get(), timingsEntry_2.get(), timingsEntry_3.get(), chargesEntry.get()), width=15)
    quitButton          = Button(infoChangeWindow, text = "EXIT", command = infoChangeWindow.destroy, width=15, fg= "red", bg= None)

    #Buttons in Registration Window
    label_offsetX = -100
    entry_offsetX = -80
    entry_width = 300
    startPos = 20
    padding = 40
    infoHeading.config(font = ("Calibri", 16))

    infoHeading.place       (x = 0, y = startPos, anchor = "w", relwidth=1)
    nameLabel.place         (x = (reg_w//2)+label_offsetX,  y = startPos+padding, anchor = "e")
    nameEntry.place         (x = (reg_w//2)+entry_offsetX,  y = startPos+padding, anchor = "w", width=entry_width)

    subjectLabel.place      (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*2), anchor = "e")
    subjectSelect.place     (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*2), anchor = "w", width=entry_width)

    headingLabel.place      (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*3), anchor = "e")
    headingEntry.place      (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*3), anchor = "w", width=entry_width)

    imageLabel.place        (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*4), anchor = "e")
    imageEntry.place        (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*4), anchor = "w", width=entry_width)

    infoLabel.place         (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*5), anchor = "e")
    infoEntry.place         (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*5)-10, anchor = "nw", height = 95, width=entry_width)

    timingsLabel_1.place    (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*8), anchor = "e")
    timingsEntry_1.place    (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*8), anchor = "w", width=entry_width)

    timingsLabel_2.place    (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*9), anchor = "e")
    timingsEntry_2.place    (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*9), anchor = "w", width=entry_width)

    timingsLabel_3.place    (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*10), anchor = "e")
    timingsEntry_3.place    (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*10), anchor = "w", width=entry_width)

    chargesLabel.place      (x = (reg_w//2)+label_offsetX,  y = startPos+(padding*11), anchor = "e")
    chargesEntry.place      (x = (reg_w//2)+entry_offsetX,  y = startPos+(padding*11), anchor = "w", width=entry_width)

    quitButton.place        (x = (reg_w//2)-10,  y = startPos+(padding*12)+15, anchor = "e")
    confirmButton.place     (x = (reg_w//2)+10,  y = startPos+(padding*12)+15, anchor = "w")
    bgImage.place           (x = 0, y = 0, relwidth=1, relheight=1)

def register(currentWindow, firstname, lastname, username, con_username, password, con_password, email, con_email, selection_int):
    if (firstname == "") or (lastname == "") or (username == "") or (con_username == "") or (password == "") or (con_password == "") or (email == "") or (con_email == "") or (selection_int == 0):
        messagebox.showinfo(title = "Register Prompt", message = "Certain fields are empty. Please try again!")
    elif (username != con_username) or (password != con_password) or (email != con_email):
        messagebox.showwarning(title = "Register Prompt", message = "Not Authorized, Please re-check your details!")
    elif ("@" not in email):
        messagebox.showwarning(title = "Register Prompt", message = "Invalid Email Address, Please try again!")
    elif (len(password) < 7):
        messagebox.showwarning(title = "Register Prompt", message = "Password too weak, enter 8 characters or more!")
    elif (len(username) < 7):
        messagebox.showwarning(title = "Register Prompt", message = "Username too short, enter 8 characters or more!")
    else:
        if selection_int == 2:
            teacherID = firstname
        else:
            teacherID = ""
        currentWindow.destroy()
        messagebox.showinfo(title = "Register Prompt", message = "Authorized, Thank You!")
        write_to_firestore(firstname, lastname, username, password, email, selection_int)
        chatwin(username, teacherID, selection_int)

def registerStudent(currentWindow, teacher_name, student_name, student_email):
    if (student_name == "") or (student_email == ""):
        messagebox.showinfo(title = "Register Prompt", message = "Certain fields are empty. Please try again!")
    else:
        studentInfo = read_from_firestore(1)
        added = False
        for student in studentInfo:
            if student_name.lower() == student.get("firstname").lower() and student_email.lower() == student.get("email").lower():
                write_student(teacher_name, student_name)
                added = True
                break

        if added == True:
            currentWindow.destroy()
            messagebox.showinfo(title = "Register Prompt", message = "Authorized, Thank You!")
        else:
            messagebox.showwarning(title = "Register Prompt", message = "Not Authorized, Please re-check student details!")

def checkAuth(currentWindow, username, password, user_integer):
    userList = read_from_firestore(user_integer)
    authenticated = False
    for user in userList:
        if username == user.get("username") and password == user.get("password"):
            messagebox.showinfo(title = "Login Prompt" , message = "Authorized, Thank You!")
            currentWindow.destroy()
            authenticated = True
            break

    if authenticated == False:
        messagebox.showwarning(title ="Login Prompt", message = "Not Authorized, Please re-check your details!")
    else:
        teacherID = ""
        if user_integer == 2: # Teachers only
            teacherInfo = list(database.collection(u'teachers').get())
            for teacher in teacherInfo:
                single_teacherUsername = teacher.to_dict().get(u"username") # Getting teacher usernames of all database entries
                if single_teacherUsername.lower() == username.lower(): # Checking if username equals the current username
                    teacherID = teacher.id
                    #print(teacherID)
                    database.collection(u"teacherIP").document(u"%s"%teacherID).set({
                        "socket_hostname": socket.gethostname()
                    })
                    break

        chatwin(username, teacherID, user_integer) # takes the logged user to the main chat page

# SERVER functions - SHOULD ALL BE DONE IN A SEPERATE THREAD
def start_server(current_socketname, message_listBox, connect_button, send_button):
    global SERVER
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        SERVER.bind((current_socketname, PORT))
    except:
        message_listBox.insert("end", ">>> [USER UNAVAILABLE]")
    else:
        message_listBox.delete(0, "end")
        message_listBox.insert("end", ">>> [CONNECTED TO SERVER]")
        connect_button.config(state="disabled")
        send_button.config(state="normal")

def accept_connections(user_name, message_listBox):
    #print("ACCEPT", user_name)
    global ADDRESSES
    while True:
        client, clientAddress = SERVER.accept()
        #print("NEW CLIENT", clientAddress)
        ADDRESSES[client] = clientAddress
        client_start_thread = threading.Thread(target=handle_client, args=(client, user_name, message_listBox,))
        client_start_thread.start()

def handle_client(client_socket, user_name, message_listBox):
    #print("CLIENT", user_name)
    global CLIENTS
    global USER
    global EXIT_CHAT

    user_name = str(random.randrange(1000, 9999))
    message_listBox.insert("end", ">>> [YOU HAVE CONNECTED]")
    CLIENTS[client_socket] = user_name

    while True:
        currentMessage = client_socket.recv(SIZE)#.decode(FORMAT)
        #print("RECEIVED MESSAGE:", currentMessage)
        if currentMessage != bytes("{END}", FORMAT):
            broadcast_message(currentMessage, user_name)
        else:
            client_socket.send(bytes("{END}", FORMAT))
            client_socket.close()
            del CLIENTS[client_socket]
            broadcast_message(bytes("%s has left the server"%user_name, FORMAT))
            EXIT_CHAT = True
            break

def broadcast_message(messageBytes, user_name=""):
    #print("CLIENT", user_name)
    for clientObject in CLIENTS:
        messageHead = ">>> ["+user_name+"]: "
        clientObject.send(bytes(messageHead, FORMAT)+messageBytes)

def run_server(user_name, message_listBox):
    #print("SERVER", user_name)
    SERVER.listen(10)
    serverThread = threading.Thread(target=accept_connections, args=(user_name, message_listBox,))
    serverThread.start()
    serverThread.join()
    SERVER.close()

# CLIENT functions - Applies for both students and teachers
def start_user(current_socketname, message_listBox, connect_button, send_button):
    global USER
    try:
        USER.connect((current_socketname, PORT))
    except:
        message_listBox.insert("end", ">>> [USER UNAVAILABLE]")
    else:
        message_listBox.delete(0, "end")
        message_listBox.insert("end", ">>> [CONNECTED TO SERVER]")
        connect_button.config(state="disabled")
        send_button.config(state="normal")

def accept_message(message_listBox):
    while True:
        try:
            message = USER.recv(SIZE).decode(FORMAT)
            #print("MESSAGE")
            message_listBox.insert("end", message)
        except OSError:
            break

def send_message(main_window, message_entry):
    #print("SENDING...")
    input_message = message_entry.get()
    message_entry.delete(0, "end")
    USER.send(bytes(input_message, FORMAT))
    if input_message == "{END}":
        USER.close()
        EXIT_CHAT = True

def end_session(main_window, message_entry):
    message_entry.delete(0, "end")
    message_entry.insert(0, "{END}")
    send_message(main_window, message_entry)

def start_connection(option_variable, message_listBox, message_entry, connect_button, send_button, user_integer, user_name):
    socket_hostname = ""
    #print("START USERNAME:", user_name)
    #message_label.config(text = "")
    #if str(option_variable.get()) != "None":
    selectedUser = str(option_variable.get())
    if user_integer == 1: # Students: Clients (# Need to get IP from database --> Note that only students can send first message)
        teacherIPs = list(database.collection(u'teacherIP').get())
        for IP in teacherIPs:
            teacherID = IP.id
            if teacherID.lower() == selectedUser.lower():
                socket_hostname = IP.to_dict().get("socket_hostname")
    else: # Teachers: Servers (# Return self comp. name)
        socket_hostname = socket.gethostname()

    if user_integer == 2:
        start_server(socket_hostname, message_listBox, connect_button, send_button)
        main_serverThread = threading.Thread(target=run_server, args=(user_name, message_listBox,))
        main_serverThread.start()

    start_user(socket_hostname, message_listBox, connect_button, send_button)
    main_userThread = threading.Thread(target=accept_message, args=(message_listBox,))
    main_userThread.start()

def chatwin(username, teacher_name, user_integer):
    global EXIT_CHAT
    global USER
    global SERVER
    global USERNAME

    EXIT_CHAT = False
    chatWindow = Toplevel()
    usernameString = ""
    chatWindow.resizable(False, False)
    chatWindow.iconbitmap(rscDict.get("iconFile"))
    chat_w = 600
    chat_h = 400
    bgImage = Label(chatWindow, image = rscDict.get("bg_1"))
    optionVar = StringVar(chatWindow)

    labelsArray = []
    users = read_from_firestore(user_integer)
    for user in users:
        if user_integer == 1:
            student_username = user.get("username")
            usernameString = student_username
            if student_username == username:
                tutorLabelText = "Select Teacher"
                labelsArray = user.get(u"teachers").split()
                break
        else: # Vice versa
            teacher_username = user.get("username")
            usernameString = teacher_username
            if teacher_username == username:
                tutorLabelText = "Select Student"
                labelsArray = user.get(u"students").split()
                break

    labelsArray.insert(0, "None")
    optionVar.set(labelsArray[0]) # default value
    USERNAME = usernameString
    #print("USERNAME:", USERNAME)

    # STUDENT is always the client
    # TEACHER is always the server
    chatWindow.geometry(str(chat_w) + "x" + str(chat_h))
    chatWindow.title( "Chat Window" )
    messageListBox = Listbox(chatWindow)
    messageListBox.config(font = ("Consolas", 10))

    rgStuButton = Button(chatWindow, text="Register Student", command = lambda:auth_reg_stu_callback(username))
    changeInfoButton = Button(chatWindow, text="Change Website Info", command = lambda:auth_infoChange_callback(teacher_name))
    visitWebsiteButton = Button(chatWindow, text="Visit Website", command = call_website)
    tutorLabel = Label(chatWindow, text=tutorLabelText)
    menu = OptionMenu(chatWindow, optionVar, *labelsArray)
    messageEntry = Entry(chatWindow, textvariable = "", relief="sunken")
    messageEntry.insert(0, "Type your message here...")

    connectButton = Button(chatWindow, text="CONNECT", command = lambda:start_connection(optionVar, messageListBox, messageEntry, connectButton, sendButton, user_integer, usernameString))
    sendButton = Button(chatWindow, text="SEND", command = lambda:send_message(chatWindow, messageEntry))
    sendButton.config(state="disabled")
    # chatWindow.protocol("WM_DELETE_WINDOW", lambda:end_session(chatWindow, messageEntry))

    Grid.rowconfigure(chatWindow, 0, weight=1)
    Grid.columnconfigure(chatWindow, 0, weight=1)

    if user_integer == 1:
        messageListBox.grid(row=0, columnspan=3, sticky=W+E+N+S, padx=5, pady=5)
        tutorLabel.grid(row=1, column=0, sticky=W+E+N+S, padx=5, pady=5)
        menu.grid(row=1, column=1, columnspan=2, sticky=W+E+N+S, padx=5, pady=5)
        messageEntry.grid(row=2, column=0, sticky=W+E+N+S, padx=5, pady=5)
        connectButton.grid(row=2, column=1, sticky=W+E+N+S, padx=5, pady=5)
        sendButton.grid(row=2, column=2, sticky=W+E+N+S, padx=5, pady=5)

    elif user_integer == 2:
        messageListBox.grid(row=0, columnspan=3, sticky=W+E+N+S, padx=5, pady=5)
        rgStuButton.grid(row=1, column=0, sticky=W+E+N+S, padx=5, pady=5)
        changeInfoButton.grid(row=1, column=1, sticky=W+E+N+S, padx=5, pady=5)
        visitWebsiteButton.grid(row=1, column=2, sticky=W+E+N+S, padx=5, pady=5)
        #tutorLabel.grid(row=1, column=1, sticky=W+E+N+S, padx=5, pady=5)
        #menu.grid(row=1, column=2, sticky=W+E+N+S, padx=5, pady=5)
        messageEntry.grid(row=2, column=0, sticky=W+E+N+S, padx=5, pady=5)
        connectButton.grid(row=2, column=1, sticky=W+E+N+S, padx=5, pady=5)
        connectButton.config(text="CONNECT")
        sendButton.grid(row=2, column=2, sticky=W+E+N+S, padx=5, pady=5)

    bgImage.place(x = 0, y = 0, relwidth=1, relheight=1)

regHeading      = Label  (authWindow, text = "Learn.lk | Desktop Client"                                                )
loginButton     = Button (authWindow, text = "START CHATTING", command = auth_login_callback, width = 30)
registerButton  = Button (authWindow, text = "REGISTER", command = auth_reg_callback, width = 30                        )
guestButton     = Button (authWindow, text = "VISIT WEBSITE", command = call_website, width = 30                        )
quitButton      = Button (authWindow, text = "QUIT", command = authWindow.destroy, width = 30 , fg= "red" , bg= None    )

regHeading.config(font = ("Calibri", 16))
startPos = 25
padding = 45

# Specifically placing menu items on the window; avoids errors
regHeading.place        (x = 0, y = startPos, anchor = "w", relwidth=1                  )
loginButton.place       (x = auth_w//2  , y = startPos+padding, anchor = "center"       )
registerButton.place    (x = auth_w//2  , y = startPos+(padding*2), anchor = "center"   )
guestButton.place       (x = auth_w//2  , y = startPos+(padding*3), anchor = "center"   )
quitButton.place        (x = auth_w//2  , y = startPos+(padding*4), anchor = "center"   )
bgImage.place           (x = 0          , y = 0        , relwidth=1, relheight=1        )

authWindow.mainloop()
