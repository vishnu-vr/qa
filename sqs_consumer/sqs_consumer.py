import os
import requests
import boto3
from sqs_common import SignalHandler, send_queue_metrics
import json
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common import send_status, send_email
from send_teamcity_status import get_and_send_overall_status
import subprocess

# dlq = sqs.get_queue_by_name(QueueName=os.environ["SQS_DEAD_LETTER_QUEUE_NAME"])

settings = None

def trigger_internal_job(custom_arguements, uuid, email, branch, platform, platformBuildAction, instanceName):
    TEAMCITY_URL = settings['TEAMCITY_URL'] + "/buildQueue"
    headers = {
        "Authorization": "Bearer " + settings['AUTHORIZATION'],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    myobj = {
        "buildType": {
            "id": settings['BUILDTYPE_ID']
        },
        "properties": {
            "property": [
                {
                    "name": "custom_arguements",
                    "value": custom_arguements
                },
                {
                    "name": "build_uuid",
                    "value": uuid
                },
                {
                    "name": "email",
                    "value": email
                },
                {
                    "name": "branch",
                    "value": branch
                },
                {
                    "name": "platform",
                    "value": platform
                },
                {
                    "name": "platform_build_action",
                    "value": platformBuildAction
                },
                {
                    "name": "instance_name",
                    "value": instanceName
                }
            ]
        }
    }

    # return True
    try:
        x = requests.post(TEAMCITY_URL, data = json.dumps(myobj), headers = headers)
        print(x.status_code)

        if x.status_code == 200:
            response = x.json()
            responseId = str(response["id"])
            print("Queued, Build ID: + " + responseId)
            send_status(uuid, "Queued - TC", settings, responseId);
            return True
    except Exception as e:
        print("Error while triggering teamcity job")
        print(e)


    send_status(uuid, "FAILURE", settings);
    send_email(receiver_email=email, message="Build Failed", settings=settings, failed=True)
    
    return False


def consumer(queue):
    signal_handler = SignalHandler()
    while not signal_handler.received_signal:
        # send_queue_metrics(queue)
        # send_queue_metrics(dlq)
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1)
        # print("retreived messages")
        for message in messages:
            try:
                print(message.body)
                payload = json.loads(message.body)
                if (payload["type"] == "retrieve_status"):
                    get_and_send_overall_status(payload, settings)
                else:
                    trigger_internal_job(payload["message"],payload["random"],payload["email"],payload["branch"],payload["platform"],payload["platformBuildAction"],payload["instanceName"])
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                # continue

            # remove the payload from sqs
            message.delete()

def start_teamcity():
    TEAMCITY_LOC = settings['TEAMCITY_SERVER_LOC']
    cwd = os.getcwd()
    os. chdir(TEAMCITY_LOC)
    process = subprocess.Popen(['./bin/runAll.sh', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stderr, stdout, sep="\n===\n")

    os. chdir(cwd)

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    AWS_ACCESS_KEY = settings['AWS_ACCESS_KEY']
    AWS_SECRET_KEY = settings['AWS_SECRET_KEY']
    AWS_SQS_QUEUE_NAME = settings['AWS_SQS_QUEUE_NAME']
    AWS_REGION_NAME = settings['AWS_REGION_NAME']

    sqs = boto3.resource('sqs', region_name = AWS_REGION_NAME,
                                aws_access_key_id = AWS_ACCESS_KEY,
                                aws_secret_access_key = AWS_SECRET_KEY)

    start_teamcity()
    
    queue = sqs.get_queue_by_name(QueueName = AWS_SQS_QUEUE_NAME)
    consumer(queue)
