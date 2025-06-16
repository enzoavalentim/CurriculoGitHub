from git import Repo
from collections import defaultdict
import math
from datetime import datetime

caminhoRepo = "./gitClones/Android-MaterialRefreshLayout"  
devAlvo = "929178101@qq.com"

repo = Repo(caminhoRepo)
commits = list(repo.iter_commits()) # Obtém todos os commits do repositório
arquivoCommits = defaultdict(list) #Armazena todos os arquivos de um determinado repositório, com seus commits e informações de cada commit


for commit in reversed(commits):
    author_name = commit.author.name
    author_email = commit.author.email  # Já existe no código original
    commit_date = datetime.fromtimestamp(commit.committed_date)

    for file in commit.stats.files:
        arquivoCommits[file].append({
            'commit': commit,
            'autor_nome': author_name,
            'autor_login': author_email,  # Alterado para usar o e-mail
            'data': commit_date
        })


arquivosAutoriaAlvo = [] # Lista para armazenar os arquivos onde o devAlvo é o principal autor

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

    if devAlvo in dev_doa:
        if (
            dev_doa[devAlvo] == doa_max and
            dev_doa[devAlvo] >= 3.293 and
            doa_normalizado[devAlvo] >= 0.75
        ):
            arquivosAutoriaAlvo.append(arquivo)

print("Arquivos de autoria principal de", devAlvo)
for arq in arquivosAutoriaAlvo:
    print(arq)
