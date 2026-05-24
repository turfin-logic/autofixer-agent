import os
import uuid
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubBot:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("GITHUB_REPO")
        
        if not self.token or not self.repo_name:
            print("⚠️ [GitHub] Warning: GITHUB_TOKEN or GITHUB_REPO not found. Running in mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            self.g = Github(self.token)
            self.repo = self.g.get_repo(self.repo_name)
        
    def create_pull_request(self, analysis, fix_code):
        branch_name = f"autofix-{analysis['error'].lower()}-{uuid.uuid4().hex[:6]}"
        print(f"🐙 [GitHub] Creating branch: {branch_name}...")
        
        pr_title = f"Fix {analysis['error']} in {analysis['file']}"
        pr_body = f"## AutoFixer Agent 🤖\n\nI detected a crash (`{analysis['message']}`) and automatically wrote a fix.\n\n**File:** `{analysis['file']}`\n**Line:** `{analysis['line']}`\n\nPlease review and merge this PR to resolve the production crash."
        
        if self.mock_mode:
            print(f"🚀 [GitHub MOCK] Pull Request Opened Successfully!\nTitle: {pr_title}\nBody: {pr_body}")
            return "https://github.com/mock/mock/pulls/1"

        try:
            # Get main branch reference to branch off
            main_ref = self.repo.get_branch("main")
            self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_ref.commit.sha)
            
            # Update the file
            file_path = analysis['file']
            file_contents = self.repo.get_contents(file_path, ref="main")
            self.repo.update_file(
                path=file_path,
                message=f"AutoFixer: Fixing {analysis['error']}",
                content=fix_code,
                sha=file_contents.sha,
                branch=branch_name
            )
            
            # Create Pull Request
            pr = self.repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base="main"
            )
            print(f"🚀 [GitHub] Pull Request Opened Successfully!")
            return pr.html_url
        except Exception as e:
            print(f"❌ [GitHub] Failed to create PR: {e}")
            return "Failed"

