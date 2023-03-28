import os
import glob
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from base_app import forms
from django.core.files.storage import default_storage
from django.core import validators
# Imports for sending mails
import smtplib
import time
# from datetime import datetime
# import sys
import pandas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Mail send function:
# def send_mail(MY_MAIL,PASSWORD,PASSED_SUBJECT, PASSED_BODY, FILE_NAME, RESUME_NAME):

def index(request):
    # to get output file,
    # sys.stdout = open(f'applied_jobs/applied jobs {datetime.now()}.txt', 'wt')

    # below we have mentioned the variable form which will be used to display form
    form= forms.mail_datas
    if request.method =="POST":
        # Below used to get datas if the user post datas
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
            # send_mail(MY_MAIL=form.cleaned_data['email'],
            #           PASSWORD= form.cleaned_data['token'],
            #           PASSED_SUBJECT = form.cleaned_data['subject'],
            #           PASSED_BODY=form.cleaned_data["message"],
            #           FILE_NAME=file_name,
            #           RESUME_NAME=resume_name)
            data = pandas.read_excel(f"media/{file_name}")
            dicted_data = data.to_dict()
            MAIL_LENGTH = len(dicted_data["email"])
            print(f"Have fed with {MAIL_LENGTH} mail addresses")
            for n in range(0, MAIL_LENGTH):
                TO_EMAIL = dicted_data['email'][n]
                DESIGNATION = dicted_data['designation'][n]
                SUBJECT = form.cleaned_data['subject'].replace("<DESIG>", DESIGNATION)
                BODY = form.cleaned_data["message"].replace("<DESIG>", DESIGNATION)
                msg = MIMEMultipart()
                MY_MAIL = form.cleaned_data['email']
                PASSWORD = form.cleaned_data['token']
                msg['From'] = MY_MAIL
                msg['To'] = TO_EMAIL
                msg['Subject'] = SUBJECT
                msg.attach(MIMEText(BODY, 'plain'))
                pdfname = resume_name
                # open the file in bynary
                binary_pdf = open("media/" + pdfname, 'rb')
                payload = MIMEBase('application', 'octate-stream', Name=pdfname)
                # payload = MIMEBase('application', 'pdf', Name=pdfname)
                payload.set_payload((binary_pdf).read())
                # enconding the binary into base64
                encoders.encode_base64(payload)
                # add header with pdf name
                payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
                try:
                    msg.attach(payload)
                except:
                    return JsonResponse(
                        {'message': 'Login Error', 'explanation': 'Failed to attach resume with mail, refresh page and try again.'},status='400')
                session = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                try:
                    session.login(MY_MAIL, PASSWORD)
                except:
                    return JsonResponse({'message': 'Login Error', 'explanation': 'Kindly verify provided email id and token.'}, status='400')
                text = msg.as_string()

                session.sendmail(MY_MAIL, TO_EMAIL, text)
                time.sleep((15))

                print(f"Mail send success To {TO_EMAIL} applying for {DESIGNATION}.")
            try:
                files = glob.glob(os.path.join('media/*'))
                for f in files:
                    os.remove(f)
                    err_data=""
            except:
                err_data = {'error_msg_file_clean':'We found an error while vanishing datas. Try to do successful batch mail again to do clean. If not contact Admin'}

        # return for successful form submit
        return render(request, "result.html", {"err_data":err_data,
                                               "total_mail_send":MAIL_LENGTH})

    # else:
    #     return JsonResponse({'message': 'Feeded Invalid Datas,', 'explanation': 'Kindly check the details provided'}, status='400')
    return render(request, "index.html", {"form":form})

# By this page we get to know how to use this web
def docs(request):
    return render(request, "documentation.html")

