---
title: "Pathforge Empower"
emoji: 👁
colorFrom: "green"
colorTo: "blue"
sdk: "streamlit"
sdk_version: "1.37.0"
app_file: app.py
pinned: false
---

# Instructions for Local Installation
> **Note:** The following section is README required for installing the application in your local desktop

## Pathforge Empower
*Empowering employee productivity, performance, career, learning and skills*

### Clone the repository
- `git clone https://github.com/vijayanands/talent-copilot.git`
(or)
- `git clone git@github.com:vijayanands/talent-copilot.git`

### Dependencies
#### Install Poetry
https://python-poetry.org/docs/

## How to run the application
### Environment Variables to setup
1. cd talent-copilot (or wherever the repository was cloned and env setup)
2. Set the environment variables as per the .env.template:
   ```
   GITHUB_TOKEN=your_github_personal_access_token
   ATLASSIAN_API_TOKEN=your_atlassian_api_key
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PROXYCURL_API_KEY=your_proxy_curl_api_key
   ```
3. Copy .env.template to .env with the valid values for the variables

#### Run the application
1. `poetry shell`
2. `poetry install`
3. `streamlit run app.py`
