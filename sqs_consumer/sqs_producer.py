import os
import uuid
import boto3
import json 

settings = None

# dlq = sqs.get_queue_by_name(QueueName=os.environ["SQS_DEAD_LETTER_QUEUE_NAME"])

def make_queue():
    sqs = boto3.resource('sqs', region_name=settings['AWS_REGION_NAME'],
                                       aws_access_key_id=settings['AWS_ACCESS_KEY'],
                                       aws_secret_access_key=settings['AWS_SECRET_KEY'])
    return sqs.get_queue_by_name(QueueName=settings['AWS_SQS_QUEUE_NAME'])

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    while True:
        message = input("message :")
        email = input("email :")
        json_object = json.dumps({"message":message,"random":str(uuid.uuid4()),"email":email}, indent = 2) 
        # MessageDeduplicationId = input("MessageDeduplicationId : ")
        messagegroupid = input("messageGroupid : ")
        queue = make_queue()
        response = queue.send_message(
        MessageBody=json_object,
        # MessageDeduplicationId=messageid,
        MessageGroupId=messagegroupid)
        print(response)
