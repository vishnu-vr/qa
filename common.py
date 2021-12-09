import requests
import json
import smtplib, ssl
from email.message import EmailMessage

def send_status(jobuuid, status, settings, teamCityID=None):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	SecretKey = settings["TRIGGER_BUILD_API_SECRET_KEY"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob/" + jobuuid #/jobuuid
	print(end_point)
	myobj = {
	    "Status": status,
	    "TeamCityID": teamCityID
	}
	print(myobj)

	try:
		x = requests.put(end_point, data = json.dumps(myobj), headers = build_header(settings), verify=False)
		print(x.status_code, x.json())
	except Exception as e:
		print("Was not able to send status")

def send_overall_status(data, settings):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob"
	print(end_point)
	print(data)

	try:
		x = requests.put(end_point, data = json.dumps(data), headers = build_header(settings), verify=False)
		print(x)
	except Exception as e:
		print("Was not able to send status")

def build_header(settings):
	headers = {
	    "Content-Type": "application/json",
	    "Authorization": "Token " + settings["TRIGGER_BUILD_API_SECRET_KEY"]
	}

	return headers

def send_email(receiver_email, message, settings, failed=False):
    port = 465  # For SSL
    smtp_server = settings["SMTP_SERVER"]
    sender_email = settings["EMAIL"]
    password = settings["SMTP_PASSWORD"]

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = ("Build Failed" if failed else "Build Succeeded")
    msg['From'] = sender_email
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login("apikey", password)
        server.send_message(msg)

def upload_file(file_name, object_name=None):

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3', region_name = settings["AWS_REGION_NAME"],
                                     aws_access_key_id = settings["AWS_ACCESS_KEY"],
                                     aws_secret_access_key = settings["AWS_SECRET_KEY"])
    try:
        response = s3_client.upload_file(file_name, settings["BUCKET_NAME"], object_name, ExtraArgs={'ACL':'public-read'})
    except ClientError as e:
        print(e)
    return True