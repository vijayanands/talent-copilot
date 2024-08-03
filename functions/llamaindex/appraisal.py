from typing import List

from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llama_index.core.prompts import PromptTemplate
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI

from helpers.confluence import get_confluence_contributions_by_author
from helpers.github import get_github_contributions_by_author
from helpers.jira import get_jira_contributions_by_author

load_dotenv()

# Create FunctionTool instances
tools: List[BaseTool] = [
    FunctionTool.from_defaults(fn=get_jira_contributions_by_author),
    FunctionTool.from_defaults(fn=get_github_contributions_by_author),
    FunctionTool.from_defaults(fn=get_confluence_contributions_by_author),
]


def get_llm(vendor: str, **kwargs):
    """
    Factory function to create an LLM instance based on the vendor.
    """
    if vendor.lower() == "openai":
        return OpenAI(
            temperature=kwargs.get("temperature", 0.7),
            model=kwargs.get("model", "gpt-3.5-turbo"),
        )
    elif vendor.lower() == "anthropic":
        return Anthropic(
            temperature=kwargs.get("temperature", 0.7),
            model=kwargs.get("model", "claude-2"),
        )
    else:
        raise ValueError(f"Unsupported LLM vendor: {vendor}")


# Define a custom prompt for generating the self-appraisal
APPRAISAL_PROMPT = PromptTemplate(
    """
    You are tasked with generating a professional self-appraisal based only on the following information about an employee's contributions:

    {context}

    Please create a self-appraisal with the following guidelines:
    1. Use an official and professional tone.
    2. Focus on facts and provide links to associated documents when possible.
    3. Highlight key achievements and contributions.
    4. Suggest potential learning opportunities based on the employee's work.
    5. Format the appraisal in a clear and organized manner.

    Self-Appraisal:
    """
)


def generate_self_appraisal(author: str, llm_vendor: str, **llm_kwargs) -> str:
    # Create the LLM instance
    llm = get_llm(llm_vendor, **llm_kwargs)

    # Create the ReAct agent
    agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)

    # Use the ReAct agent to gather information
    jira_query = f"Get Jira contributions for {author}"
    github_query = f"Get GitHub contributions for {author}"
    confluence_query = f"Get Confluence contributions for {author}"

    jira_response = agent.chat(jira_query)
    github_response = agent.chat(github_query)
    confluence_response = agent.chat(confluence_query)

    # Combine the gathered information
    context = f"""
    Jira Contributions:
    {jira_response.response}

    GitHub Contributions:
    {github_response.response}

    Confluence Contributions:
    {confluence_response.response}
    """

    # Generate the self-appraisal using the LLM
    appraisal_response = llm.complete(APPRAISAL_PROMPT.format(context=context))

    return appraisal_response.text


def create_html_document(appraisal: str) -> str:
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Self-Appraisal</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .appraisal {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Employee Self-Appraisal</h1>
        <div class="appraisal">
            {appraisal}
        </div>
    </body>
    </html>
    """
    return html
