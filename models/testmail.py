from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#import datetime

def Trigger(candidate_email, candidate_name): #availability_datetime):
    try:
        smtp_server = 'mail.devpozent.com'
        smtp_port = 465
        sender_email = 'no-reply@devpozent.com'
        sender_password = 'Pozent@123'
        subject = 'Interview Availability'

        # personalized_email = f"Dear {candidate_name},\n\nWe would like to invite you for an interview. Are you available on {availability_datetime}.\n\nBest regards,\nPozent Corp"
        personalized_email = f"Dear {candidate_name},\n\nWe would like to invite you for an interview." # Are you available on {availability_datetime}.\n\nBest regards,\nPozent Corp"
# 

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = candidate_email
        msg['Subject'] = subject
        msg.attach(MIMEText(personalized_email, 'plain'))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, candidate_email, msg.as_string())
            
            return 'Email Sent'
    
    except Exception as e:
        error = {'message': 'Error:' + str(e)}
        return error
