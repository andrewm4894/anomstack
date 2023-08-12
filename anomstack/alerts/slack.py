"""
Helper functions for sending alerts via Slack.
"""

import requests
import json
import os


def send_alert_slack(title='alert', message='hello', env_var_webhook_url='ANOMSTACK_SLACK_WEBHOOK_URL') -> requests.Response:
    """
    Send alert via webhook.
    """
    
    webhook_url = os.environ[env_var_webhook_url]
    payload = {
        #'text': f'{title}',
        'blocks': [
            {
    		"type": "section",
    		"text": {
    			"type": "mrkdwn",
    			"text": title
    		    }
    	    },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    
    return response
