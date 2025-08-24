import requests
from github import Github
from collections import Counter, defaultdict
from pydriller import Repository
from pydriller.metrics.process.lines_count import LinesCount
import os
import git
import shutil
import subprocess
import re
from openpyxl import Workbook
import math
from datetime import datetime
from git import Repo
from pathlib import Path
import pandas as pd
from datetime import datetime


class UserData:
    def __init__(self, name, email, photo):
        self.name = name
        self.email = email
        self.photo = photo
        self.linesAddRemov= None  

    def getLinesAddRemov(self):
        listaRepos = self.createRepoList()

        for repo_dict in listaRepos:
            repoPath = f"./gitClones/{repo_dict['nome']}"
            linhas_adicionadas = 0
            linhas_removidas = 0

            try:
                    for commit in Repository(repoPath).traverse_commits():
                        if commit.author.email == 'johnatan-si@hotmail.com':
                                linhas_adicionadas += commit.insertions
                                linhas_removidas += commit.deletions
   
                    repo_dict['linhaAdd'] = linhas_adicionadas
                    repo_dict['linhaRemov'] = linhas_removidas

            except Exception as e:
                    print(f"Erro ao abrir o repositório em {repoPath}: {e}")

        self.linesAddRemov = listaRepos


    @staticmethod
    def createRepoList():

        repoPath = "./gitClones"
        lista_repositorios = []

        for nome in os.listdir(repoPath):
            caminho_completo = os.path.join(repoPath, nome)

            if os.path.isdir(caminho_completo) and os.path.isdir(os.path.join(caminho_completo, '.git')):
                repo_info = {
                    'nome': nome,
                    'linhaAdd': None,     
                    'linhaRemov': None
                }
                lista_repositorios.append(repo_info)

        return lista_repositorios
    

    
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
        caminho_base = "gitClones"
        
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

                nome_arquivo = f"{repo}.xlsx"
                caminho_saida = os.path.join("./tablesDoa", nome_arquivo)
                wb.save(caminho_saida)
                print(f"Arquivo Excel criado: {caminho_saida}")
                repoAnalisado += 1
            else:
                print(f"Nenhum arquivo de autoria principal para {dev_email} no repositório {repo}.")

        print(f"Total de repositórios analisados com arquivos de autoria principal: {repoAnalisado}/{len(resultados)} ")
        return resultados  


    @staticmethod
    def filtroArquivos():
        folderPath = Path("./tablesDoa")
        fixos = ['.java', '.py', '.js', '.c', '.cpp', '.cs']

        for arquivo in folderPath.iterdir():  

            if arquivo.suffix not in ['.xlsx', '.xls']:  
                continue

            df = pd.read_excel(arquivo)

            if 'Arquivo' not in df.columns:
                print(f"Coluna 'Arquivo' não encontrada em {arquivo.name}")
                continue

            filtro = df['Arquivo'].astype(str).apply(lambda x: any(x.endswith(suf) for suf in fixos))
            df_filtrado = df[filtro]

            df_filtrado.to_excel(arquivo, index=False)

            print(f"Arquivo processado: {arquivo.name} — {len(df) - len(df_filtrado)} linha(s) removida(s)")

    
    @staticmethod
    def captureImports():
        folderPath = Path("./tablesDoa")

        for tabela_path in folderPath.iterdir():
            df = pd.read_excel(tabela_path)  
            df['Imports'] = ""


            for index, row in df.iterrows():

                linha = row['Arquivo']

                arquivoAnalise = Path(f"gitClones/{repo_name}/{linha}")

                importsEncontrados = []

                try:
                    with open(arquivoAnalise, 'r', encoding='utf-8') as arquivo:
                        for line in arquivo:
                            linha_limpa = line.strip()
                            if linha_limpa.startswith(("(", "import", "from", "#include", "include")):
                                importsEncontrados.append(linha_limpa)
                except FileNotFoundError:
                    print(f"[AVISO] Arquivo não encontrado: {arquivoAnalise}")
                    importsEncontrados = ["ARQUIVO NAO ENCONTRADO"]

                df.at[index, 'Imports'] = '\n'.join(importsEncontrados)

            df.to_excel(tabela_path, index=False)


        

