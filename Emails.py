import os
import pandas as pd
from git import Repo 
from rapidfuzz import fuzz
import pandas as pd
import os
import shutil

class Emails:

    def __init__(self):
        self.emails = None

    def listCommits():
     
        caminho_base = f"gitClones" 

        CLONE_DIR = "tablesEmails"
            
        if os.path.exists(CLONE_DIR):
            shutil.rmtree(CLONE_DIR)
        os.makedirs(CLONE_DIR, exist_ok=True)


        repositorios = [
            os.path.join(caminho_base, d)
            for d in os.listdir(caminho_base)
            if os.path.isdir(os.path.join(caminho_base, d))
        ]

        for repo_path in repositorios:
            try:
                repo = Repo(repo_path)
                commits_data = []

                for commit in repo.iter_commits():
                    commits_data.append({
                        "hash": commit.hexsha,
                        "autor_nome": commit.author.name,
                        "autor_email": commit.author.email
                    })

                df = pd.DataFrame(commits_data)

                
                nome_repo = os.path.basename(repo_path)
                arquivo_saida = os.path.join('./tablesEmails', f"{nome_repo}_commits.csv")
                df.to_csv(arquivo_saida, index=False, encoding="utf-8")

            except Exception as e:
                print(f"[ERRO] Não foi possível processar {repo_path}: {e}")

    def catchEmails(userNamex, displayNamex): 


        userName = userNamex.lower()  #base1
        displayName = displayNamex.lower() #base2


        pasta = 'tablesEmails'


        arquivos = [f for f in os.listdir(pasta) if f.endswith('.csv')]


        linhas_filtradas = []

        for arquivo in arquivos:
            caminho_arquivo = os.path.join(pasta, arquivo)
            df = pd.read_csv(caminho_arquivo)
            
            for index, linha in df.iterrows():
                try:
                    commitEmail = linha.get('autor_email', "")
                    commitName = linha.get('autor_nome', "")


                    if not isinstance(commitEmail, str):
                        commitEmail = ""
                    else:
                        commitEmail = commitEmail.lower()

                    if not isinstance(commitName, str):
                        commitName = ""
                    else:
                        commitName = commitName.lower()

                    score_userNameXEmail = fuzz.ratio(userName, commitEmail)
                    score_userNameXCommitName = fuzz.ratio(userName, commitName)
                    score_displayNameXEmail = fuzz.ratio(displayName, commitEmail)
                    score_displayNameXCommitName = fuzz.ratio(displayName, commitName)
                    
                    if score_userNameXCommitName >= 72.0:
                        linhas_filtradas.append(linha)

                    
                    if score_displayNameXCommitName >= 70.89:
                        linhas_filtradas.append(linha)

                except Exception as e:
                    print(f"[ERRO] Linha {index} do arquivo {arquivo} não pôde ser processada: {e}")

        df_filtrado = pd.DataFrame(linhas_filtradas)

        df_filtrado.to_csv(f'emails{userName}.csv', index=False)

        if os.path.exists('tablesEmails'):
            shutil.rmtree('tablesEmails')

    def criandoListaEmaisls(userName): 

        df = pd.read_csv(f"emails{userName}.csv")
        emailsUniicos = df["autor_email"].unique().tolist()
        os.remove(f"emails{userName}.csv")
        return emailsUniicos