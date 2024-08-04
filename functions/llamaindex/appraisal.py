import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llama_index.core.prompts import PromptTemplate
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI

from helpers.confluence import get_confluence_contributions_by_author
from helpers.jira import get_jira_contributions_by_author
from helpers.github import get_github_contributions_by_author

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
    ... (previous instructions)

    5. Format the output as a valid JSON object with the following structure:
       {{
         "Summary": {{"content": "Overall summary..."}},
         "Key Achievements": {{"items": ["Achievement 1", "Achievement 2", ...]}},
         "Contributions": {{
           "Project A": {{"content": "Details about contributions to Project A..."}},
           "Project B": {{"content": "Details about contributions to Project B..."}}
         }},
         "Learning Opportunities": {{"items": ["Opportunity 1", "Opportunity 2", ...]}}
       }}

    Ensure that the Key Achievements section contains information about all three function outputs, namely, Jira, GitHub, and Confluence contributions.
    Ensure that the Contributions section contains detailed information about each project, including project name, description, and any relevant links or screenshots.
    Ensure that the response is a valid JSON object and nothing else.

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

    # Parse the JSON response
    try:
        appraisal_json = json.loads(appraisal_response.text)
    except json.JSONDecodeError:
        print("Error: LLM output is not valid JSON. Falling back to raw text.")
        appraisal_json = {"Raw Appraisal": {"content": appraisal_response.text}}

    return appraisal_json


def save_appraisal_to_json(
    appraisal: Any, filename: str
) -> None:
    with open(filename, "w") as f:
        json.dump(appraisal, f, indent=2)
    print(f"Appraisal saved to {filename}")
