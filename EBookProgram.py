import os
import random
import tkinter as tk
from xml.dom import minidom
from xml.etree import ElementTree as ET
import six
import base64
import datetime
import sys

script_dir = os.path.dirname(__file__)

class student ():
    def __init__ (self, first, middle, last, grade, code):
        self.first = first
        self.middle = middle
        self.last = last 
        self.grade = grade
        self.code = code

class Class ():
    def __init__ (self, name):
        self.name = name
        self.students = list()
        self.book = "None"

class RunProgram ():
    def __init__ (self):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"

        self.classList = list() #this is a list of all the classes we added
        self.classButtonList = list() #this is a list of the buttons used to select a class
        self.classSelected = None #this is the class currently selected
        self.bookList = list()
        self.secureMode = False
        self.inAction = False
        self.saved = False

        self.loaded = False
        if (os.path.isfile(os.path.join(script_dir, "programFiles/saveFile.xml"))):
            self.loaded = True
            self.loadXML()
        else:
            self.createXML()

        self.root = tk.Tk()
        self.root.title ("Ebook Program")
        self.root.geometry ("800x500")
        if (self.secureMode):
            tk.Label (self.root, text="Secure Mode Actived", font=("Helvetica", 20, "bold")).pack(pady=(20,50))
            password = self.createEntry (self.root, "Enter Password", 25, 15, "top", 0, 5)
            tk.Button (self.root, text="Continue", font=("Helvetica",12), width=30, command=lambda:self.checkPassword(password)).pack(pady=5)
        else:
            self.setUpWindow()

    def setUpWindow (self):
        #set up window
        self.root.protocol("WM_DELETE_WINDOW", self.quitApp)

        menubar = tk.Menu (self.root)
        menubar.add_command (label="Ebooks", command=self.OpenEbookMenu)
        menubar.add_command (label="View Report", command=self.openReportsWindow)
        menubar.add_command (label="Secure", command=self.secure)
        menubar.add_command (label="Help", command=self.openHelp)
        menubar.add_command (label="Clear Save", command=self.clearSave)
        menubar.add_command (label="Quit", command=self.quitApp)
        self.root.config (menu=menubar)

        #create class select panel
        self.classesFrame = tk.Frame (self.root, width=200, bg="light gray")
        self.classesFrame.pack (side="left", fill="y")
        self.classesFrame.pack_propagate (False)
        classesHeader = tk.Frame (self.classesFrame, bg="light gray")
        classesHeader.pack (fill="x")
        tk.Label (classesHeader, text="CLASSES", font=("Helvetica",16,"bold"), bg="light gray").pack (side="left", padx=5, pady=5)
        self.addIcon = tk.PhotoImage(file=os.path.join(script_dir, "programFiles/plus.png"))
        self.addIcon = self.addIcon.subsample (13)
        addBut = tk.Button (classesHeader, image=self.addIcon, command=lambda:self.AddClass(True), width=30, height=30, relief="flat", bg="light gray")
        addBut.pack (side="right", padx=5, pady=5)
        AddToolTip (addBut, "Add a new class")
        self.addClassInst = tk.Label (self.classesFrame, text="Click the plus button to add a new class", justify="center", font=("Helvetica",10), fg="gray", wraplength=150, bg="light gray")
        self.addClassInst.pack (pady=150)

        #create class view panel
        self.classFrame = tk.Frame (self.root)
        self.classFrame.pack (fill="both")
        self.classHeader = tk.Frame (self.classFrame)

        self.classTitle = tk.Label (self.classHeader, text="New Class", font=("Helvetica",16,"bold"))
        self.classTitle.pack(side="left", padx=5, pady=5)

        self.classControls = tk.Frame (self.classHeader)
        self.classControls.pack (side="right", fill="y")
        tk.Label (self.classControls, text="EBook:", font=("Helvetica",12)).pack (side="left", padx=1, pady=5)
        self.classBook = tk.StringVar ()
        self.classBook.set ("None")
        self.classBook.trace ("w", self.EbookUpdated)
        self.bookMenu = tk.OptionMenu (self.classControls, self.classBook, "None", *self.bookList)
        self.bookMenu.pack (side="left", padx=(1,5), pady=5)
        self.bookMenu["menu"].add_separator ()
        self.bookMenu["menu"].add_command(label="Add New Book", command=self.OpenEbookMenu)
        self.removeIcon = tk.PhotoImage(file=os.path.join(script_dir, "programFiles/trashCan.png"))
        self.removeIconSmall = self.removeIcon.subsample (21)
        self.removeIcon = self.removeIcon.subsample (13)
        trashBut = tk.Button (self.classControls, image=self.removeIcon, command=self.removeClass, width=30, height=30, relief="flat")
        trashBut.pack(side="right", padx=(3,5), pady=5)
        AddToolTip (trashBut, "Remove Class")
        self.randomizeIcon = tk.PhotoImage(file=os.path.join(script_dir, "programFiles/randomize.png"))
        self.randomizeIconSmall = self.randomizeIcon.subsample (21)
        self.randomizeIcon = self.randomizeIcon.subsample (13)
        rb = tk.Button (self.classControls, image=self.randomizeIcon, command=self.randomizeAllCodes, width=30, height=30, relief="flat")
        rb.pack(side="right", padx=3, pady=5)
        AddToolTip (rb, "Randomize All Student Codes")
        self.renameIcon = tk.PhotoImage(file=os.path.join(script_dir, "programFiles/edit.png"))
        self.renameIconSmall = self.renameIcon.subsample (21)
        self.renameIcon = self.renameIcon.subsample (13)
        eb = tk.Button (self.classControls, image=self.renameIcon, command=self.renameClass, width=30, height=30, relief="flat")
        eb.pack(side="right", padx=3, pady=5)
        AddToolTip (eb, "Rename the class")
        ab = tk.Button (self.classControls, image=self.addIcon, command=self.addStudent, width=30, height=30, relief="flat")
        ab.pack(side="right", padx=3, pady=5)
        AddToolTip (ab, "Add Student To Class")
        self.noClass = tk.Label (self.classFrame, text="No Class Selected", justify="center", font=("Helvetica",14), fg="gray", wraplength=150)
        self.noClass.pack(pady=200)

        self.classHeader2 = tk.Frame(self.classFrame)
        self.studentCountLabel = tk.Label (self.classHeader2, text="0 Students", font=("Helvetica",10))
        self.studentCountLabel.pack(side="left", padx=7, pady=3)
        self.nameDisplayOptions = ["First Middle Last", "First Last", "Last, First Middle", "Last, First", "First M. Last", "First L.", "First M. L.", "F. L.", "F. M. L."]
        self.displayAs = tk.StringVar ()
        self.displayAs.set ("First Middle Last")
        self.displayAs.trace ("w", self.displayTypeUpdated)
        tk.OptionMenu (self.classHeader2, self.displayAs, "First Middle Last", *self.nameDisplayOptions).pack (side="right", padx=(1,5), pady=5)
        tk.Label (self.classHeader2, text="Display Names As: ", font=("Helvetica",10)).pack (side="right", padx=1, pady=5)
        self.sortMethod = tk.StringVar ()
        self.sortMethod.set ("First Name")
        self.sortMethod.trace ("w", self.displayTypeUpdated)
        tk.OptionMenu (self.classHeader2, self.sortMethod, "First Name", "Last Name", "Grade L-H", "Grade H-L", "Order Added").pack (side="right", padx=(1,5), pady=5)
        tk.Label (self.classHeader2, text="Sort Students By: ", font=("Helvetica",10)).pack (side="right", padx=1, pady=5)

        self.studentsFrame = tk.Frame (self.classFrame)

        for _class in self.classList:
            self.AddClass (False, _class.name)

    #region help

    def openHelp (self):
        Help = tk.Toplevel(self.root)
        Help.title = "Help"
        tk.Button (Help, text="Classes", font=("Helvetica",18, "bold"), width=20, command=self.classHelp).pack(fill="x")
        tk.Button (Help, text="Students", font=("Helvetica",18, "bold"), width=20, command=self.studentsHelp).pack(fill="x")
        tk.Button (Help, text="eBooks", font=("Helvetica",18, "bold"), width=20, command=self.eBooksHelp).pack(fill="x")
        tk.Button (Help, text="Reports", font=("Helvetica",18, "bold"), width=20, command=self.reportsHelp).pack(fill="x")
        tk.Button (Help, text="Secure Mode", font=("Helvetica",18, "bold"), width=20, command=self.secureHelp).pack(fill="x")
        tk.Button (Help, text="Saving", font=("Helvetica",18, "bold"), width=20, command=self.saveHelp).pack(fill="x")

    def classHelp (self):
        classHelp = tk.Toplevel(self.root)
        classHelp.title = "Class Help"
        txt = tk.Text (classHelp, height=12, width=120)
        txt.pack ()
        info = """
        All classes are displayed in the classes panel on the left of the screen. 
        A new class can be added by clicking on the plus icon in the upper right corner of the classes panel. 
        To select a class, click on one of the buttons in the classes panel. When selected, 
        it will turn light blue, and the class properties will be displayed on the right of the class panel. 
        This includes the class’s students, name, and eBook. Once you have a class selected,
        you may rename it by clicking the pencil icon, delete it by clicking the trash icon,
        or change its eBook by choosing one from the drop down menu. 
        There are also several drop downs that determine how the students are displayed. You may 
        select another class from the class panel at any time."""
        txt.insert ("end", info)

    def studentsHelp (self):
        classHelp = tk.Toplevel(self.root)
        classHelp.title = "Students Help"
        txt = tk.Text (classHelp, height=20, width=100)
        txt.pack ()
        info = """
        Students can be added to a class by selecting the class, 
        and then clicking the plus icon in the upper left corner. 
        After clicking the plus icon, you must set the student’s name and grade. 
        After you click confirm, the student will be added to the class. 
        Additionally, a random access code will be assigned to each student. 
        This can be changed, but the new access code cannot match the code of any 
        students in the class. All the properties of a student can be edited by 
        clicking the pencil icon, and students can be removed from a class by 
        clicking the trash icon. If you wish to assign the student a new random access code, 
        you may click the randomize icon. It is important to remember that in each class, 
        there can only be one student with the same name and grade."""
        txt.insert ("end", info)

    def eBooksHelp (self):
        classHelp = tk.Toplevel(self.root)
        classHelp.title = "eBooks Help"
        txt = tk.Text (classHelp, height=10, width=100)
        txt.pack ()
        info = """
        The eBook menu can be accessed by clicking the eBook button in the menu bar. 
        Here, you can add an eBook by clicking the plus icon in the upper left 
        corner of the program, or you can delete previously added eBooks. Once an eBook is added, 
        you can select it in the eBook drop down menu of the class view. 
        You can also access eBooks by clicking “Add New eBook” in this menu."""
        txt.insert ("end", info)
    
    def reportsHelp (self):
        classHelp = tk.Toplevel(self.root)
        classHelp.title = "Reports Help"
        txt = tk.Text (classHelp, height=20, width=100)
        txt.pack ()
        info = """
        In order to access the report menu, select “View Reports” in the menu bar. 
        In this window, you can view any previous reports by clicking the one you 
        wish to open, or you can generate a new one. Reports display every student and 
        their grade, classes, books, and access codes as they were at the time the 
        report was generated. When viewing a report, you have to option to delete the 
        report or recover the data from the report. If you recover the data, 
        the main save file will be overridden and the program will revert back 
        to how it was when the report was made. This will cause the program to restart. 
        Reports are automatically generated if you open the program and its been over 
        week since it was last opened. This means if something happens to the primary save file, 
        or you wish to revert to any previous reports, you have lots of back-ups that you 
        can recover information from. You also have the option to organize 
        the students in the report by class. This can be done by clicking the 
        check box in the upper left while viewing a report."""
        txt.insert ("end", info)

    def secureHelp (self):
        classHelp = tk.Toplevel(self.root)
        classHelp.title = "Secure Mode Help"
        txt = tk.Text (classHelp, height=14, width=110)
        txt.pack ()
        info = """
        The security window can be accessed by clicking the “Security” button in the menu bar. 
        In this window you can set a password to lock the program and activate secure mode. 
        When secure mode is activated, the program will be locked until the correct password is entered. 
        If you forget the password, you can reset the program, but this will result in the loss 
        of any information that was saved. The save files of the program will also be encrypted 
        when secure mode is activated. While secure mode is activated, you can change the password 
        or deactivate secure mode in the security window."""
        txt.insert ("end", info)

    def saveHelp (self):
        classHelp = tk.Toplevel(self.root)
        classHelp.title = "Secure Mode Help"
        txt = tk.Text (classHelp, height=8, width=120)
        txt.pack ()
        info = """
        All information is saved automatically in an XML file when the application is closed. 
        You can reset the program and clear the save file by clicking “Clear Save” in the menu bar. 
        If you wish to make a backup of the program’s information, you can click 
        the “generate report manually” button in the reports window (see reports section)."""
        txt.insert ("end", info)

    #endregion

    #region security

    def checkPassword (self, passwordEntry):
        if (passwordEntry.get() == self.prefsXML.get ("password")):
            self.removeAllWidgets (self.root)
            self.setUpWindow()
        else:
            passwordEntry.delete (0, "end") 
            passwordEntry.insert (0, "Password Incorrect")

    def secure (self): 
        reportsRoot = tk.Toplevel()
        reportsRoot.title ("Secure")
        reportsRoot.geometry ("400x400")
        password = self.createEntry (reportsRoot, "Enter A Password", 25, 15, "top", 0, 5)

        if (not self.secureMode):
            tk.Button (reportsRoot, text="Activate Secure Mode", font=("Helvetica",12), command = lambda:self.activateSecure(reportsRoot, password.get())).pack(fill="x")
        else:
            tk.Button (reportsRoot, text="Change Password", font=("Helvetica",12), command = lambda:self.changePass(reportsRoot, password.get())).pack(fill="x")
            tk.Button (reportsRoot, text="Deactivate Secure Mode", font=("Helvetica",12), command = lambda:self.deactivateSecure(reportsRoot)).pack(fill="x")

    def activateSecure (self,root,password):
        self.secureMode = True
        self.prefsXML.set ("secureMode", "1")
        self.prefsXML.set ("password", password)
        root.destroy()

    def deactivateSecure (self,root):
        self.secureMode = False
        self.prefsXML.set ("secureMode", "0")
        root.destroy()

    def changePass (self, root, newPass):
        self.prefsXML.set ("password", newPass)
        root.destroy()

    #endregion

    #region report

    def openReportsWindow (self):
        reportsRoot = tk.Toplevel()
        reportsRoot.title ("Reports")
        reportsRoot.geometry ("400x400")

        for File in os.listdir (os.path.join(script_dir, "programFiles/reports")):
            tk.Button (reportsRoot, text="Report For " + File[:-4], font=("Helvetica",12), command=lambda f=File:self.showReport(reportsRoot, os.path.join(script_dir, "programFiles/reports/" + f), f)).pack(fill="x")
        tk.Button (reportsRoot, text="Generate Report Manually", font=("Helvetica",10), command=lambda:[reportsRoot.destroy(), self.generateReport(), self.openReportsWindow()]).pack(pady=20)
        tk.Label (reportsRoot, text="Reports Generated Weekly", font=("Helvetica",10), fg="gray").pack()
        reportsRoot.mainloop()

    def showReport (self, winRoot, xml, file):
        reportRoot = tk.Toplevel()
        reportRoot.title ("Report " + file[:-4])
        reportRoot.geometry ("600x400")
        header = tk.Frame (reportRoot)
        header.pack(fill="x")
        tk.Button (header, text="Delete Report", font=("Helvetica",10,"bold"), command=lambda:[reportRoot.destroy(), os.remove(xml), winRoot.destroy(), self.openReportsWindow()]).pack (padx=10, pady=5,side="left")
        tk.Button (header, text="Recover From Report", font=("Helvetica",10,"bold"), command=lambda:self.recover(xml)).pack (padx=10, pady=5, side="right")
        chart = tk.Frame (reportRoot)
        chart.pack()
        var = tk.IntVar()
        var.set (0)
        var.trace ("w", lambda *args, r=reportRoot, c=chart, XML=xml:self.reportOrganChanged(r, c, XML, var.get()))
        tk.Checkbutton (header, text="Organize by Class", font=("Helvetica",10), variable=var).pack (side="left")
        self.createChart (xml, chart, var.get())

    def reportOrganChanged (self, root, chart, xml, org):
        self.removeAllWidgets (chart)
        self.createChart(xml, chart, org)

    def createChart (self, xml, chart, org):
        classes = list()
        try:
            tree = ET.parse(xml)
        except:
            self.decryptXML (xml, "carson s")
            tree = ET.parse(xml)
        root = tree.getroot()
        classesXML = root[0]
        for _class in classesXML.findall("class"):
            newClass = Class(_class.get ("name"))
            newClass.book = _class.get ("book")
            for _student in _class.findall("student"):
                newStudent = student(
                    _student.get("first"), 
                    _student.get("middle"),
                    _student.get("last"),
                    _student.get("grade"),
                    _student.get("code"),
                )
                newClass.students.append (newStudent)
            classes.append (newClass)

        if (org):
            r = 1
            for _class in classes:
                tk.Label (chart, text=_class.name, font=("Helvetica", 14, "bold")).pack(padx=10, pady=10)
                classFrame = tk.Frame(chart)
                classFrame.pack()
                tk.Label (classFrame, text="Name", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=0, sticky="w e", ipadx=5, ipady=5)
                tk.Label (classFrame, text="Grade", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=1, sticky="w e", ipadx=5, ipady=5)
                tk.Label (classFrame, text="Access Codes", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=4, sticky="w e", ipadx=5, ipady=5)
                for stu in _class.students:
                    tk.Label (classFrame, text=stu.first+" "+stu.middle+" "+stu.last, relief="solid", font=("Helvetica", 12)).grid(row=r,column=0, sticky="w e", ipadx=5, ipady=5)
                    tk.Label (classFrame, text=stu.grade, font=("Helvetica", 12), relief="solid").grid(row=r,column=1, sticky="w e", ipadx=5, ipady=5)
                    codeLabel = tk.Label (classFrame, text=stu.code, font=("Helvetica", 12), relief="solid")
                    codeLabel.grid(row=r,column=4, sticky="w e", ipadx=5, ipady=5)
                    r = r+1
        else:
            tk.Label (chart, text="Name", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=0, sticky="w e", ipadx=5, ipady=5)
            tk.Label (chart, text="Grade", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=1, sticky="w e", ipadx=5, ipady=5)
            tk.Label (chart, text="Classes", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=2, sticky="w e", ipadx=5, ipady=5)
            tk.Label (chart, text="Books", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=3, sticky="w e", ipadx=5, ipady=5)
            tk.Label (chart, text="Access Codes", relief="solid", font=("Helvetica",10,"bold")).grid(row=0,column=4, sticky="w e", ipadx=5, ipady=5)

            studentsUsed = list()
            classLabels = list()
            bookLabels = list()
            codeLabels = list()
            r = 1
            for _class in classes:
                for stu in _class.students:
                    if (self.studentContainedInList (stu, studentsUsed) == None):
                        tk.Label (chart, text=stu.first+" "+stu.middle+" "+stu.last, relief="solid").grid(row=r,column=0, sticky="w e", ipadx=5, ipady=5)
                        tk.Label (chart, text=stu.grade, relief="solid").grid(row=r,column=1, sticky="w e", ipadx=5, ipady=5)
                        classLabel = tk.Label (chart, text=_class.name, relief="solid")
                        classLabel.grid(row=r,column=2, sticky="w e", ipadx=5, ipady=5)
                        classLabels.append (classLabel)
                        bookLabel = tk.Label (chart, text=_class.book, relief="solid")
                        bookLabel.grid(row=r,column=3, sticky="w e", ipadx=5, ipady=5)
                        bookLabels.append (bookLabel)
                        codeLabel = tk.Label (chart, text=stu.code, relief="solid")
                        codeLabel.grid(row=r,column=4, sticky="w e", ipadx=5, ipady=5)
                        codeLabels.append (codeLabel)
                        studentsUsed.append (stu)
                        r = r+1
                    else:
                        index = studentsUsed.index(self.studentContainedInList (stu, studentsUsed))
                        classesTx = classLabels[index]["text"]
                        classLabels[index]["text"] = classesTx + ", " + _class.name
                        booksTx = bookLabels[index]["text"]
                        bookLabels[index]["text"] = booksTx + ", " + _class.book
                        codeTx = codeLabels[index]["text"]
                        codeLabels[index]["text"] = codeTx + ", " + stu.code

    def recover (self, xml):
        savefile = open (os.path.join(script_dir, "programFiles/saveFile.xml"), "w")
        backup = open (xml, "r")
        savefile.write (backup.read())
        savefile.close()
        backup.close()
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def generateReport (self):
        self.saveXML()
        savefile = open (os.path.join(script_dir, "programFiles/saveFile.xml"), "r")
        path = os.path.join(script_dir, "programFiles/reports/" + str(datetime.datetime.today().date())) + ".xml"
        count = 1
        while (os.path.isfile (path)):
            path = os.path.join(script_dir, "programFiles/reports/" + str(datetime.datetime.today().date())) + " " + str(count) + ".xml"
            count = count + 1
        reportFile = open(path, "w")
        reportFile.write(savefile.read())
        reportFile.close()
        savefile.close()

    def studentContainedInList (self, stu, stuList):
        for s in stuList:
            if (stu.first == s.first and stu.middle == s.middle and stu.last == s.last and stu.grade == s.grade):
                return s
        return None

    #endregion

    #region classes

    def AddClass (self, new, name=""):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return

        if (new):
            defaultClassName = "New Class"
            if len(self.classList) > 0:
                defaultClassName = "New Class " + str(len(self.classList) + 1)
        else:
            defaultClassName = name

        if (new):
            self.classList.append (Class(defaultClassName))
            classElement = ET.SubElement (self.classesXML, "class")
            classElement.set ("name", defaultClassName)

        if len(self.classButtonList) == 0:
            self.addClassInst.destroy()

        button = tk.Button (self.classesFrame, text=defaultClassName, font=("Helvetica",12), command=lambda:self.viewClass(self.classButtonList.index(button)))
        self.classButtonList.append (button)
        button.pack (fill="x",padx=5, pady=1)

    def viewClass (self, classIndex):
        if (self.classSelected == None or self.classSelected != self.classList[classIndex]):
            if (self.classSelected != None):
                oldIndex = self.classList.index(self.classSelected)
                self.classButtonList[oldIndex]["bg"] = "SystemButtonFace"
                self.classButtonList[oldIndex]["relief"] = "raised"
            else:
                self.noClass.pack_forget()
                self.classHeader.pack(fill="x", side="top")
                self.classHeader2.pack(fill="x", side="top")
                self.studentsFrame.pack(fill="x")

            self.classSelected = self.classList[classIndex]
            self.removeAllWidgets (self.studentsFrame)
            self.createStudentFrames()

            self.classTitle["text"] = self.classSelected.name
            self.updateClassCount()
            self.classBook.set(self.classSelected.book)
            self.classButtonList[classIndex]["bg"] = "pale turquoise"
            self.classButtonList[classIndex]["relief"] = "sunken"

    #endregion

    #region class

    def renameClass (self):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return
        else:
            self.inAction = True
        self.classTitle.pack_forget()
        self.classControls.pack_forget()
        tk.Label (self.classHeader, text="Rename Class: ")
        self.classNameEntry = tk.Entry (self.classHeader, font=("Helvetica",12))
        self.classNameEntry.insert (0, self.classSelected.name)
        self.classNameEntry.pack (side="left", fill="both", padx=5, pady=5)
        self.confirmName = tk.Button (self.classHeader, text="Cancel", font=("Helvetica",12), command=lambda:self.renameClassConfirm(False))
        self.confirmName.pack (side="right", padx=(1,5), pady=5)
        self.cancelName = tk.Button (self.classHeader, text="Confirm", font=("Helvetica",12), command=lambda:self.renameClassConfirm(True))
        self.cancelName.pack (side="right", padx=1, pady=5)

    def renameClassConfirm (self, confirmed):
        self.inAction = False

        if (confirmed):
            self.classSelected.name = self.classNameEntry.get()
            self.classTitle["text"] = self.classSelected.name
            self.classButtonList[self.classList.index(self.classSelected)]["text"] = self.classSelected.name
            self.classesXML[self.classList.index(self.classSelected)].set("name", self.classSelected.name)

        self.classNameEntry.destroy()
        self.confirmName.destroy()
        self.cancelName.destroy()
        self.classTitle.pack (side="left", padx=5, pady=5)
        self.classControls.pack (side="right")
        self.classButtonList[self.classList.index(self.classSelected)]["text"] = self.classSelected.name

    def removeClass (self):
        self.inAction = False        
        self.classHeader.pack_forget()
        self.classHeader2.pack_forget()
        self.studentsFrame.pack_forget()
        self.noClass.pack(pady=200)

        index = self.classList.index(self.classSelected)
        self.classButtonList[index].destroy()
        del self.classButtonList[index]
        self.classList.remove (self.classSelected)
        self.classesXML.remove (self.classesXML[index])
        self.classSelected = None

    def updateClassCount (self):
        studentLabel = str(len(self.classSelected.students))
        if (len(self.classSelected.students) == 1): 
            studentLabel += " Student"
        else:
            studentLabel += " Students"
        self.studentCountLabel["text"] = studentLabel

    def addStudent (self):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return
        else:
            self.inAction = True

        self.removeAllWidgets(self.studentsFrame)

        studentFrame = tk.Frame (self.studentsFrame, bg="pale turquoise")
        studentFrame.pack(side="top", padx=(10,40), pady=5, fill="x")
        firstname = self.createEntry (studentFrame, "First", 8, 12, "left", (5,1), 5)
        middlename = self.createEntry (studentFrame, "Middle", 8, 12, "left", 1, 5)
        lastname = self.createEntry (studentFrame, "Last", 8, 12, "left", 1, 5)
        grade = tk.StringVar(studentFrame)
        grade.set ("Grade")
        gradeSelect = tk.OptionMenu (studentFrame, grade, "K","1","2","3","4","5","6","7","8","9","10","11","12")
        gradeSelect.pack(side="left", padx=1, pady=5)
        gradeSelect.config (font=("Helvetica",8))
        tk.Button (studentFrame, text="Cancel", font=("Helvetica",12), command=lambda:self.cancelStudent(studentFrame)).pack (side="right", padx=(1,5), pady=5)
        tk.Button (studentFrame, text="Confirm", font=("Helvetica",12), command=lambda:self.confirmStudent(studentFrame, firstname.get(), middlename.get(), lastname.get(), grade.get(), accessCode.get())).pack (side="right", padx=1, pady=5)
        accessCode = tk.Entry (studentFrame, font=("Helvetica",12), width=6)
        accessCode.pack (side="right", fill="y", padx=10, pady=5)
        accessCode.insert (0, self.generateAccessCode(5))

        self.createStudentFrames ()

    def confirmStudent (self, frame, first, middle, last, grade, code):
        self.inAction = False
        if (str.strip(first)=="" or str.strip(middle)=="" or str.strip(last)=="" or str.strip(code)=="" or grade=="Grade"):
            self.errorMessage ("You must assign all the students information")
            return
        if (self.codeExists (code)):
            self.errorMessage ("This code is already assigned to a student")
            return

        stu = student (first, middle, last, grade, code)
        if (self.studentContainedInList (stu, self.classSelected.students)):
            self.errorMessage ("This student is already in the class")
            return
        self.classSelected.students.append (stu)
        stuXML = ET.SubElement (self.classesXML[self.classList.index(self.classSelected)], "student")
        stuXML.set ("first", stu.first)
        stuXML.set ("middle", stu.middle)
        stuXML.set ("last", stu.last)
        stuXML.set ("grade", stu.grade)
        stuXML.set ("code", stu.code)
        self.updateClassCount()

        self.removeAllWidgets(self.studentsFrame)
        
        self.createStudentFrames ()
        self.classHeader.pack(side="top", fill="x")

    def cancelStudent (self, studentFrame):
        self.inAction = False
        self.removeAllWidgets(self.studentsFrame)
        self.createStudentFrames()

    def displayTypeUpdated (self, *args):
        self.removeAllWidgets(self.studentsFrame)
        self.createStudentFrames()

    #endregion

    #region ebooks

    def EbookUpdated (self, *args):
        if (not self.classSelected == None):
            self.classSelected.book = self.classBook.get()
            self.classesXML[self.classList.index(self.classSelected)].set ("book", self.classBook.get())

    def OpenEbookMenu(self):
        self.booksRoot = tk.Toplevel()
        self.booksRoot.title ("EBooks")
        self.booksRoot.geometry ("400x400")
        tk.Button (self.booksRoot, text="Add New EBook", font=("Helvetica",12), command=self.addEBook).pack(fill="x")
        self.EBookFrames = list()
        self.displayEBookList()
        self.booksRoot.mainloop()

    def addEBook (self):
        frame = tk.Frame (self.booksRoot, bg="pale turquoise")
        frame.pack(fill="x")
        nameEntry = self.createEntry (frame, "Book Name", 15, 12, "left", 5, 5)
        tk.Button (frame, text="Cancel", command=lambda:self.confirmEBook(frame, nameEntry, True)).pack (side="right", padx=1, pady=5)
        tk.Button (frame, text="Confirm", command=lambda:self.confirmEBook(frame, nameEntry, False)).pack (side="right", padx=(1,5), pady=5)

    def confirmEBook (self, frame, entry, canceled):
        self.inAction = False
        if (not canceled):
            self.bookList.append (entry.get())
            self.refreshEBookMenu()
            ET.SubElement (self.booksXML, "book").set ("name", entry.get())
        frame.destroy()
        self.displayEBookList()

    def displayEBookList (self):
        copyOfFrames = self.EBookFrames.copy()
        for Frame in copyOfFrames:
            self.EBookFrames.remove (Frame)
            Frame.destroy()

        count = 0
        for book in self.bookList:
            count=count+1
            self.displayEbookPanel (book, count)

    def displayEbookPanel (self, book, count):
        frame = tk.Frame (self.booksRoot)
        self.EBookFrames.append (frame)
        frame.pack(fill="x")
        BG = "gray70"
        if (count % 2 > 0):
            BG = "light gray"
        frame["bg"] = BG
        tk.Label (frame, text=book, font=("Helvetica",10), bg=BG).pack(side="left")
        rb = tk.Button (frame, image=self.removeIconSmall, command=lambda:self.removeEBook(book), width=20, height=20, relief="flat", bg=BG)
        rb.pack (side="right", padx=(1,5), pady=5)
        AddToolTip (rb, "Remove EBook")
        rn = tk.Button (frame, image=self.renameIconSmall, command=lambda:[self.renameEbook(frame, book),self.bookList.remove(book)], width=20, height=20, relief="flat", bg=BG)
        rn.pack (side="right", padx=1, pady=5)
        AddToolTip (rn, "Rename EBook")

    def refreshEBookMenu(self):
        self.bookList.sort (key=lambda s: s.lower())

        self.bookMenu["menu"].delete(0, "end")
        if (not self.classBook.get() in self.classList):
            self.classBook.set ("None")
            self.bookMenu["menu"].add_command(label="None", command=tk._setit(self.classBook, "None"))
            self.bookMenu["menu"].add_separator()

        for book in self.bookList:
            self.bookMenu["menu"].add_command(label=book, command=tk._setit(self.classBook, book))
        self.bookMenu["menu"].add_separator ()
        self.bookMenu["menu"].add_command(label="Add New Book", command=self.OpenEbookMenu)

    def removeEBook (self, book):
        self.booksXML.remove (self.booksXML[self.bookList.index(book)])
        self.bookList.remove (book)
        self.displayEBookList()

    def renameEbook (self, frame, book):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return
        else:
            self.inAction = True
        self.removeAllWidgets (frame)
        nameEntry = tk.Entry (frame, font=("Helvetica",12))
        nameEntry.insert (0, book)
        nameEntry.pack (side="left", fill="both", padx=5, pady=5)
        tk.Button (frame, text="Cancel", command=lambda:self.cancelRename(frame, book)).pack (side="right", padx=1, pady=5)
        tk.Button (frame, text="Confirm", command=lambda:self.confirmEBook(frame, nameEntry, False)).pack (side="right", padx=(1,5), pady=5)

    def cancelRename (self, frame, book):
        self.inAction= False
        self.removeAllWidgets (frame)
        BG = frame["bg"]
        tk.Label (frame, text=book, font=("Helvetica",10), bg=BG).pack(side="left")
        tk.Button (frame, image=self.removeIconSmall, command=lambda:self.removeEBook(book), width=20, height=20, relief="flat", bg=BG).pack (side="right", padx=(1,5), pady=5)
        tk.Button (frame, image=self.renameIconSmall, command=lambda:[self.renameEbook(frame, book),self.bookList.remove(book)], width=20, height=20, relief="flat", bg=BG).pack (side="right", padx=1, pady=5)

    #endregion

    def removeAllWidgets (self, parent):
        slaves = list(parent.children.values())
        for slave in slaves:
            slave.destroy()

    #region codes

    def randomizeAllCodes (self):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return
        self.removeAllWidgets(self.studentsFrame)
        for stu in self.classSelected.students:
            stu.code = self.generateAccessCode (5)
            self.classesXML[self.classList.index(self.classSelected)][self.classSelected.students.index(stu)].set ("code", stu.code)
        self.createStudentFrames ()

    def generateAccessCode (self, length): 
        code = self.randomCode(length)
        while (self.codeExists (code)):
            code = self.randomCode(length)
        return code

    def codeExists (self, code):
        for stu in self.classSelected.students:
            if (code == stu.code):
                return True
        return False

    def codeExistsExceptStudent (self, code, stu):
        for s in self.classSelected.students:
            if (code == s.code and not s==stu):
                return True
        return False

    def randomCode (self, length):
        code = ""
        for i in range(length):
            rnd = random.randint(0,2)
            if (rnd == 0):
                code += self.alphabet[random.randrange (0, len(self.alphabet))].upper()
            elif (rnd == 1):
                code += self.alphabet[random.randrange (0, len(self.alphabet))]
            else:
                code += str(random.randint (0,9))
        return code

    #endregion

    #region student

    def createStudentFrames (self):
        classIndex = self.classList.index(self.classSelected)
        studentsSorted = {
            "First Name":sorted(self.classList[classIndex].students, key=lambda s: str.lower(s.first)),
            "Last Name":sorted(self.classList[classIndex].students, key=lambda s: str.lower(s.last)),
            "Grade L-H":sorted(self.classList[classIndex].students, key=lambda s: 0 if s.grade == "K" else int(s.grade)),
            "Grade H-L":sorted(self.classList[classIndex].students, key=lambda s: 0 if s.grade == "K" else int(s.grade), reverse=True),
            "Order Added":self.classSelected.students
        }[self.sortMethod.get()]
        for stu in studentsSorted:
            self.createStudentFrame (classIndex, stu)

    def createStudentFrame (self, classIndex, stu):
        studentFrame = tk.Frame (self.studentsFrame, bg="pale turquoise")
        studentFrame.pack(side="top", padx=(10,40), pady=5, fill="x")
        tk.Label (studentFrame, text=self.convertNameToDisplayType(stu.first, stu.middle, stu.last), font=("Helvetica",10), bg="pale turquoise").pack (side="left", padx=5, pady=5)
        tk.Label (studentFrame, text="Grade: " + stu.grade, font=("Helvetica",10), bg="pale turquoise").pack (side="left", padx=5, pady=5)
        rb = tk.Button (studentFrame, image=self.removeIconSmall, command=lambda:self.removeStudent(studentFrame, stu), width=20, height=20, relief="flat", bg="pale turquoise")
        rb.pack (side="right", padx=(1,5), pady=5)
        AddToolTip(rb, "Remove Student")
        rndb = tk.Button (studentFrame, image=self.randomizeIconSmall, command=lambda:self.randomizeStudentCode(stu, codeLabel), width=20, height=20, relief="flat", bg="pale turquoise")
        rndb.pack (side="right", padx=1, pady=5)
        AddToolTip (rndb, "Randomize Student's Code")
        eb = tk.Button (studentFrame, image=self.renameIconSmall, command=lambda:self.editStudent(studentFrame, stu), width=20, height=20, relief="flat", bg="pale turquoise")
        eb.pack (side="right", padx=1, pady=5)
        AddToolTip (eb, "Edit Student")
        codeLabel = tk.Label (studentFrame, text="Access Code: " + stu.code, font=("Helvetica",10), bg="pale turquoise")
        codeLabel.pack (side="right", padx=20, pady=5)

    def convertNameToDisplayType (self, first, middle, last):
        displayType = self.displayAs.get()
        displayType = displayType.replace ("First", first)
        displayType = displayType.replace ("Middle", middle)
        displayType = displayType.replace ("Last", last)
        displayType = displayType.replace ("F.", first[0] + ".")
        displayType = displayType.replace ("M.", middle[0] + ".")
        displayType = displayType.replace ("L.", last[0] + ".")
        return displayType

    def editStudent (self, frame, stu):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return
        else:
            self.inAction = True

        self.removeAllWidgets (frame)
        firstname = tk.Entry (frame, font=("Helvetica",12), width=8)
        firstname.pack (side="left", fill="y", padx=(5,1), pady=5)
        firstname.insert (0, stu.first)
        middlename = tk.Entry (frame, font=("Helvetica",12), width=8)
        middlename.pack (side="left", fill="y", padx=1, pady=5)
        middlename.insert (0, stu.middle)
        lastname = tk.Entry (frame, font=("Helvetica",12), width=8)
        lastname.pack (side="left", fill="y", padx=1, pady=5)
        lastname.insert (0, stu.last)
        grade = tk.StringVar(frame)
        grade.set (stu.grade)
        gradeSelect = tk.OptionMenu (frame, grade, "K","1","2","3","4","5","6","7","8","9","10","11","12")
        gradeSelect.pack(side="left", padx=1, pady=5)
        gradeSelect.config (font=("Helvetica",8))
        tk.Button (frame, text="Cancel", font=("Helvetica",12), command=lambda:self.cancelStudent(frame)).pack (side="right", padx=(1,5), pady=5)
        tk.Button (frame, text="Confirm", font=("Helvetica",12), command=lambda:self.confirmStudentEdit(frame, stu, firstname.get(), middlename.get(), lastname.get(), grade.get(), accessCode.get())).pack (side="right", padx=1, pady=5)
        accessCode = tk.Entry (frame, font=("Helvetica",12), width=6)
        accessCode.pack (side="right", fill="y", padx=10, pady=5)
        accessCode.insert (0, str(stu.code))

    def randomizeStudentCode (self, stu, codeLabel):
        stu.code = self.generateAccessCode (5)
        self.classesXML[self.classList.index(self.classSelected)][self.classSelected.students.index(stu)].set ("code", stu.code)
        codeLabel["text"] = "Access Code: " + stu.code

    def confirmStudentEdit (self, frame, stu, first, middle, last, grade, code):
        self.inAction = False
        if (self.codeExistsExceptStudent(code, stu)):
            self.errorMessage ("This code is already assigned to another student.")
            return
        if (str.strip(first)=="" or str.strip(middle)=="" or str.strip(last)=="" or str.strip(code)=="" or grade=="Grade"):
            self.errorMessage ("You must assign all the students information")
            return

        st = student (first, middle, last, grade, code)
        if (self.studentContainedInList (st, self.classSelected.students)):
            self.errorMessage ("This student is already in the class")
            return

        stu.first = first
        stu.middle = middle
        stu.last = last
        stu.grade = grade
        stu.code = code

        stuXML = self.classesXML[self.classList.index(self.classSelected)][self.classSelected.students.index(stu)]
        stuXML.set ("first", stu.first)
        stuXML.set ("middle", stu.middle)
        stuXML.set ("last", stu.last)
        stuXML.set ("grade", stu.grade)
        stuXML.set ("code", stu.code)

        tk.Label (frame, text=stu.first+" "+stu.middle+" "+stu.last, font=("Helvetica",12), bg="pale turquoise").pack (side="left", padx=5, pady=5)
        tk.Label (frame, text="Grade: " + stu.grade, font=("Helvetica",12), bg="pale turquoise").pack (side="left", padx=5, pady=5)
        tk.Button (frame, text="Remove", font=("Helvetica",10), command=lambda:self.removeStudent(frame, stu)).pack (side="right", padx=(1,5), pady=5)
        tk.Button (frame, text="Edit", font=("Helvetica",10), command=lambda:self.editStudent(frame, stu)).pack (side="right", padx=1, pady=5)
        tk.Label (frame, text="Access Code: " + stu.code, font=("Helvetica",12), bg="pale turquoise").pack (side="right", padx=20, pady=5)

        self.removeAllWidgets (self.studentsFrame)
        self.createStudentFrames ()

    def cancelStudentEdit (self, frame, stu):
        self.inAction = False
        self.removeAllWidgets (frame)

        tk.Label (frame, text=stu.first+" "+stu.middle+" "+stu.last, font=("Helvetica",12), bg="pale turquoise").pack (side="left", padx=5, pady=5)
        tk.Label (frame, text="Grade: " + stu.grade, font=("Helvetica",12), bg="pale turquoise").pack (side="left", padx=5, pady=5)
        tk.Button (frame, text="Remove", font=("Helvetica",10), command=lambda:self.removeStudent(frame, stu)).pack (side="right", padx=(1,5), pady=5)
        tk.Button (frame, text="Edit", font=("Helvetica",10), command=lambda:self.editStudent(frame, stu)).pack (side="right", padx=1, pady=5)
        tk.Label (frame, text="Access Code: " + stu.code, font=("Helvetica",12), bg="pale turquoise").pack (side="right", padx=20, pady=5)

    def removeStudent (self, frame, stu):
        if (self.inAction):
            self.errorMessage ("You must Confirm/Cancel the first action first.")
            return
        frame.destroy()
        classXML = self.classesXML[self.classList.index(self.classSelected)]
        classXML.remove(classXML[self.classSelected.students.index(stu)])
        self.classSelected.students.remove (stu)
        self.updateClassCount()

    #endregion

    #region Entries

    def entryFocusIn (self, entry, defaultText):
        if (entry.get() == defaultText):
            entry.delete (0, "end")
            entry.insert (0, "")
            entry["fg"] = "black"

    def entryFocusOut (self, entry, defaultText):
        if (entry.get() == ""):
            entry.insert (0, defaultText)
            entry["fg"] = "gray"

    def createEntry (self, frame, defaultText, length, fontSize, position, px, py):
        entry = tk.Entry (frame, font=("Helvetica",fontSize), fg="gray", width=length)
        entry.pack(side=position, padx=px, pady=py, fill="y")
        entry.insert (0, defaultText)
        entry.bind ("<FocusIn>", lambda event: self.entryFocusIn(entry, defaultText))
        entry.bind ("<FocusOut>", lambda event: self.entryFocusOut (entry, defaultText))
        return entry

        #endregion

    #region XML  

    def createXML (self):
        self.data = ET.Element ("data")
        self.classesXML = ET.SubElement (self.data, "classes")
        self.booksXML = ET.SubElement (self.data, "books")
        self.prefsXML = ET.SubElement (self.data, "prefs")
        self.prefsXML.set ("secureMode", str(0))
        self.data.set ("lastTime", datetime.datetime.today().strftime('%Y-%m-%d'))
        self.lastTime = datetime.datetime.now().date()
        mydata = ET.tostring(self.data, encoding="unicode")  
        myfile = open(os.path.join(script_dir, "programFiles/saveFile.xml"), "w")
        myfile.write(mydata)

    def loadXML (self):
        try:
            self.tree = ET.parse(os.path.join(script_dir, "programFiles/saveFile.xml")) 
        except:
            self.decryptXML (os.path.join(script_dir, "programFiles/saveFile.xml"), "carson s")
            self.tree = ET.parse(os.path.join(script_dir, "programFiles/saveFile.xml")) 
        root = self.tree.getroot()
        self.data = root
        self.classesXML = root[0]
        self.booksXML = root[1]
        self.prefsXML = root[2]
        for _class in self.classesXML.findall("class"):
            newClass = Class(_class.get ("name"))
            newClass.book = _class.get ("book")
            for _student in _class.findall("student"):
                newStudent = student(
                    _student.get("first"), 
                    _student.get("middle"),
                    _student.get("last"),
                    _student.get("grade"),
                    _student.get("code"),
                )
                newClass.students.append (newStudent)
            self.classList.append (newClass)
        for book in self.booksXML.findall ("book"):
            self.bookList.append (book.get("name"))
        sm = (int)(root[2].get("secureMode"))
        self.secureMode = sm == 1
        time = str.split(root.get ("lastTime"), "-")
        self.lastTime = datetime.date ((int)(time[0]), (int)(time[1]), (int)(time[2]))

    def saveXML (self):
        self.saved = True

        if (self.loaded):
            self.data.set ("lastTime", datetime.datetime.today().strftime('%Y-%m-%d'))
            self.tree.write (os.path.join(script_dir, "programFiles/saveFile.xml"))
        else:
            mydata = ET.tostring(self.data, encoding="unicode")
            myfile = open (os.path.join(script_dir, "programFiles/saveFile.xml"), "w")
            myfile.write (mydata)
            myfile.close()
        self.encryptXML (os.path.join(script_dir, "programFiles/saveFile.xml"), "carson s")

        currentDT = datetime.datetime.today().date()
        if ((currentDT - self.lastTime).days >= 7):
            self.generateReport()

    def encryptXML (self, file, key):
        if (not self.secureMode):
            return

        myfile = open(file, "r+")
        fileContents = myfile.read()
        encoded_chars = []
        for i in range(len(fileContents)):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(fileContents[i]) + ord(key_c) % 256)
            encoded_chars.append(encoded_c)
        myfile.truncate(0)
        myfile.seek(0)
        myfile.write(repr("".join(encoded_chars)))
        myfile.close()

    def decryptXML (self, file, key):
        myfile = open(file, "r+")
        fileContents = eval(myfile.read())        
        dec = []
        for i in range(len(fileContents)):
            key_c = key[i % len(key)]
            dec_c = chr ((ord(fileContents[i]) - ord(key_c) + 256) % 256)
            dec.append(dec_c)
            myfile.truncate(0)
        myfile.seek(0)
        myfile.write("".join(dec))
        myfile.close()

    def clearSave (self):
        os.remove (os.path.join(script_dir, "programFiles/saveFile.xml"))
        python = sys.executable
        os.execl(python, python, * sys.argv)

    #endregion

    #region userFeedback

    def errorMessage (self, label):
        root = tk.Toplevel()
        root.title ("EBook Program")
        tk.Label (root, text=label, justify="center").pack(pady=20)
        tk.Button (root, text="OK", width=25, command=root.destroy).pack(pady=20)

    #endregion

    def quitApp (self):
        self.saveXML ()
        self.root.destroy()

class AddToolTip(object):
    def __init__(self, widget, text):
        self.waittime = 500   
        self.wraplength = 180  
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
        background="#ffffff", relief='solid', borderwidth=1,
        wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

program = RunProgram()
program.root.mainloop()
