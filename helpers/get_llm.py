from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI


# def get_llm(llm_choice):
#     if llm_choice == "OpenAI":
#         return OpenAI(model="gpt-3.5-turbo", temperature=0)
#     else:
#         return Anthropic(model="claude-2", temperature=0)
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
