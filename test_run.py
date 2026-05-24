import sys
sys.stdout.reconfigure(encoding='utf-8')
from agent import AutoFixAgent
from github_bot import GitHubBot

print("--- AutoFixer Manual Test Run ---")
agent = AutoFixAgent()
bot = GitHubBot()

dummy_error = """Traceback (most recent call last):
  File "test.py", line 15, in <module>
TypeError: expected string"""

print("Injecting dummy crash log...")
analysis = agent.analyze_error(dummy_error)
if analysis:
    fix_code = agent.generate_fix_code(analysis)
    pr_url = bot.create_pull_request(analysis, fix_code)
    print(f"Process Complete! PR created at: {pr_url}")
else:
    print("Analysis failed.")
