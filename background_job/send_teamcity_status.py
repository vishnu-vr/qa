import requests
import json
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from common import send_overall_status

settings=None

def get_overall_status():
	headers = {
	    "Authorization": "Bearer " + settings['AUTHORIZATION'],
	    "Accept": "application/json"
	}
	url = settings["TEAMCITY_URL"] + "/builds/?locator=state:finished,start:0,count:50,buildType:Test_BuildApk"
	response = requests.get(url, headers=headers)
	return response.json()


def get_individual_status(job_number):
	headers = {
	    "Authorization": "Bearer " + settings['AUTHORIZATION'],
	    "Accept": "application/json"
	}
	url = settings["TEAMCITY_URL"] + "/builds/id:" + str(job_number)
	response = requests.get(url, headers=headers)
	return response.json()


def get_and_send_overall_status():
	teamcity_status = get_overall_status()

	build_status_list=[]
	for build in teamcity_status["build"]:
		build_status_list.append(get_individual_status(build["id"]))

	data = {
		"BuildStatus" : build_status_list
	}
	send_overall_status(data);

if __name__ == "__main__":
	with open('../settings.json') as f:
	    settings = json.load(f)

	while True:
		get_and_send_overall_status()
		# send every 5 minutes
		time.sleep(60*5)

