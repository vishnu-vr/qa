import requests
import json

def send_status(jobuuid, status, settings):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	SecretKey = settings["TRIGGER_BUILD_API_SECRET_KEY"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob/" + jobuuid #/jobuuid
	print(end_point)
	myobj = {
	    "Status": status
	}

	x = requests.put(end_point, data = json.dumps(myobj), headers = build_header(settings), verify=False)
	print(x)

def send_overall_status(data, settings):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob"
	print(end_point)

	x = requests.put(end_point, data = json.dumps(data), headers = build_header(settings), verify=False)
	print(x)

def build_header(settings):
	headers = {
	    "Content-Type": "application/json",
	    "Authorization": "Token " + settings["TRIGGER_BUILD_API_SECRET_KEY"]
	}

	return headers