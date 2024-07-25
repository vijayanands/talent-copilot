from llama_index.readers.github import GithubRepositoryReader, GithubClient
from dotenv import load_dotenv

load_dotenv()
client = github_client = GithubClient(verbose=True)

reader = GithubRepositoryReader(
    github_client=github_client,
    owner="apache",
    repo="superset",
    use_parser=False,
    verbose=True,
    # filter_directories=(
    #     ["docs"],
    #     GithubRepositoryReader.FilterType.INCLUDE,
    # ),
    filter_file_extensions=(
        [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            "json",
            ".ipynb",
        ],
        GithubRepositoryReader.FilterType.EXCLUDE,
    ),
)

documents = reader.load_data(branch="main")
print(f"Total documents: {len(documents)}")
