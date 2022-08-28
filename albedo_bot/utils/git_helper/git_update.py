from pathlib import Path
from git import repo


def pull_repo(repo_path: Path):
    """
    Pull/update the repository found a repo_path

    Args:
        repo_path (str): path to repository locally
    """

    repository_object = repo.Repo(repo_path)

    output = repository_object.remotes[0].pull()
    return output
