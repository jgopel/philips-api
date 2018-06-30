#!/usr/bin/python3

import json
import logging
import requests
import urllib

API_SERVER = "http://localhost:8080"
LIGHTS_API = urllib.parse.urljoin(API_SERVER, "api/newdeveloper/lights/")

logging.basicConfig(level=logging.DEBUG)

def main():
	# Build current state
	light_list = sorted(get_lights())
	logging.debug("light_list: " + prettify_json(light_list))
	current_state = []
	for light_num in light_list:
		light_state = get_light_state(light_num)
		logging.debug("light_state: " + prettify_json(light_state))
		current_state.append(light_state)

	# Print current state
	print(prettify_json(current_state))

	# TODO: Monitor for changes

def get_lights():
	"""Get all lights the server knows about

	Can throw an exception if the API URL is wrong. This seems like a reasonable
	failure mode.
	"""

	return requests.get(LIGHTS_API).json()

def get_light_state(light_num):
	"""Get the tracked states for a specific light

	Can throw an excpetion if the light number provided does not exist. Since
	this is not expected to be used on its own, it makes no effort to handle that
	excpetion. It would be trivial to write a safer version of this for any
	number of desired failure modes.
	"""

	# Data sanity
	light_num = str(light_num)

	# Do HTTP request
	api_url = urllib.parse.urljoin(LIGHTS_API, light_num)
	response = requests.get(api_url).json()

	# Pull out relevant pieces for output
	output = {}
	output["name"] = response["name"]
	output["id"] = light_num
	output["on"] = response["state"]["on"]
	output["brightness"] = response["state"]["bri"]
	return output

def prettify_json(json_string):
	"""Takes JSON and makes it pretty

	Will also take anything that can be converted to JSON. Thanks Python!
	"""

	return json.dumps(json_string, indent=4, sort_keys=True)

if __name__ == "__main__":
	main()
