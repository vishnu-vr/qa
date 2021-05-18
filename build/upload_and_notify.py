import boto3
from botocore.exceptions import ClientError
import json
import sys
import smtplib, ssl
import os
from os import path
import glob
from common import send_status

settings = None

def send_email(receiver_email, link):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = settings["EMAIL"]
    password = settings["EMAIL_PASSWORD"]
    message = """\
    Subject: The build you requested is ready.

    {}
    """.format(link)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

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
        send_status(filename, "Failed", settings);
        sys.exit()

    filepath = paths[0]
    print(filepath)
    if (not path.exists(filepath)):
    	send_status(filename, "Failed", settings);
        sys.exit()

    filename_with_ext = filename + (".ipa" if platform == "ios" else ".apk")
    upload_file(filepath, filename_with_ext)
    os.remove(filepath)

    link = "https://"+settings["TRIGGER_BUILD_URL"]+"/GenerateLink/"+filename
    send_email(email, link)
    send_status(filename, "Finished", settings);
