import boto3
from botocore.exceptions import ClientError
import json
import sys
import smtplib, ssl

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

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    file = sys.argv[1]
    email = sys.argv[2]

    upload_file(file)

    filename = file.split("/")[-1]
    link = "https://"+settings["BUCKET_NAME"]+".s3."+settings["AWS_REGION_NAME"]+".amazonaws.com/"+filename
    send_email(email, link)
