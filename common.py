import requests
import json

def send_status(jobuuid, status, settings, teamCityID=None):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	SecretKey = settings["TRIGGER_BUILD_API_SECRET_KEY"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob/" + jobuuid #/jobuuid
	print(end_point)
	myobj = {
	    "Status": status,
	    "TeamCityID": teamCityID
	}
	print(myobj)

	try:
		x = requests.put(end_point, data = json.dumps(myobj), headers = build_header(settings), verify=False)
		print(x.status_code, x.json())
	except Exception as e:
		print("Was not able to send status")

def send_overall_status(data, settings):
	trigger_build_url = settings["TRIGGER_BUILD_URL"]
	end_point = trigger_build_url + "/api/jobStatus/updateJob"
	print(end_point)
	print(data)

	try:
		x = requests.put(end_point, data = json.dumps(data), headers = build_header(settings), verify=False)
		print(x)
	except Exception as e:
		print("Was not able to send status")

def build_header(settings):
	headers = {
	    "Content-Type": "application/json",
	    "Authorization": "Token " + settings["TRIGGER_BUILD_API_SECRET_KEY"]
	}

	return headers