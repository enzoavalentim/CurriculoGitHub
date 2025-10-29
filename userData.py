import requests
from github import Github
from collections import Counter, defaultdict
from pydriller import Repository
from pydriller.metrics.process.lines_count import LinesCount
import os
import git
import shutil
from openpyxl import Workbook
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
        self.mainLang = None

    def getLinesAddRemov(self, github_token: str):
        listaRepos = self.createRepoList(username=self.name, github_token=github_token)

        for repo_dict in listaRepos:
            repoPath = f"./gitClones/{repo_dict['nome']}"
            linhas_adicionadas = 0
            linhas_removidas = 0

            try:
                    for commit in Repository(repoPath).traverse_commits():
                        if commit.author.email in self.email:
                                linhas_adicionadas += commit.insertions
                                linhas_removidas += commit.deletions
   
                    repo_dict['linhaAdd'] = linhas_adicionadas
                    repo_dict['linhaRemov'] = linhas_removidas

            except Exception as e:
                    print(f"Erro ao abrir o repositório em {repoPath}: {e}")

        self.linesAddRemov = listaRepos

    
    @staticmethod
    def createRepoList(username, github_token):

        repoPath = "./gitClones"
        lista_repositorios = []


        g = Github(github_token)
        user = g.get_user(username)

        allowedLanguages = {'Java', 'JavaScript', 'Python', 'C', 'C++', 'C#'}

        repo_names = set() 

        for repo in user.get_repos():
            try:
                language = repo.language or "Unknown"
                if language in allowedLanguages and repo.name not in repo_names:
                    repo_info = {
                        'nome': repo.name,
                        'linhaAdd': None,
                        'linhaRemov': None,
                        'linguagem': language
                    }
                    lista_repositorios.append(repo_info)
                    repo_names.add(repo.name)
            except Exception as e:
                print(f"❌ Failed to process {repo.name}: {e}")


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
                    detected = from_path(arquivoAnalise).best()
                    if not detected:
                        raise UnicodeError("Não foi possível detectar a codificação.")
                    encoding_detectada = detected.encoding

                    with open(arquivoAnalise, 'r', encoding=encoding_detectada, errors='ignore') as arquivo:
                        for line in arquivo:
                            linha_limpa = line.strip()
                            if linha_limpa.startswith(("//", "/*", "*", "#")):
                                continue

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

    def mainLanguage(self):
        #Definindo linguagem principal com base em em numero de arquivos de autoria em cada linguagem 

        Java = 0
        Python = 0
        JavaScript = 0
        C = 0       
        Cpp = 0
        CSharp = 0

        folderPath = Path("./tablesDoa")

        for tabela_path in folderPath.iterdir():
            if not tabela_path.name.endswith((".xlsx", ".xls")):
                continue

            df = pd.read_excel(tabela_path)
            df['Imports'] = ""

            for index, row in df.iterrows():
                linha = row['Arquivo']
                
                if linha.endswith('.java'):
                    Java += 1
                elif linha.endswith('.py'):
                    Python += 1
                elif linha.endswith('.js'):
                    JavaScript += 1
                elif linha.endswith('.c'):
                    C += 1
                elif linha.endswith('.cpp'):
                    Cpp += 1
                elif linha.endswith('.cs'):
                    CSharp += 1

        print(f"Contagem de arquivos por linguagem:")
        print(f"Java: {Java}")
        print(f"Python: {Python}")      
        print(f"JavaScript: {JavaScript}")
        print(f"C: {C}")
        print(f"C++: {Cpp}")
        print(f"C#: {CSharp}")
        
        listaLang = {
            'Java': Java,
            'Python': Python,
            'JavaScript': JavaScript,
            'C': C,
            'C++': Cpp,
            'C#': CSharp
        }
        mainLang = max(listaLang, key=listaLang.get)
        self.mainLang = mainLang
        return

        
