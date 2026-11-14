
from git import Repo


def detect_changes(repo_path):

    repo = Repo(repo_path)

    # Get the latest commit
    current_commit = repo.head.commit

    # Get the previous commit
    if current_commit.parents:
        previous_commit = current_commit.parents[0]

        # Compare the two commits
        changes = previous_commit.diff(current_commit)

    else:
        # First commit: all files are newly added
        changes = []

    modified_files = []
    added_files = []
    deleted_files = []
    renamed_files = []

    for change in changes:

        if change.change_type == 'M':
            modified_files.append(change.b_path)

        elif change.change_type == 'A':
            added_files.append(change.b_path)

        elif change.change_type == 'D':
            deleted_files.append(change.a_path)

        elif change.change_type == 'R':
            renamed_files.append(change.b_path)

    return {
        "modified": modified_files,
        "added": added_files,
        "deleted": deleted_files,
        "renamed": renamed_files
    }
# Testing Python code change detection