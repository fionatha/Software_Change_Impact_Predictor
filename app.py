
from flask import Flask, render_template, request
from git import Repo, GitCommandError
from analyzer.change_detector import detect_changes
from urllib.parse import urlparse
import os
import uuid
import html

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():

    repo_url = request.form.get('repo_url', '').strip()
    parsed_url = urlparse(repo_url)

    if parsed_url.scheme != 'https' or parsed_url.hostname != 'github.com':
        return "<h2>Please enter a valid HTTPS GitHub URL.</h2>"

    parts = parsed_url.path.strip('/').split('/')

    if len(parts) != 2:
        return "<h2>Invalid GitHub repository URL.</h2>"

    owner, repo_name = parts

    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]

    destination = os.path.join(
        UPLOAD_FOLDER,
        f"{owner}_{repo_name}_{uuid.uuid4().hex[:8]}"
    )

    try:
        # Clone the complete repository history
        Repo.clone_from(repo_url, destination)

        # Detect changes between the latest commits
        changes = detect_changes(destination)

        result = "<h1>Code Change Analysis Results</h1>"

        categories = {
            "Modified Files": changes["modified"],
            "Added Files": changes["added"],
            "Deleted Files": changes["deleted"],
            "Renamed Files": changes["renamed"]
        }

        for title, files in categories.items():
            result += f"<h2>{title} ({len(files)})</h2>"
            if files:
                result += "<ul>"
                for file in files:
                    result += f"<li>{html.escape(file)}</li>"
                result += "</ul>"
            else:
                result += "<p>No files detected.</p>"

        result += '<br><a href="/">Analyze Another Repository</a>'

        return result

    except GitCommandError:
        return """
        <h1>Repository Upload Failed</h1>
        <p>Check your GitHub URL and repository access.</p>
        <a href="/">Try Again</a>
        """


if __name__ == '__main__':
    app.run(debug=True)
