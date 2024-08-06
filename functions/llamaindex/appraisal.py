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
    You are tasked with generating a professional self-appraisal based only on the following information about an employee's contributions:

    {context}

    Please create a self-appraisal with the following guidelines:
    1. Use an official and professional tone.
    2. Focus on facts and provide links to associated documents when possible.
    3. Highlight key achievements and contributions.
    4. Suggest potential learning opportunities based on the employee's work.
    5. Create an appendix that lists all of the following
        - links to all JIRAs resolved
        - links to confluence contributed
        - links to github commits made
    5. Format the output as a valid JSON object with the following structure:
       {{
         "Summary": "Overall summary...",
         "Key Achievements": ["Achievement 1", "Achievement 2", ...],
         "Contributions": {{
           "Project A": "Details about contributions to Project A...",
           "Project B": "Details about contributions to Project B..."
         }},
         "Learning Opportunities": ["Opportunity 1", "Opportunity 2", ...]
         "Appendix": {{
            "JIRAs Resolved": ["Link 1", "Link 2",...],
            "confluence Contributed": ["Link 1", "Link 2",...],
            "github commits": ["Link 1", "Link 2",...]
         }}
       }}
    
    Ensure that the Key Achievements section contains information about all three function outputs, namely, Jira, GitHub, and Confluence contributions.
    Ensure that the Contributions section contains detailed information about each project, including project name, description, and any relevant links or screenshots.
    Ensure that the response is a valid JSON object and nothing else. Do not include any markdown formatting or code blocks.

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
    # Generate the self-appraisal using the LLM
    appraisal_response = llm.complete(APPRAISAL_PROMPT.format(context=context))

    # Parse the JSON response
    try:
        # Try to parse the response as JSON
        appraisal_json = json.loads(appraisal_response.text)
    except json.JSONDecodeError:
        print("Error: LLM output is not valid JSON. Attempting to clean the output.")

        # Remove any potential markdown formatting
        cleaned_text = appraisal_response.text.strip('`').strip()
        if cleaned_text.startswith('json'):
            cleaned_text = cleaned_text[4:].strip()

        try:
            # Try parsing the cleaned text
            appraisal_json = json.loads(cleaned_text)
        except json.JSONDecodeError:
            print("Error: Cleaned output is still not valid JSON. Falling back to raw text.")
            appraisal_json = {"Raw Appraisal": appraisal_response.text}

    return json.dumps(appraisal_json, indent=2)


def save_appraisal_to_json(appraisal: str, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(appraisal)
    print(f"Appraisal saved to {filename}")