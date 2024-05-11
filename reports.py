from mysql.connector import connect
import smtplib
import random
from datetime import datetime, date
import numpy as np
import pandas as pd
from email.message import EmailMessage
from twilio.rest import Client
from glob import glob

Cont = connect(host="localhost", user="root", password="", database="management_auto_attendance_system")
MyCur = Cont.cursor()

absentList = ()

current_date = date.today().strftime("%d-%b-%Y")

def getReports():
# Query for fetch present students from database:
    query1 = "SELECT DISTINCT section FROM attendance"
    MyCur.execute(query1)
    sections = MyCur.fetchall()
    print(sections)

    for section in sections:
        query2 = "SELECT student_id, student_name, in_time FROM attendance WHERE _date = %s and section = %s"
        MyCur.execute(query2,(current_date,section[0]))
        presentsList = MyCur.fetchall()
        
        data = pd.DataFrame(presentsList,columns=["Student ID","Student Name","Time"])
        data.to_csv(f"AttendanceReports\{section[0]}_{current_date}.csv")
        

        



    # Query for absent students from database:
    sub_query = f"SELECT student_id FROM attendance WHERE _date = %s"
    query3 = f"SELECT student_id, full_name, parent_no, section,gender FROM students WHERE is_model_available = 'True' and student_id not in ({sub_query})"
    MyCur.execute(query3,(current_date,))
    absentList = MyCur.fetchall()
    return absentList





def send_mail():
    sender_address = "o180428@rguktong.ac.in"
    password = "tmxddfmbsuaoacai"
    current_date = date.today().strftime("%d-%b-%Y")
    section = "CSE-3"

    msg = EmailMessage()
    msg['Subject'] = f"Attendance of {section} Students"
    msg['From'] = "VISPR Technologies"
    msg['To'] = "dolajhansi007@gmail.com"

    with open("MailBodyConten.txt") as mybody:
        data = mybody.read()
        msg.set_content(data)
    for file in glob(f"AttendanceReports\\*{current_date}.csv"):
        with open(file, "rb") as reader:
            file_data = reader.read()
            file_name = reader.name
            msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_address, password)
        server.send_message(msg)

def send_msg(student_name, son_or_daughter, parent_no):
    SID = ""
    Auth_Token = ""

    to_number = parent_no
    from_number = ""



    msg_content = f"Good Morning! We are from IIIT Ongole. \n Your {son_or_daughter} {student_name} is absent today."

    c1 = Client(SID, Auth_Token)

    c1.messages.create(body=msg_content, from_=from_number, to=to_number)

def verifyNumber(parent_no,student_name):
    SID = "AC59ac2ed1ce7c876729dbee6108d40daf"
    Auth_Token = "69b844b7bfab05c96cbfbeb935ed9d97"

    client = Client(SID,Auth_Token)
    verify = client.verify.services("Verification")
    verify.verifications.create(to=parent_no,channel="sms")
    n = int(input("Enter Otp:"))
    result = verify.verification_checks.create(to=parent_no, code=n)
    print(result.status)



    
    
