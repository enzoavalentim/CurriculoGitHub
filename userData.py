import requests
from github import Github
from collections import Counter, defaultdict
from pydriller import Repository
import os
import git
import shutil
import subprocess
import re
from openpyxl import Workbook
import math
from datetime import datetime
from git import Repo

class UserData:
    def __init__(self, name, email, photo):
        self.name = name
        self.email = email
        self.photo = photo
        self.top_languages_data = None  

    def getEmail(self, userName, GitToken):
        user = userName
        g = GitToken
        caminhoEmailFinder = "github-email-finder"
        comando = f"python3 script.py {user} --token {g}"
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, cwd=caminhoEmailFinder)

        saida = resultado.stdout
        
        padrao_email = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        emails = re.findall(padrao_email, saida)
        emails_unicos = list(set(emails))
        self.email = emails_unicos
        
        return emails_unicos

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
    
    def cloningRepos(self, github_token: str, username: str):

        CLONE_DIR = "gitClones"
        TABLES_DIR = "tablesDoa"
        
        if os.path.exists(CLONE_DIR):
            shutil.rmtree(CLONE_DIR)
        os.makedirs(CLONE_DIR, exist_ok=True)

        if os.path.exists(TABLES_DIR):
            shutil.rmtree(TABLES_DIR)
        os.makedirs(TABLES_DIR, exist_ok=True)

        g = Github(github_token)
        user = g.get_user(username)

        allowedLanguages = {'Java', 'JavaScript', 'Python', 'C', 'C++', 'C#'}

        for repo in user.get_repos():
            try:
                local_path = os.path.join(CLONE_DIR, repo.name)
                language = repo.language or "Unknown"

                if not os.path.exists(local_path):
                    if language in allowedLanguages:
                        git.Repo.clone_from(repo.clone_url, local_path)
        
            except Exception as e:
                print(f"❌ Failed to clone {repo.name}: {e}")
        print("Todas reposClonados com sucesso!")
    


    def calcDOA(self, dev_email: str):
        caminho_base = "./gitClones"
        
        repositorios = [os.path.join(caminho_base, d) for d in os.listdir(caminho_base)
                        if os.path.isdir(os.path.join(caminho_base, d))]

        resultados = {}  

        for repo_path in repositorios:
            try:
                repo = Repo(repo_path)
            except Exception as e:
                print(f"Erro ao abrir o repositório em {repo_path}: {e}")
                continue

            commits = list(repo.iter_commits())
            arquivoCommits = defaultdict(list)

            for commit in reversed(commits):
                author_name = commit.author.name
                author_login = commit.author.email
                commit_date = datetime.fromtimestamp(commit.committed_date)

                for file in commit.stats.files:
                    arquivoCommits[file].append({
                        'commit': commit,
                        'autor_nome': author_name,
                        'autor_login': author_login,
                        'data': commit_date
                    })

            arquivosAutoriaAlvo = []

            for arquivo, commits_info in arquivoCommits.items():
                ordered_commits = sorted(commits_info, key=lambda x: x['data'])
                dev_stats = defaultdict(lambda: {'FA': 0, 'DL': 0, 'AC': 0})

                primeiro_commit = ordered_commits[0]
                primeiro_autor = primeiro_commit['autor_login']
                dev_stats[primeiro_autor]['FA'] = 1
                dev_stats[primeiro_autor]['DL'] += 1

                for commit_info in ordered_commits[1:]:
                    autor = commit_info['autor_login']
                    dev_stats[autor]['DL'] += 1

                for dev in dev_stats:
                    outros_devs = [d for d in dev_stats if d != dev]
                    dev_stats[dev]['AC'] = sum(dev_stats[d]['DL'] for d in outros_devs)

                dev_doa = {}
                for dev, stats in dev_stats.items():
                    FA = stats['FA']
                    DL = stats['DL']
                    AC = stats['AC']
                    doa = 3.293 + 1.098 * FA + 0.164 * DL - 0.321 * math.log(1 + AC)
                    dev_doa[dev] = doa

                doa_max = max(dev_doa.values())
                doa_normalizado = {dev: val / doa_max for dev, val in dev_doa.items()}

                if dev_email in dev_doa:
                    if (
                        dev_doa[dev_email] == doa_max and
                        dev_doa[dev_email] >= 3.293 and
                        doa_normalizado[dev_email] >= 0.75
                    ):
                        arquivosAutoriaAlvo.append(arquivo)

            nome_repo = os.path.basename(repo_path)
            resultados[nome_repo] = arquivosAutoriaAlvo

        repoAnalisado = 0
        for repo, arquivos in resultados.items():
            if arquivos:
                wb = Workbook()
                ws = wb.active
                ws.title = "Arquivos DOA"

                ws.append(["Arquivo"])

                for arq in arquivos:
                    ws.append([arq])

                nome_arquivo = f"{repo}_DOA.xlsx"
                caminho_saida = os.path.join("./tablesDoa", nome_arquivo)
                wb.save(caminho_saida)
                print(f"Arquivo Excel criado: {caminho_saida}")
                repoAnalisado += 1
            else:
                print(f"Nenhum arquivo de autoria principal para {dev_email} no repositório {repo}.")

        print(f"Total de repositórios analisados com arquivos de autoria principal: {repoAnalisado}/{len(resultados)} ")
        return resultados  
