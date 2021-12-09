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
from common import send_status, send_email
from email.message import EmailMessage

settings = None

def get_file_path(platform, platformBuildAction):
	if (platform == "ios"):
		base_loc = settings["IOS_PATH"]
		full_loc = glob.glob(path.join(base_loc,"*.ipa"))#base_loc + '\\' + "*.ipa";
	else:
		base_loc = settings["ANDROID_PATH"]
		full_loc = glob.glob(path.join(base_loc, platformBuildAction, "*.apk"))#base_loc + '\\' + "*.apk"

	return full_loc

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    uuid = sys.argv[1]
    platform = sys.argv[2]
    email = sys.argv[3]
    platformBuildAction = sys.argv[4]
    arguementsUsed = sys.argv[5]

    if platform not in ["ios","android"]:
        raise Exception("invalid platform")
        sys.exit()

    paths = get_file_path(platform, platformBuildAction)
    if len(paths) == 0:
        send_status(uuid, "FAILURE", settings);
        send_email(receiver_email=email, message="Build Failed", settings=settings, failed=True)
        raise Exception("path does not exists")
        sys.exit()

    filepath = paths[0]
    print(filepath)
    if (not path.exists(filepath)):
        print("file does not exists")
        send_status(uuid, "FAILURE", settings);
        send_email(receiver_email=email, message="Build Failed", settings=settings, failed=True)
        raise Exception("file does not exists")
        sys.exit()

    filename_with_ext = uuid + (".ipa" if platform == "ios" else ".apk")
    upload_file(filepath, filename_with_ext)
    os.remove(filepath)

    link = settings["TRIGGER_BUILD_URL"]+"/GenerateLink/"+filename_with_ext
    send_email(receiver_email=email, message="{arguementsUsed} \n\n {link}".format(arguementsUsed=arguementsUsed, link=link), settings=settings)
    send_status(uuid, "SUCCESS", settings);
