import requests
import json

def send_status(jobuuid, status, settings):
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
	x = requests.put(end_point, data = json.dumps(myobj), headers = headers, verify=False)
	print(x)