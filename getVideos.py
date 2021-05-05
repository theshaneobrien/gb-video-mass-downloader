import requests
import json
import urllib
import os
import datetime
import time

#This should be stored in envars... but eh
apiKey =""
videosURL = "https://www.giantbomb.com/api/videos/?api_key="

limit = "&limit="
limitAmount = 1

offset = "&offset="
offsetAmount = 0

maxOffset = 15000

bufferSize = 1024000

sortPattern = "&sort=publish_date:asc"
filters = "&filter=premium:true"
startRuntime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def startVideoArchival():
	#Open progress file, read the latest offset we need to pull from
	print ("starting...")
	with open("archivalProgress.json", "r") as archivalProgress:
		data = json.load(archivalProgress)
		global offsetAmount
		global maxOffset
		offsetAmount = data["currentOffset"]
		maxOffset = data["maxOffset"]
		startRuntime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	#Download the video
	getVideoDetails()

def getVideoDetails():
	downloadURL = "0"
	combinedURL = videosURL + apiKey + "&format=json" + limit + str(limitAmount) + offset + str(offsetAmount) + filters + sortPattern

	response = requests.get(combinedURL,
		headers={"User-Agent": "VideoCatelogger"}
	)

	if response.status_code == 200:
		responseJson = response.json()
		global maxOffset
		maxOffset = responseJson["number_of_total_results"]
		print("Getting Videos from:")
		print(combinedURL)

		print("Video Name:")

		print(responseJson["results"][0]["name"])

		#We are only interested in the highest quality video, so check what the best URL is and proceed
		if responseJson["results"][0]["hd_url"]:
			print(responseJson["results"][0]["hd_url"])
			downloadURL = responseJson["results"][0]["hd_url"]
		elif responseJson["results"][0]["high_url"]:
			print(responseJson["results"][0]["high_url"])
			downloadURL = responseJson["results"][0]["high_url"]
		elif responseJson["results"][0]["low_url"]:
			print(responseJson["results"][0]["low_url"])
			downloadURL = responseJson["results"][0]["low_url"]
		else:
			print("noURL")
			downloadURL = "noURL"

		if downloadURL != "noURL":
			print("Downloading Video")
			#Sleep to not exceed API Request Limit
			time.sleep(2)
			#Stream files and save as chucks so we don't eat up all the memory
			with requests.get(downloadURL + "?api_key=" + apiKey, stream=True) as video:
				video.raise_for_status()
				if video.headers.get("content-type") == "video/mp4":
					print("Writing Video to Disk")
					with open(os.getcwd() + "/success/" + responseJson["results"][0]["url"], "wb") as videoFile:	
						for chunk in video.iter_content(chunk_size=bufferSize):
							videoFile.write(chunk)
							#Progress bar would be cool as hell
					#Write the GUID to a file in the Success / Failed Folder
					with open(os.getcwd() + "/success/" + responseJson["results"][0]["guid"]+ ".json", "w") as jsonFile:
						json.dump(responseJson, jsonFile)
					print("Download Successful")
					saveArchivingProgress(True)

				else:
					print("not a video")
					#Write the GUID to a file in the Success / Failed Folder
					with open(os.getcwd() + "/failed/notVideo" + responseJson["results"][0]["guid"]+ ".json", "w") as jsonFile:
						json.dump(responseJson, jsonFile)
					saveArchivingProgress(False)
		else:
			print("noURL")
			#Write the GUID to a file in the Success / Failed Folder
			with open(os.getcwd() + "/failed/noURL" + responseJson["results"][0]["guid"]+ ".json", "w") as jsonFile:
				json.dump(responseJson, jsonFile)
			saveArchivingProgress(False)
	else:
		print("API Error: " + str(response.status_code))
		saveArchivingProgress(False)

def saveArchivingProgress(succeeded):
	if succeeded == True:
		#Increment our offset, save the progress file, start again
		global offsetAmount
		global maxOffset
		progress = {
			"lastOffset" : offsetAmount,
			"currentOffset" : offsetAmount + 1,
			"maxOffset" : maxOffset,
			"lastRuntime" : startRuntime,
			"lastCompleteTime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		}
		print(json.dumps(progress))
		print("Saving Progress Successful")
		print("Video " + str(offsetAmount) + " of " + str(maxOffset))
		with open("archivalProgress.json", "w") as archivalProgress:
			json.dump(progress, archivalProgress)

		#Sleep to not exceed API Request Limit
		time.sleep(2)
	elif succeeded == False:
		#Wait until the next hour and try again?
		print("failed")
		time.sleep(3600)

while offsetAmount < maxOffset:
	startVideoArchival()