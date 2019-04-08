import requests
import json
import time
import os
import boto3
import botocore


def getTokenData(bucket, tokenFile):
	s3 = boto3.resource('s3')
	obj = s3.Object(bucket, tokenFile)
	return json.loads(obj.get()['Body'].read().decode('utf-8'))

def getAuthData(authFile):
	authFile = os.path.join(os.path.dirname(__file__), authFile)
	f = open(authFile, "r")
	return json.loads(f.read())

def accessToken(bucket, tokenFile):
	data = getTokenData(bucket, tokenFile)
	return data["access_token"]

def refreshToken(bucket, tokenFile):
	data = getTokenData(bucket, tokenFile)
	return data["refresh_token"]

def updateTokenData(bucket, pollData, tokenFile):
	s3 = boto3.resource('s3')
	s3.Object(bucket, tokenFile).put(Body=json.dumps(pollData))


def refreshAccessTokenToAuthServer(bucket, tokenFile, authFile):
	URL = "https://www.googleapis.com/oauth2/v4/token"
	tokenData = getTokenData(bucket, tokenFile)
	authData = getAuthData(authFile)

	GRANT_TYPE = "refresh_token"

	params = {"refresh_token": tokenData["refresh_token"], "client_id": authData["client_id"],
				"client_secret": authData["client_secret"], "grant_type": GRANT_TYPE}
	response = requests.post(url=URL, data=params)
	data = json.loads(response.text)
	tokenData = getTokenData(bucket, tokenFile)
	tokenData["access_token"] = data["access_token"]
	tokenData["expires_in"] = data["expires_in"]
	updateTokenData(bucket, tokenData, tokenFile)


def requestToAuthServer(authFile):
	"""
	:param auth: dictionary
	:rtype: dictionary
	"""
	auth = getAuthData(authFile)

	URL = "https://accounts.google.com/o/oauth2/device/code"
	CLIENT_ID = auth["client_id"]
	SCOPE = "https://www.googleapis.com/auth/calendar.readonly"

	params = {"client_id": auth["client_id"], "scope": SCOPE}

	response = requests.post(url=URL, data=params)
	return json.loads(response.text)


def pollToAuthServer(bucket, authFile, tokenFile, data):
	"""
	:param auth: dictionary
	:param token: dictionary
	:rtype: dictionary
	"""
	auth = getAuthData(authFile)

	POLL_URL = "https://www.googleapis.com/oauth2/v4/token"
	GRANT_TYPE = "http://oauth.net/grant_type/device/1.0"

	params = {"client_id": auth["client_id"], "client_secret": auth["client_secret"], 
			"code": data["device_code"], "grant_type": GRANT_TYPE}

	while (True):
		time.sleep(data['interval'])
		response = requests.post(url=POLL_URL, data=params)
		pollData = json.loads(response.text)
		try:
			accessToken = pollData["access_token"]
		except KeyError:
			continue
		else:
			break
	updateTokenData(bucket, pollData, tokenFile)
	return pollData


if __name__ == '__main__':
	TOKENFILE = "token.json"
	AUTHFILE = "authentication.json"
	BUCKET = "deckle-data"

	# body = requestToAuthServer(AUTHFILE)
	# print(body)
	# pollData = pollToAuthServer(AUTHFILE, body)
	# print(pollData)
	refreshAccessTokenToAuthServer(BUCKET, TOKENFILE, AUTHFILE)






