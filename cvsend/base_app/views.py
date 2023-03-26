import os
import glob
from django.http import HttpResponse
from django.shortcuts import render
from base_app import forms
from django.core.files.storage import default_storage
# Imports for sending mails
import smtplib
import time
import pandas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Mail send function:
def send_mail(MY_MAIL,PASSWORD,PASSED_SUBJECT, PASSED_BODY, FILE_NAME, RESUME_NAME):
    data = pandas.read_excel(f"media/{FILE_NAME}")
    dicted_data = data.to_dict()
    MAIL_LENGTH = len(dicted_data["email"])
    print(dicted_data)
    # print(f"There were {MAIL_LENGTH} number of mail address provided")
    for n in range(0, MAIL_LENGTH):
        TO_EMAIL = dicted_data['email'][n]
        DESIGNATION = dicted_data['designation'][n]
        SUBJECT = PASSED_SUBJECT.replace("<DESIG>", DESIGNATION)
        BODY = PASSED_BODY.replace("<DESIG>", DESIGNATION)
        print("Subject : " +SUBJECT +" and body " +BODY)
        try:
            msg = MIMEMultipart()
            msg['From'] = MY_MAIL
            msg['To'] = TO_EMAIL
            msg['Subject'] = SUBJECT
            msg.attach(MIMEText(BODY, 'plain'))
            pdfname = RESUME_NAME
            # open the file in bynary
            binary_pdf = open("media/" +pdfname, 'rb')
            payload = MIMEBase('application', 'octate-stream', Name=pdfname)
            # payload = MIMEBase('application', 'pdf', Name=pdfname)
            payload.set_payload((binary_pdf).read())
            # enconding the binary into base64
            encoders.encode_base64(payload)
            # add header with pdf name
            payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
            msg.attach(payload)

            session = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            session.login(MY_MAIL, PASSWORD)
            text = msg.as_string()
            session.sendmail(MY_MAIL, TO_EMAIL, text)
            time.sleep((15))

        except:
            pass

        print(f"Mail send success To {TO_EMAIL} for the designation of {DESIGNATION}")



def index(request):
    # below we have mentioned the variable form which will be used to display form
    form= forms.mail_datas
    if request.method =="POST":
        # Bleow used to get datas if the user post datas
        form = forms.mail_datas(request.POST, request.FILES)

        if form.is_valid():
            # create the folder if it doesn't exist.
            try:
                os.mkdir(os.path.join(settings.MEDIA_ROOT, folder))
            except:
                pass
            file = request.FILES['user_file']
            file_name = default_storage.save(file.name, file)
            file = request.FILES['resume_file']
            resume_name = default_storage.save(file.name, file)
            send_mail(MY_MAIL=form.cleaned_data['email'],
                      PASSWORD= form.cleaned_data['token'],
                      PASSED_SUBJECT = form.cleaned_data['subject'],
                      PASSED_BODY=form.cleaned_data["message"],
                      FILE_NAME=file_name,
                      RESUME_NAME=resume_name)
            try:
                files = glob.glob(os.path.join('media/*'))
                for f in files:
                    os.remove(f)

            except:
                pass

        else:
            print("skipped if condition")
    return render(request, "index.html", {"form":form})
