# URLScanBot
A Slackbot to perform periodic URLScan queries and kick the results back to a Slack channel

####Requirements####

pip install slacker
pip install defang
pip install requests


runningtotal.txt in the same directory as the script


searches.txt in the same directory as the script with the URLScan searches you'd like to perform in the following format:
	[name_of_search], [urlscan_search_url_encoded]
	[name_of_search], [urlscan_search_url_encoded]

Example: 

	lucy_server, page.server%3A"Lucy"


keys.py with your Slack Slacker ID, working directory path, and slack channel name

	See sample keys file
