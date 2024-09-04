# Pathforge Empower
*Empowering employee productivity, performance, career, learning and skills*

## Clone the repository
- `git clone https://github.com/vijayanands/talent-copilot.git`
(or)
- `git clone git@github.com:vijayanands/talent-copilot.git`

### Dependecies
#### Install Poetry
https://python-poetry.org/docs/

### How to run the application
#### Environment Variables to setup
- cd talent-copilot (or wherever the repository was clone and env setup)
- Set the environment variables as per the .env.template
-`GITHUB_TOKEN=your_github_personal_access_token
ATLASSIAN_API_TOKEN=your_atlassian_api_key
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PROXYCURL_API_KEY=your_proxy_curl_api_key`
- copy .env.template to .env with the valid values for the variables
#### Run the application
- poetry shell
- poetry install
- streamlit run app.py

