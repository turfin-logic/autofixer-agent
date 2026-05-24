import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
from watcher import start_watching
from agent import AutoFixAgent
from github_bot import GitHubBot

LOG_FILE = "error.log"

agent = AutoFixAgent()
github = GitHubBot()

def handle_crash(error_text):
    print("\n" + "="*50)
    
    # 1. AI Agent analyzes the stack trace
    analysis = agent.analyze_error(error_text)
    
    if analysis:
        # 2. AI Agent generates the fix
        fix_code = agent.generate_fix_code(analysis)
        
        # 3. GitHub Bot pushes the fix and creates a PR
        pr_link = github.create_pull_request(analysis, fix_code)
        print(f"🎉 All done! PR is waiting for review at: {pr_link}")
        
        # Clear the log after fixing to prevent infinite loops in this mock
        with open(LOG_FILE, 'w') as f:
            f.write("")
            
    print("="*50 + "\n")

if __name__ == "__main__":
    print("🚀 Starting AutoFixer Agent...")
    start_watching(LOG_FILE, handle_crash)
