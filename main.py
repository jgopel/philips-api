#!/usr/bin/python3

import json
import logging
import requests
import time
import urllib

API_SERVER = "http://localhost:8080"
LIGHTS_API = urllib.parse.urljoin(API_SERVER, "api/newdeveloper/lights/")

logging.basicConfig(level=logging.DEBUG)

def main():
	# Build current state
	current_state = get_current_state()
	print(prettify_json(current_state))

	# Monitor for changes
	while True:
		# Get updated state
		new_state = get_current_state()

		# Find new states
		for current_light, new_light in zip(current_state, new_state):
			# Ensure sanity of data
			non_shared_keys = current_light.keys() ^ new_light.keys()
			assert(len(non_shared_keys) == 0)
			assert(current_light["id"] == new_light["id"])

			for key in current_light.keys():
				# ID will always be identical, but it's probably faster to check it
				# than skip it. Not benchmarked.

				if current_light[key] != new_light[key]:
					change = {}
					change["id"] = current_light["id"]
					change[key] = new_light[key]
					print(prettify_json(change))

		current_state = new_state

		# Poll a bit more slowly - there's no need to hammer the API host
		time.sleep(1)


def get_current_state():
	"""Get state of all lights

	Could potentially be optimized if number of lights will not change (or will
	not change frequently) by caching the variable light_list.

	This could be parallelized. Investigation is required to determine whether or
	not that parallelization would result in performance gains. I suspect the
	main factor there would be number of lights in the average system.
	"""

	light_list = sorted(get_lights())
	logging.debug("light_list: " + prettify_json(light_list))
	state = []
	for light_num in light_list:
		light_state = get_light_state(light_num)
		logging.debug("light_state: " + prettify_json(light_state))
		state.append(light_state)

	return state

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
