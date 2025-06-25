import requests
from github import Github
from collections import Counter, defaultdict
from pydriller import Repository
import os
import git
import shutil

class UserData:
    def __init__(self, name, email, photo):
        self.name = name
        self.email = email
        self.photo = photo
        self.top_languages_data = None  

    @staticmethod
    def getEmail(userName, GitToken):
        GITHUB_TOKEN = GitToken  
        HEADERS = {
            "Accept": "application/vnd.github+json"
        }

        if GITHUB_TOKEN:
            HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

        url = f"https://api.github.com/users/{userName}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            if data.get("email"):
                print(f"E-mail encontrado no perfil: {data['email']}")
                return data["email"]

        repos_url = f"https://api.github.com/users/{userName}/repos"
        repos_response = requests.get(repos_url, headers=HEADERS)

        if repos_response.status_code == 200:
            repos = repos_response.json()
            for repo in repos:
                if repo.get("fork"):
                    continue  

                repo_name = repo["name"]
                commits_url = f"https://api.github.com/repos/{userName}/{repo_name}/commits"
                commits_response = requests.get(commits_url, headers=HEADERS)
                
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    for commit in commits:
                        if isinstance(commit, dict): 
                            commit_info = commit.get("commit", {}).get("author", {})
                            email = commit_info.get("email")
                            if email and "noreply.github.com" not in email:
                                return email

        print("Nenhum e-mail público encontrado para este usuário.")
        return None

    def getTop5Repos(self, github_token: str, username: str) -> dict:
        g = Github(github_token)
        user = g.get_user(username)
        
        language_commit_counter = Counter()
        repos_language = defaultdict(list)

        for repo in user.get_repos():
            try:
                commits = repo.get_commits()
                commit_count = commits.totalCount
                langs = repo.get_languages()
                repo_name = repo.name
                repo_url = repo.clone_url

                for lang in langs:
                    language_commit_counter[lang] += commit_count
                    repos_language[lang].append({
                        'name': repo_name,
                        'commits': commit_count,
                        'locAdd': 0,
                        'locRemov': 0,
                        'url': repo_url
                    })

            except Exception as e:
                print(f"⚠️ Erro ao acessar {repo.name}: {e}")

        top_5_languages = language_commit_counter.most_common(5)
        top5_repos_language = {lang: repos_language[lang] for lang, _ in top_5_languages}
        self.top_languages_data = top_5_languages

        return {
            'user_info': {
                'name': user.name,
                'login': user.login,
                'avatar_url': user.avatar_url,
                'email': user.email
            },
            'top_languages': top_5_languages,
            'repos_by_language': top5_repos_language
        }
    

    def getLinesAddRemov(self, github_token: str, username: str, user_email: str,  filter_by_user: bool = True ) -> dict:

        CLONE_DIR = "gitClones"
        
        if os.path.exists(CLONE_DIR):
            shutil.rmtree(CLONE_DIR)
        os.makedirs(CLONE_DIR, exist_ok=True)

        if not hasattr(self, 'top_languages_data') or not self.top_languages_data:
            g = Github(github_token)
            user = g.get_user(username)
            
            language_commit_counter = Counter()
            repos_language = defaultdict(list)

            for repo in user.get_repos():
                try:
                    commits = repo.get_commits()
                    commit_count = commits.totalCount
                    langs = repo.get_languages()
                    
                    for lang in langs:
                        language_commit_counter[lang] += commit_count
                        repos_language[lang].append({
                            'name': repo.name,
                            'commits': commit_count,
                            'url': repo.clone_url
                        })

                except Exception as e:
                    print(f"⚠️ Error accessing {repo.name}: {e}")

            self.top_languages_data = {
                'top_languages': language_commit_counter.most_common(5),
                'repos_language': repos_language
            }

        top5_repos_language = defaultdict(list)

        for lang, _ in self.top_languages_data['top_languages']:
            for repo_info in self.top_languages_data['repos_language'][lang]:
                repo_name = repo_info['name']
                local_path = os.path.join(CLONE_DIR, repo_name)

                if not os.path.exists(local_path):
                    try:
                        print(f"🔽 Cloning {repo_name}...")
                        git.Repo.clone_from(repo_info['url'], local_path)
                    except Exception as e:
                        print(f"❌ Failed to clone {repo_name}: {e}")
                        continue

                loc_add, loc_remov = 0, 0
                try:
                    for commit in Repository(local_path).traverse_commits():
                        if filter_by_user and commit.author.email != user_email:
                            continue

                        for mod in commit.modified_files:
                            loc_add += mod.added_lines if mod.added_lines else 0
                            loc_remov += mod.deleted_lines if mod.deleted_lines else 0

                except Exception as e:
                    print(f"❌ Error analyzing {repo_name}: {e}")
                    continue

                top5_repos_language[lang].append({
                    'name': repo_name,
                    'commits': repo_info['commits'],
                    'locAdd': loc_add,
                    'locRemov': loc_remov
                })

        return {
            'top_languages': self.top_languages_data['top_languages'],
            'repos_by_language': top5_repos_language
        }