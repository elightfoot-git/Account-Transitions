import os
import json
from datetime import datetime
from simple_salesforce import Salesforce

# 1. Authenticate with Salesforce using GitHub Secrets
sf = Salesforce(
    username=os.environ.get('SF_USERNAME'),
    password=os.environ.get('SF_PASSWORD'),
    security_token=os.environ.get('SF_SECURITY_TOKEN'),
    consumer_key=os.environ.get('SF_CONSUMER_KEY'),
    consumer_secret=os.environ.get('SF_CONSUMER_SECRET')
)

# 2. Query Salesforce for your transition data
# (We can adjust these SOQL queries to match your exact Salesforce fields later)
transition_query = "SELECT Transition_Type__c, COUNT(Id) FROM Case WHERE CreatedDate = THIS_YEAR GROUP BY Transition_Type__c"
transition_results = sf.query_all(transition_query)

# Process query data into a dictionary
transitions = {}
for record in transition_results['records']:
    transitions[record['Transition_Type__c']] = record['expr0']

# 3. Format the final JSON structure for your HTML dashboard
dashboard_data = {
    "lastUpdated": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
    "kpis": {
        "totalVolume": sum(transitions.values()),
        "activePipeline": sf.query("SELECT COUNT(Id) FROM Case WHERE IsClosed = False")['totalSize']
    },
    "transitionTypes": transitions,
    "pipelineStatus": {
        "Intake": sf.query("SELECT COUNT(Id) FROM Case WHERE Status = 'Intake'")['totalSize'],
        "In Progress": sf.query("SELECT COUNT(Id) FROM Case WHERE Status = 'In Progress'")['totalSize']
    }
}

# 4. Overwrite data.json
with open('data.json', 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print("Dashboard data successfully synced!")
