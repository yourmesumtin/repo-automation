import os
import subprocess
import github
from concurrent.futures import ThreadPoolExecutor, as_completed

# Use the GitHub Token provided by GitHub Actions
access_token = os.getenv('GITHUB_TOKEN')

# Initialize GitHub client
gh = github.Github(access_token)

# Get your user or organization
user = gh.get_user() 

# Path to your PR template and JIRA workflow file in the GitHub Actions runner
pr_template_path = './templates/PULL_REQUEST_TEMPLATE.md'
jira_workflow_path = './templates/enforce-jira-key.yml'

# Function to clone, add, commit, and push changes to a repository
def update_repository(repo):
    repo_name = repo.name
    clone_url = repo.clone_url.replace('https://', f'https://x-access-token:{access_token}@')

    # Clone the repository
    subprocess.run(['git', 'clone', clone_url])
    
    # Check if PR template and JIRA workflow already exist
    if os.path.exists(pr_template_path) and os.path.exists(jira_workflow_path):
        print(f'{repo_name} already updated. Skipping...')
        return
    
     # Ensure .github and .github/workflows directories exist
    os.makedirs(f'{repo_name}/.github', exist_ok=True)
    os.makedirs(f'{repo_name}/.github/workflows', exist_ok=True)

    # Add PR template
    os.system(f'cp {pr_template_path} {repo_name}/.github/PULL_REQUEST_TEMPLATE.md')

    # Add JIRA workflow
    os.system(f'cp {jira_workflow_path} {repo_name}/.github/workflows/enforce-jira-key.yml')

    # Git add, commit, and push
    os.chdir(repo_name)
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Add PR template and JIRA workflow'])
    subprocess.run(['git', 'push'])
    os.chdir('..')
    print(f'Successfully updated {repo_name}')

# Use ThreadPoolExecutor for parallel execution
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_repo = {executor.submit(update_repository, repo): repo for repo in user.get_repos()}
    for future in as_completed(future_to_repo):
        repo = future_to_repo[future]
        try:
            data = future.result()
        except Exception as exc:
            print(f'{repo.name} generated an exception: {exc}')
