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
from charset_normalizer import from_path


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

    @staticmethod
    def filtroArquivos():
        folderPath = Path("./tablesDoa")
        fixos = ['.java', '.py', '.js', '.c', '.cpp', '.cs']

        for arquivo in folderPath.iterdir():  # Para cada arquivo na pasta

            if arquivo.suffix not in ['.xlsx', '.xls']:  
                continue

            df = pd.read_excel(arquivo)

            if 'Arquivo' not in df.columns:
                print(f"Coluna 'Arquivo' não encontrada em {arquivo.name}")
                continue

            filtro = df['Arquivo'].astype(str).apply(lambda x: any(x.endswith(suf) for suf in fixos))
            df_filtrado = df[filtro]

            df_filtrado.to_excel(arquivo, index=False)

            #print(f"Arquivo processado: {arquivo.name} — {len(df) - len(df_filtrado)} linha(s) removida(s)")

    


    @staticmethod
    def captureImports():
        folderPath = Path("./tablesDoa")

        for tabela_path in folderPath.iterdir():
            if not tabela_path.name.endswith((".xlsx", ".xls")):
                continue

            df = pd.read_excel(tabela_path)
            df['Imports'] = ""
            repo_name = tabela_path.stem

            for index, row in df.iterrows():
                linha = row['Arquivo']
                arquivoAnalise = Path(f"gitClones/{repo_name}/{linha}")

                importsEncontrados = []

                try:
                    # Detecta automaticamente a codificação
                    detected = from_path(arquivoAnalise).best()
                    if not detected:
                        raise UnicodeError("Não foi possível detectar a codificação.")
                    encoding_detectada = detected.encoding

                    with open(arquivoAnalise, 'r', encoding=encoding_detectada, errors='ignore') as arquivo:
                        for line in arquivo:
                            linha_limpa = line.strip()

                            # ignora comentários
                            if linha_limpa.startswith(("//", "/*", "*", "#")):
                                continue

                            # captura imports Python, Java, C/C++, e C#
                            if linha_limpa.startswith(("import ", "from ", "using ", "#include ", "include ")):
                                importsEncontrados.append(linha_limpa)

                except FileNotFoundError:
                    print(f"[AVISO] Arquivo não encontrado: {arquivoAnalise}")
                    importsEncontrados = ["ARQUIVO NAO ENCONTRADO"]

                except Exception as e:
                    print(f"[ERRO] Falha ao processar {arquivoAnalise}: {e}")
                    importsEncontrados = ["ERRO AO LER ARQUIVO"]

                df.at[index, 'Imports'] = '\n'.join(importsEncontrados)

            df.to_excel(tabela_path, index=False)


        

