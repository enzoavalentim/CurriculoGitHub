import os
import pandas as pd
from git import Repo 
from rapidfuzz import fuzz
import pandas as pd
import os
import shutil

class Emails:

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

                print(f"[OK] Extraído {len(df)} commits de {nome_repo}")

            except Exception as e:
                print(f"[ERRO] Não foi possível processar {repo_path}: {e}")