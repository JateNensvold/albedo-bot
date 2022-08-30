from enum import Enum
from pathlib import Path
from git import repo, Head, Remote, GitError, Commit, DiffIndex
from git.diff import T_Diff


class ChangeType(Enum):
    """
    An enum class to represent all the types of changes a file can have
        during a git commit
    """
    #('A', 'C', 'D', 'R', 'M', 'T')
    added: str = "A"
    copied: str = "C"
    deleted: str = "D"
    renamed: str = "R"
    modified: str = "M"
    mode: str = "T"


class CommitInfo:
    """
    A utility class used to store all the information about a git commit
    """

    def __init__(self, commit: Commit, diff: DiffIndex) -> None:
        """
        Generate a message containing information about everything that
            changed in `commit`

        Args:
            commit (Commit): commit that changes occurred in
            diff (DiffIndex): diff of changes between the last_commit and
                `commit`
        """
        self.commit = commit
        self.diff = diff
        self.file_changes: dict[str, ChangeType] = {}
        self.messages: list[str] = [
            f"Author: {commit.author} - Commit: {commit.authored_date}",
            commit.message.strip()]
        change_messages = self.generate_diff(diff)
        self.messages.extend(change_messages)
        self.message: str = "\n".join(self.messages)

    def generate_diff(self, diff: DiffIndex):
        """
        Generate a list of files changes from `diff`

        Args:
            diff (DiffIndex): diff object with changes

        Returns:
            list[str]: list of file change messages
        """
        commit_info: list[str] = []

        for cht in diff.change_type:
            changes: list[T_Diff] = list(diff.iter_change_type(cht))
            if len(changes) == 0:
                continue
            commit_info.append(
                f"\nChange type: {ChangeType(cht).name.capitalize()}")
            for change_type in changes:
                self.file_changes
                commit_info.append(change_type.b_path)
        return commit_info


class RepoUpdate:
    """
    A utility class used to store all the updates that have occurred in a repo
    """

    def __init__(self, repository: repo.Repo, old_commit: Commit,
                 new_commit: Commit):
        """
        All the information about the updates `repository` had

        Args:
            repository (repo.Repo): repository that was updated
            old_commit (Commit): commit before updates occurred
            new_commit (Commit): current after updates occurred
        """
        self.file_changes: dict[str, ChangeType] = {}
        self.commit_info: list[CommitInfo] = []

        last_commit: Commit = old_commit
        for commit in repository.iter_commits(f"{old_commit}..{new_commit}"):
            diff = last_commit.diff(commit)
            latest_commit_info = CommitInfo(commit, diff)
            self.commit_info.append(latest_commit_info)
            self.file_changes.update(latest_commit_info.file_changes)
            last_commit = commit
        self.message = "\n".join(
            [commit_info.message for commit_info in self.commit_info])


def pull_repo(repo_path: Path, remote: Remote = None, branch: Head = None):
    """
    Pull/update the repository found a repo_path. If `remote` is provided then
    `repo_path` is ignored and the pull is performed on `remote`

    If `branch` is provided then the pull update for that branch will be
    returned, otherwise the active git branch will be used

    Args:
        repo_path (Path): path to repository locally
        remote (Remote, optional): remote to perform pull on.
            Defaults to None.
        branch (Head, optional): head to get update for.
            Defaults to None.

    Returns:
        FetchInfo: updates pulled for `branch`
    """

    if not branch:
        branch = get_branch(repo_path)

    if not remote:
        remote = get_remote(repo_path, branch=branch)

    fetch_list = remote.pull()

    desired_info = "/".join([remote.name, branch.name])

    for fetch_info in fetch_list:
        if fetch_info.name == desired_info:
            return fetch_info

    raise GitError(
        (f"Unable to find remote {remote.name} and branch "
         f"{branch.name} - {desired_info}"))


def get_remote(repo_path: Path, branch: Head = None):
    """
    Get the current remote of the repo at `repo_path`, If `branch` is provided
    then it will be used to get the remote reference instead of fetching the
    currently active git branch that `repo_path` is using.

    If no remote reference can be found then the default remote for the repo
        will be returned

    Args:
        repo_path (Path): path to repository locally
        branch (Head, optional): head to get remote from.
            Defaults to None.

    Returns:
        (Remote): the remote that is
    """
    repository_object = repo.Repo(repo_path)

    if not branch:
        branch = get_branch(repo_path)

    remote_reference = branch.tracking_branch()
    if remote_reference is None:
        remote = repository_object.remote()
    else:
        remote = repository_object.remote(remote_reference.remote_name)
    return remote


def get_branch(repo_path: Path):
    """
    Get the current branch of the repo at `repo_path`

    Args:
        repo_path (Path): path to repository locally
    Returns:
        (Head): current branch
    """

    repository_object = repo.Repo(repo_path)
    return repository_object.active_branch


def update_repo(repo_path: Path):
    """
    Update a repository to the latest information available

    Args:
        repo_path (Path): path to repository locally

    Returns:
        (RepoUpdate): all the updates that `repo_path` had
    """
    repository_object = repo.Repo(repo_path)

    current_branch = get_branch(repo_path)
    old_commit = current_branch.commit

    current_remote = get_remote(repo_path,
                                branch=current_branch)

    output = pull_repo(repo_path,
                       remote=current_remote,
                       branch=current_branch)
    new_commit = output.commit

    repo_update = RepoUpdate(repository_object,
                             old_commit=old_commit,
                             new_commit=new_commit)
    return repo_update


if __name__ == "__main__":

    # Update AFK_Helper repo
    import albedo_bot.config as config
    print(config.AFK_HELPER_PATH)
    repo_update = update_repo(config.AFK_HELPER_PATH)

    for commit_info in repo_update.commit_info:
        print(commit_info.message)
