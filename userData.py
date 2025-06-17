import requests

class UserData:

    def __init__(self, name, email, photo):
        self.name = name
        self.email = email
        self.photo = photo

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
                                #print(f"E-mail encontrado nos commits: {email}")
                                return email

        print("Nenhum e-mail público encontrado para este usuário.")
        return None




        
