import os
from typing import List

from dotenv import load_dotenv
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()


def find_learning_resources(
    skills: List[str],
    llm: OpenAI = OpenAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY")),
):
    # Define the prompt template
    prompt_template = PromptTemplate(
        "You are an assistant skilled at finding learning resources and events such as conferences and meetups. "
        "I am interested in the following skills: {skills}. "
        "Please recommend a list of online learning opportunities, upcoming conferences, and meetups relevant to these skills. "
        "Provide the details about the opportunity and a clickable link for each recommendation if one is available. "
        "If one is not available, provide a recommendation on what I can search for."
    )

    # Format the prompt with the given skills
    prompt = prompt_template.format(skills=", ".join(skills))

    # Use the LLM to generate a response
    response = llm.complete(prompt)

    return response


# Example usage:
if __name__ == "__main__":
    # List of skills you're interested in
    skills = ["Python", "Machine Learning", "Data Visualization"]

    # Find learning resources (using default GPT-4 model)
    result = find_learning_resources(skills)
    print(result)

    # Optionally, use a different OpenAI model
    custom_llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
    custom_result = find_learning_resources(skills, llm=custom_llm)
    print(custom_result)
