from flask import jsonify
import json
def generate_summary(data):
    # Here you would typically process the data and generate a summary
    # For this example, we'll just create a simple summary
    summary = f"Summary for {data['profileInfo']['firstName']} {data['profileInfo']['lastName']}:\n"
    summary += f"Email: {data['profileInfo']['email']}\n"
    summary += f"Atlassian - Confluence: {data['atlassianInfo']['confluenceUsername']}, Jira: {data['atlassianInfo']['jiraUsername']}\n"
    summary += f"GitHub Username: {data['githubInfo']['username']}\n"
    summary += f"Time Range: {data['timeRange']['start']} to {data['timeRange']['end']}\n"
    
    # In a real application, you would use the provided credentials to fetch data from the respective services
    # and generate a meaningful summary based on the user's activity during the specified time range

    summary = "this is a sample summary"

    return jsonify({"summary": summary})
