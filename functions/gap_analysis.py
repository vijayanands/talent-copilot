import os
from typing import Dict, List

from dotenv import load_dotenv
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()


def perform_gap_analysis(
    skills: List[Dict[str, int]],
    eligibility_criteria: str,
    llm: OpenAI = OpenAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY")),
):
    # Define the prompt template
    prompt_template = PromptTemplate(
        "You are an assistant skilled at performing gap analysis for career progression. "
        "The user has the following skills and proficiency levels (on a scale of 1-5): {skills}. "
        "The eligibility criteria for the next career level are: {eligibility_criteria}. "
        "Based on this information, please identify and list the key areas where the user needs to focus "
        "to meet the eligibility criteria for the next level. For each area, provide a brief explanation "
        "of why it's important and how it relates to the eligibility criteria."
    )

    # Format the skills list for the prompt
    formatted_skills = ", ".join(
        [f"{skill['name']} (Level: {skill['level']})" for skill in skills]
    )

    # Format the prompt with the given skills and eligibility criteria
    prompt = prompt_template.format(
        skills=formatted_skills, eligibility_criteria=eligibility_criteria
    )

    # Use the LLM to generate a response
    response = llm.complete(prompt)

    return response.text


# Example usage:
if __name__ == "__main__":
    # Example skills list
    skills = [
        {"name": "Python", "level": 4},
        {"name": "Machine Learning", "level": 3},
        {"name": "Data Visualization", "level": 2},
    ]

    # Example eligibility criteria
    eligibility_criteria = "Advanced proficiency in Python, strong understanding of machine learning algorithms, and ability to create complex data visualizations."

    # Perform gap analysis
    result = perform_gap_analysis(skills, eligibility_criteria)
    print(result)
