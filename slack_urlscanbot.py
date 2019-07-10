#!/usr/bin/python3
import sys
import os
import requests
import json
import re
from datetime import timedelta
from dateutil.parser import parse
import datetime
import time
import urllib
from slacker import Slacker
from random import randint
from PIL import Image
from defang import defang
import keys

####Requirements####
# runningtotal.txt in the same directory as the script
# searches.txt in the same directory as the script with the URLScan searches you'd like to perform in the following format:
	#[name_of_search], [urlscan_search_url_encoded]
	#[name_of_search], [urlscan_search_url_encoded]
#Example: 
	#lucy_server, page.server%3A"Lucy"
# keys.py with your Slack Slacker ID, working directory path, and slack channel name
	# See sample keys file
#pip install slacker
#pip install defang
#pip install requests

# Configuration
slack = Slacker(keys.slack_id)
date=datetime.datetime.now()
runningtotal_file = "runningtotal.txt"
searches = "searches.txt"

try:
	searches = open(keys.working_path+searches, 'r')
	searches_read = searches.read()
	searches_list = list(searches_read.split('\n'))
	searches.close()

	startdate = datetime.datetime.today() - timedelta(days=3)

	urlscan_results = []
	
	for term in searches_list:
		if(term):
			category = term.split(', ')[0]
			search = term.split(', ')[1]
			response = requests.get('https://urlscan.io/api/v1/search/?q='+search) 
			json_response = response.json()
			if json_response['total'] != 0: 
				for record in json_response['results']:
					querydate = datetime.datetime.strptime(record['task']['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
					if (querydate > startdate) and (str(record['page']['domain']) != "onedrive.live.com") and (str(record['page']['domain']) != "login.live.com"):
						urlscan_results.append((category,(record['page']['domain']),(record['page']['url'])))
						#These onedrive and login domains are expected to have MSFT images/files so removing those to reduce some FPs
		time.sleep(2)

	dedup_urlscan_results = []
	for i in urlscan_results:				
		if i not in dedup_urlscan_results:
			dedup_urlscan_results.append(i)

	runningfile = open(keys.working_path+runningtotal_file,'r')
	runningtotal=runningfile.readlines()
	runningfile.close()
	
	total = open(keys.working_path+runningtotal_file,'a+')
	rt = []
	
	uniq_search_terms = []
	for i in dedup_urlscan_results:
		if i[0]	not in uniq_search_terms:
			uniq_search_terms.append(i[0])
	
	for j in runningtotal:
		rt.append(j.rstrip("\r\n"))
	for search_name in uniq_search_terms:
		message = ""
		for k in dedup_urlscan_results:
			if str(k) in rt:
				continue
			else:
				if search_name == str(k[0]):
					if message == "":
						message = "Possible *"+k[0]+"* IoC\r\nDomain "+defang(k[1])+" with URL: "+defang(k[2]) +'\r\n'
					else:
						message = message + "Domain "+defang(k[1])+" with URL: "+defang(k[2]) +'\r\n'
					print >> total, k
		if not message == "":
			message = message + '\r\n' + "================================================================"
			slack.chat.post_message('#'+keys.slack_channel_name, message, username="URLScan", icon_emoji=":exploding_head:")
	total.close()

except Exception as e:
        print 'Error: %s' % e
        sys.exit(1)




