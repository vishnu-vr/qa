import boto3
from botocore.exceptions import ClientError
import json
import sys
import smtplib, ssl
import os
from os import path
import glob
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common import send_status
from email.message import EmailMessage

settings = None

def send_email(receiver_email, message, failed=False):
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

def get_file_path(platform):
	if (platform == "ios"):
		base_loc = settings["IOS_PATH"]
		full_loc = glob.glob(path.join(base_loc,"*.ipa"))#base_loc + '\\' + "*.ipa";
	else:
		base_loc = settings["ANDROID_PATH"]
		full_loc = glob.glob(path.join(base_loc,"*.apk"))#base_loc + '\\' + "*.apk"

	return full_loc

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    filename = sys.argv[1]
    platform = sys.argv[2]
    email = sys.argv[3]

    if platform not in ["ios","android"]:
    	print("invalid platform")
    	sys.exit()

    paths = get_file_path(platform)
    if len(paths) == 0:
        print("path does not exists")
        send_status(filename, "Failed", settings);
        send_email(email, "Build Failed", failed=True)
        sys.exit()

    filepath = paths[0]
    print(filepath)
    if (not path.exists(filepath)):
        print("file does not exists")
        send_status(filename, "Failed", settings);
        send_email(email, "Build Failed", failed=True)
        sys.exit()

    filename_with_ext = filename + (".ipa" if platform == "ios" else ".apk")
    upload_file(filepath, filename_with_ext)
    os.remove(filepath)

    link = settings["TRIGGER_BUILD_URL"]+"/GenerateLink/"+filename_with_ext
    send_email(email, link)
    send_status(filename, "Finished", settings);
