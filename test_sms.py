from twilio.rest import Client

def send_msg(student_name, son_or_daughter, parent_no):
    SID = "AC85a7b3c089982132e92f5aa3f0952661"
    Auth_Token = ""

    to_number = parent_no
    from_number = "572c631a720a1a33a066df60b9de5652"



    msg_content = f"Good Morning! We are from IIIT Ongole. \n Your {son_or_daughter} {student_name} is absent today."

    c1 = Client(SID, Auth_Token)

    c1.messages.create(body=msg_content, from_=from_number, to=to_number)



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
