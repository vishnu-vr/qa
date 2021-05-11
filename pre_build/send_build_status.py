import requests
import json
import sys

settings = None

def send_status(jobuuid, status):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	SecretKey = settings["TRIGGER_BUILD_API_SECRET_KEY"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob/" + jobuuid #/jobuuid
	print(end_point)
	myobj = {
	    "SecretKey": SecretKey,
	    "Status": status
	}
	headers = {
	    "Content-Type": "application/json"
	}
	x = requests.put(trigger_build_url, data = json.dumps(myobj), headers = headers, verify=False)
	print(x.text)

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    jobuuid = sys.argv[1]
    status = sys.argv[2]

    send_status(jobuuid, status);