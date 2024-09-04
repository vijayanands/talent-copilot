import json

from functions.llamaindex_appraisal import self_appraisal_tool
from helpers.confluence import get_confluence_contributions_by_author
from helpers.github import (get_github_contributions_by_author,
                            initialize_github_hack)
from helpers.jira import get_jira_contributions_by_author

debug_jira = False
debug_confluence = False
debug_github = True



def create_self_appraisal(author):
    initialize_github_hack()
    return self_appraisal_tool(author)
