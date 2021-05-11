import boto3
from botocore.exceptions import ClientError
import json
import sys
import smtplib, ssl
import os
from os import path
import glob

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
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

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

def build_status(status):
	print(status)
	sys.exit()

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
    	build_status("Failed")

    filepath = paths[0]
    print(filepath)
    if (not path.exists(filepath)):
    	build_status("Failed")

    upload_file(filepath, filename)
    os.remove(filepath)

    link = "https://"+settings["BUCKET_NAME"]+".s3."+settings["AWS_REGION_NAME"]+".amazonaws.com/"+filename
    send_email(email, link)
    build_status("Finished")
