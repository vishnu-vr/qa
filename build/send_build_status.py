import requests
import json
import sys
from common import send_status

if __name__ == "__main__":
    with open('../settings.json') as f:
        settings = json.load(f)
    jobuuid = sys.argv[1]
    status = sys.argv[2]

    send_status(jobuuid, status, settings);