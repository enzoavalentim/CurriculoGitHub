import requests
from github import Github
from collections import Counter, defaultdict
from pydriller import Repository
from pydriller.metrics.process.lines_count import LinesCount
import os
from openpyxl import Workbook
import math
from datetime import datetime
from git import Repo
from pathlib import Path
import pandas as pd
from datetime import datetime
    
class DOACalculator:

    def __init__(self, base_path="gitClones", output_path="./tablesDoa", min_lines_threshold=5, max_files_per_commit=20):
        self.base_path = base_path
        self.output_path = output_path
        self.min_lines_threshold = min_lines_threshold    # Mínimo de linhas alteradas para considerar autoria
        self.max_files_per_commit = max_files_per_commit  # Limite de arquivos alterados para identificar commits de geração automática 

    def get_repositories(self):
        """Retorna os caminhos dos repositórios clonados."""
        repositorios = [
            os.path.join(self.base_path, d)
            for d in os.listdir(self.base_path)
            if os.path.isdir(os.path.join(self.base_path, d))
        ]
        return repositorios

    def get_commits_by_file(self, repo_path):
        """Retorna um dicionário {arquivo: commits_info[]}."""
        try:
            repo = Repo(repo_path)
        except Exception as e:
            print(f"Erro ao abrir o repositório em {repo_path}: {e}")
            return {}
        

        print(f"Analisando repositório: {repo_path}")
        commits = list(repo.iter_commits())
        arquivoCommits = defaultdict(list)
        arquivos_vistos = set()  

        for commit in reversed(commits):
            author_name = commit.author.name
            author_email = commit.author.email
            commit_date = datetime.fromtimestamp(commit.committed_date)

            extensoes_validas = (".java", ".py", ".js", ".cs", ".c", ".cpp")

            # Conta quantos arquivos válidos esse commit toca
            arquivos_validos_no_commit = [f for f in commit.stats.files if f.endswith(extensoes_validas)]
            is_bulk_commit = len(arquivos_validos_no_commit) > self.max_files_per_commit

            for file, stats in commit.stats.files.items():
                if file.endswith(extensoes_validas):
                    is_creation_commit = file not in arquivos_vistos
                    arquivos_vistos.add(file)

                    arquivoCommits[file].append({
                        'commit': commit,
                        'autor_nome': author_name,
                        'autor_login': author_email,
                        'data': commit_date,
                        'linhas_alteradas': stats['lines'],
                        'is_creation_commit': is_creation_commit,
                        'is_bulk_commit': is_bulk_commit 
                    })
        return arquivoCommits

    def calculate_dev_stats(self, commits_info):
        """Calcula FA, DL, AC para cada dev de um arquivo."""
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

        return dev_stats

    def calculate_doa(self, dev_stats):
        """Calcula o DOA para cada dev de um arquivo."""
        dev_doa = {}
        for dev, stats in dev_stats.items():
            FA = stats['FA']
            DL = stats['DL']
            AC = stats['AC']
            doa = 3.293 + 1.098 * FA + 0.164 * DL - 0.321 * math.log(1 + AC)
            dev_doa[dev] = doa
        return dev_doa

    def get_lines_per_dev(self, commits_info):
        """Retorna o total de linhas alteradas por dev em um arquivo,
        excluindo commits de geração automática (bulk commits) da contagem."""
        linhas_por_dev = defaultdict(int)

        for commit_info in commits_info:
            autor = commit_info['autor_login']

            if not commit_info['is_bulk_commit']:
                linhas_por_dev[autor] += commit_info['linhas_alteradas']

        return linhas_por_dev

    def get_principal_author_files(self, arquivoCommits, dev_emails):
        """Retorna os arquivos em que algum dos e-mails é autor principal."""
        arquivosAutoriaAlvo = []

        for arquivo, commits_info in arquivoCommits.items():
            dev_stats = self.calculate_dev_stats(commits_info)
            dev_doa = self.calculate_doa(dev_stats)
            linhas_por_dev = self.get_lines_per_dev(commits_info) 

            doa_max = max(dev_doa.values())
            doa_normalizado = {dev: val / doa_max for dev, val in dev_doa.items()}

            for email in dev_emails:
                if email in dev_doa:
                    # filtro: linhas contadas apenas em commits que não sejam bulk (geração automática)
                    if linhas_por_dev[email] < self.min_lines_threshold:
                        continue

                    if (
                        dev_doa[email] == doa_max and
                        dev_doa[email] >= 3.293 and
                        doa_normalizado[email] >= 0.75
                    ):
                        arquivosAutoriaAlvo.append(arquivo)
                        break

        return arquivosAutoriaAlvo

    def save_to_excel(self, repo_name, arquivos):

        if not arquivos:
            return False

        wb = Workbook()
        ws = wb.active
        ws.title = "Arquivos DOA"
        ws.append(["Arquivo"])

        for arq in arquivos:
            ws.append([arq])

        nome_arquivo = f"{repo_name}.xlsx"
        caminho_saida = os.path.join(self.output_path, nome_arquivo)
        os.makedirs(self.output_path, exist_ok=True)
        wb.save(caminho_saida)
        #print(f"Arquivo Excel criado: {caminho_saida}")
        return True

    def calc_doa(self, dev_email):
        """Fluxo principal: percorre repositórios, calcula DOA e salva resultados."""
        repositorios = self.get_repositories()
        resultados = {}
        repoAnalisado = 0

        for repo_path in repositorios:
            arquivoCommits = self.get_commits_by_file(repo_path)
            arquivosAutoriaAlvo = self.get_principal_author_files(arquivoCommits, dev_email)

            nome_repo = os.path.basename(repo_path)
            resultados[nome_repo] = arquivosAutoriaAlvo

            if self.save_to_excel(nome_repo, arquivosAutoriaAlvo):
                repoAnalisado += 1
            #else:
                #print(f"Nenhum arquivo de autoria principal para {dev_email} no repositório {nome_repo}.")


        print(f"Total de repositórios analisados com arquivos de autoria principal: {repoAnalisado}/{len(resultados)}")
        return resultados