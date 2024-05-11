import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QTableWidgetItem, QFileDialog
from PyQt5 import QtCore as core, QtGui
from PyQt5.uic import loadUi
from PyQt5.uic.properties import QtCore
from mysql.connector import connect, errorcode
import mysql.connector as mc
import time
from dataset_creator import createDataSet
from datetime import date,datetime
from training import generateQR, trainData, dumpEncodings
from imutils import paths
from run import AttendanceSystem
from reports import getReports, send_mail, send_msg


try:
    Cont = connect(host="localhost", user="root", password="", database="management_auto_attendance_system")
except mc.Error as error:
    print(f"Error is {error}")
MyCur = Cont.cursor()


class MainPage(QMainWindow):
    def __init__(self):
        super(MainPage, self).__init__()
        loadUi("Application_UI//ResponsiveWindows//System.ui", self)
        self.stackedWidget.setCurrentIndex(0)

        self.studentTable.setColumnWidth(0, 30)
        self.studentTable.setColumnWidth(1, 100)
        self.studentTable.setColumnWidth(2, 250)
        self.studentTable.setColumnWidth(3, 100)
        self.studentTable.setColumnWidth(4, 100)
        self.studentTable.setColumnWidth(5, 250)
        self.studentTable.setColumnWidth(6, 100)
        self.studentTable.setColumnWidth(7, 125)
        self.studentTable.setColumnWidth(0, 125)
        # setting DataSetTable column Widths:
        self.DataSetTable.setColumnWidth(0, 220)
        self.DataSetTable.setColumnWidth(1, 220)
        self.DataSetTable.setColumnWidth(2, 240)
        self.DataSetTable.setColumnWidth(3, 220)
        self.DataSetTable.setColumnWidth(4, 220)
        # setting TrainDataTable column Widths:
        self.TrainDataTable.setColumnWidth(0, 220)
        self.TrainDataTable.setColumnWidth(1, 220)
        self.TrainDataTable.setColumnWidth(2, 240)
        self.TrainDataTable.setColumnWidth(3, 220)
        self.TrainDataTable.setColumnWidth(4, 220)
        # setting RegisterTable column widths:
        self.RegisterTable.setColumnWidth(0, 150)
        self.RegisterTable.setColumnWidth(1, 220)
        self.RegisterTable.setColumnWidth(2, 220)
        self.RegisterTable.setColumnWidth(3, 220)
        self.RegisterTable.setColumnWidth(4, 220)
        self.RegisterTable.setColumnWidth(5, 220)

        self.TrainDataTable.verticalHeader().setVisible(False)
        self.RegisterTable.verticalHeader().setVisible(False)
        self.DataSetTable.verticalHeader().setVisible(False)
        self.studentTable.verticalHeader().setVisible(False)

        self.actionNew_Student.triggered.connect(self.showStudentProfile)
        self.actionNew_Student.triggered.connect(self.showStudentDetails)
        self.actionModify_Student.triggered.connect(self.showModifyPage)
        self.actionModify_Student.triggered.connect(self.showStudentDetails)
        self.actionData_Set.triggered.connect(self.showDataSet)
        self.actionData_Set.triggered.connect(self.showDataSets)
        self.actionTrain_Data.triggered.connect(self.showTrainData)
        self.actionTrain_Data.triggered.connect(self.showTrainDatas)
        self.actionView_Records.triggered.connect(self.showAttendance)
        self.actionView_Records.triggered.connect(self.showRecords)
        self.actionHome.triggered.connect(self.showHomePage)
        self.actionDevelopers.triggered.connect(self.showDevelopers)
        self.InsertBtn.clicked.connect(self.InsertData)
        self.InsertBtn.clicked.connect(self.showStudentDetails)

        self.InsertBtn.clicked.connect(self.inputBranch.clear)
        self.InsertBtn.clicked.connect(self.inputParent.clear)
        self.InsertBtn.clicked.connect(self.inputMobile.clear)
        self.InsertBtn.clicked.connect(self.inputEmail.clear)
        self.InsertBtn.clicked.connect(self.stdname.clear)
        self.InsertBtn.clicked.connect(self.lineID.clear)
        self.captureBtn.clicked.connect(self.creatingDataSet)
        self.captureBtn.clicked.connect(self.showDataSets)
        self.captureBtn.clicked.connect(self.StdID.clear)
        self.captureBtn.clicked.connect(self.images.clear)
        self.trainBtn.clicked.connect(self.insertTrainData)
        self.trainBtn.clicked.connect(self.stdID.clear)
        self.actionTrain_Data.triggered.connect(self.showTrainDatas)
        self.attnstart.clicked.connect(self.StartAttendance)
        

    def showHomePage(self):
        self.stackedWidget.setCurrentIndex(0)

    def showStudentProfile(self):
        self.stackedWidget.setCurrentIndex(1)

    def showModifyPage(self):
        self.stackedWidget.setCurrentIndex(2)

    def showDataSet(self):
        self.stackedWidget.setCurrentIndex(3)

    def showTrainData(self):
        self.stackedWidget.setCurrentIndex(4)

    def showRecords(self):
        self.stackedWidget.setCurrentIndex(5)

    def showDevelopers(self):
        self.stackedWidget.setCurrentIndex(6)

    def showPopUp(self, msg, icon, com_msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        if com_msg:
            msgBox.setDetailedText(com_msg)
        msgBox.setIcon(icon)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def setPhoto(self, image):
        self.filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
        self.stdpic.setIcon(QIcon(self.filename))
        self.stdpic.setIconSize(core.QSize(201, 221))

    def showStudentDetails(self):
        query = f"SELECT auto_id, student_id, full_name, dob, gender, email_address, Section, phone_no, parent_no from students"
        MyCur.execute(query)
        student_details = MyCur.fetchall()
        self.studentTable.setRowCount(len(student_details))
        row = 0
        for std in student_details:
            self.studentTable.setItem(row, 0, QTableWidgetItem(str(std[0])))
            self.studentTable.setItem(row, 1, QTableWidgetItem(std[1]))
            self.studentTable.setItem(row, 2, QTableWidgetItem(std[2]))
            self.studentTable.setItem(row, 3, QTableWidgetItem(std[3]))
            self.studentTable.setItem(row, 4, QTableWidgetItem(std[4]))
            self.studentTable.setItem(row, 5, QTableWidgetItem(std[5]))
            self.studentTable.setItem(row, 6, QTableWidgetItem(std[6]))
            self.studentTable.setItem(row, 7, QTableWidgetItem(std[7]))
            self.studentTable.setItem(row, 8, QTableWidgetItem(std[8]))
            row += 1

    def showDataSets(self):
        query1 = f"SELECT * FROM datasets"
        MyCur.execute(query1)
        datasets = MyCur.fetchall()
        self.DataSetTable.setRowCount(len(datasets))
        row = 0
        for set in datasets:
            self.DataSetTable.setItem(row, 0, QTableWidgetItem(str(set[0])))
            self.DataSetTable.setItem(row, 1, QTableWidgetItem(set[1]))
            self.DataSetTable.setItem(row, 2, QTableWidgetItem(set[2]))
            self.DataSetTable.setItem(row, 3, QTableWidgetItem(set[3]))
            self.DataSetTable.setItem(row, 4, QTableWidgetItem(set[4]))
            row += 1

    def showTrainDatas(self):
        query2 = f"SELECT * FROM training"
        MyCur.execute(query2)
        trainings = MyCur.fetchall()
        self.TrainDataTable.setRowCount(len(trainings))
        row = 0
        for train in trainings:
            self.TrainDataTable.setItem(row, 0, QTableWidgetItem(str(train[0])))
            self.TrainDataTable.setItem(row, 1, QTableWidgetItem(train[1]))
            self.TrainDataTable.setItem(row, 2, QTableWidgetItem(train[2]))
            self.TrainDataTable.setItem(row, 3, QTableWidgetItem(train[3]))
            self.TrainDataTable.setItem(row, 4, QTableWidgetItem(train[3]))
            row += 1

    def showAttendance(self):
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d-%b-%Y")
        self.settime.setText(str(current_time))
        self.setdate.setText(str(current_date))
        query3 = f"SELECT auto_id, student_id, student_name,section, in_time, _date FROM attendance"
        MyCur.execute(query3)
        records = MyCur.fetchall()
        self.RegisterTable.setRowCount(len(records))
        row = 0
        for record in records:
            self.RegisterTable.setItem(row, 0, QTableWidgetItem(str(record[0])))
            self.RegisterTable.setItem(row, 1, QTableWidgetItem(record[1]))
            self.RegisterTable.setItem(row, 2, QTableWidgetItem(record[2]))
            self.RegisterTable.setItem(row, 3, QTableWidgetItem(record[3]))
            self.RegisterTable.setItem(row, 4, QTableWidgetItem(record[4]))
            self.RegisterTable.setItem(row, 5, QTableWidgetItem(record[5]))
            row += 1

    def InsertData(self):
        studentID = self.lineID.text()
        studentName = self.stdname.text()
        dob = self.inputDOB.text()
        emailid = self.inputEmail.text()
        mobileno = self.inputMobile.text()
        parentno = self.inputParent.text()
        branch = self.inputBranch.text()
        if self.male.isChecked():
            gender = self.male.text()
        if self.female.isChecked():
            gender = self.female.text()
        if studentID and studentName and dob and emailid and mobileno and parentno and branch:
            query5 = "SELECT * FROM students WHERE student_id = %s"
            try:
                MyCur.execute(query5, (studentID,))
                existed_details = MyCur.fetchall()
            except mc.Error as err:
                self.showPopUp("Database Error", QMessageBox.Warning, err)
            if not existed_details:
                query4 = "INSERT INTO students( student_id, full_name, dob, gender, Section, phone_no, parent_no, email_address, photo_path, is_dataset_available, is_model_available) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                try:
                    MyCur.execute(query4, (studentID, studentName, str(dob), gender, branch, mobileno, parentno, emailid, "No_IMAGE", "False", "False"))
                    Cont.commit()
                except mc.Error as err:
                    self.showPopUp("Database Error", QMessageBox.Warning, err)
            else:
                self.showPopUp("Student details alreay existed", QMessageBox.Information, "")
        else:
            self.showPopUp("Please fill all columns", QMessageBox.Information, "")

    def creatingDataSet(self):
        stdid = self.StdID.text()
        no_of_imgs = self.images.text()
        today_date = date.today().strftime("%d-%b-%y")
        query2 = "INSERT INTO datasets(student_id, full_name, number_of_images, created_date) VALUES (%s,%s,%s,%s)"
        query3 = f"SELECT auto_id, full_name FROM students WHERE student_id = '{stdid}'"
        query4 = "SELECT * from datasets WHERE student_id = %s"
        query5 = f"UPDATE students set is_dataset_available = 'True' WHERE student_id = '{stdid}'"
        if stdid and no_of_imgs:
            try:
                MyCur.execute(query3)
                students = MyCur.fetchall()
                print(students)
            except mc.Error as err:
                self.showPopUp("Database Error",QMessageBox.Warning, err)
            if  students:
                if createDataSet(stdid, no_of_imgs):
                    MyCur.execute(query4,(stdid,))
                    data = MyCur.fetchall()
                    if not data:
                        try:
                            MyCur.execute(query2, (stdid, students[0][1], no_of_imgs, today_date))
                            MyCur.execute(query5)
                            Cont.commit()
                        except mc.Error as err:
                            self.showPopUp("Database Error", QMessageBox.Warning, err)
                    else:
                        self.showPopUp("Data Set already Exists", QMessageBox.Information, "")
                else:
                    self.showPopUp("Data Set creation Failed", QMessageBox.Information, "")
            else:
                self.showPopUp("User doesn't exists", QMessageBox.Information, "")
        else:
            self.showPopUp("Please fill data", QMessageBox.Information, "")

    def insertTrainData(self):
        stdID = self.stdID.text()
        date_today = date.today().strftime("%d-%b-%Y")
        query2 = "SELECT full_name, number_of_images from datasets WHERE student_id = %s "
        query3 = "SELECT * FROM training WHERE student_id = %s"
        query4 = "INSERT INTO training(student_id, full_name,number_of_trained_images,trained_date) VALUES(%s,%s,%s,%s)"
        query5 = f"UPDATE students SET is_model_available = 'True' WHERE student_id = '{stdID}' "
        try:
            MyCur.execute(query2, (stdID,))
        except mc.Error as err:
            self.showPopUp("Database error while inserting", QMessageBox.Warning, err)
        datasets = MyCur.fetchall()
        if datasets:
            try:
                MyCur.execute(query3, (stdID,))
            except mc.Error as err:
                self.showPopUp("Database error while inserting", QMessageBox.Warning, err)
            existed_training = MyCur.fetchall()
            if not existed_training:
                self.trainingData()
                try:
                    MyCur.execute(query4, (stdID, datasets[0][0], datasets[0][1], str(date_today)))
                    MyCur.execute(query5)
                    Cont.commit()
                    self.showPopUp("Train Model Created Successfully", QMessageBox.Information, "")
                except mc.Error as err:
                    self.showPopUp("Database error while inserting", QMessageBox.Warning, err)
            else:
                self.showPopUp("Trained set already Existed", QMessageBox.Information, "")
        else:
            self.showPopUp("Dataset doesn't exists", QMessageBox.Information, "")
        self.showTrainDatas()
        self.trainingBar.setValue(0)

    def trainingData(self):
        student_ID = self.stdID.text()
        generateQR(student_ID)
        self.filename = f"Trained_Models\{student_ID}\{student_ID}_(QRCODE).jpg"
        self.qrcode.setObjectName("")
        self.qrcode.setIcon(QtGui.QIcon(self.filename))
        self.qrcode.setIconSize(core.QSize(201, 221))
        print("[INFO] quantifying faces...")
        imagePaths = list(paths.list_images(f"Datasets\\{student_ID}\\"))
        for (i, imagePath) in enumerate(imagePaths):
            value = trainData(i, imagePath, imagePaths)
            self.trainingBar.setValue(value)
        dumpEncodings(student_ID)



    def StartAttendance(self):
        AttendanceSystem()
        absents = getReports()
        send_mail()
        for absent in absents:
            student_name = absent[1]
            parent_no = "+91"+absent[2]
            if absent[4].lower() == 'male':
                son_or_daughter = 'son'
            else:
                son_or_daughter = 'daughter'
            parent_no = "+918184923796"
            send_msg(student_name, son_or_daughter, parent_no)
        








class LoadPage(QDialog):
    def __init__(self):
        super(LoadPage, self).__init__()
        loadUi("Application_UI//LoadApp.ui", self)
        self.startBtn.clicked.connect(self.startProgress)
        self.startBtn.clicked.connect(self.closing)

    def startProgress(self):
        for i in range(101):
            time.sleep(0.05)
            self.progressBar.setValue(i)

        LoginWindow.show()

    def closing(self):
        self.close()


class LoginPage(QDialog):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("Application_UI//Login.ui", self)
        self.LoginBtn.clicked.connect(self.checkLogin)

    def checkLogin(self):
        in_uname = self.uname.text()
        in_passwd = self.passwd.text()
        # Creating cursor for Get Data from databse users;
        query = f"Select * from users where username = %s and password = %s"
        MyCur.execute(query, (in_uname, in_passwd))
        details = MyCur.fetchall()
        if (details):
            if in_passwd == details[0][2]:
                MainWindow.showMaximized()
                MainWindow.show()
                self.closing()
        else:
            self.showmsg.setText("Invalid Username or Password")

    def closing(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Window FOr Login Window
    LoadWindow = LoadPage()
    LoadWindow.setFixedWidth(661)
    LoadWindow.setFixedHeight(380)
    LoadWindow.show()

    # Window FOr Login window
    LoginWindow = LoginPage()
    LoginWindow.setFixedWidth(379)
    LoginWindow.setFixedHeight(451)

    # Window for HomePage
    MainWindow = MainPage()
    sys.exit(app.exec_())
