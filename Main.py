from userData import UserData
from Emails import Emails   
from github import Github
from CalcDOA import DOACalculator  
from Imports import Imports
from CreatePrompt import CreatePrompt
from CreateGraphics import CreateGraphics
import pandas as pd 
import json
import os


class Main:

    def curriculo(devName):
        GITHUB_TOKEN = ""
        g = Github(GITHUB_TOKEN)
        userName = devName

        user = g.get_user(userName)
        print(user)
        profilePicture = user.avatar_url
        displayName = user.name
        print(displayName)
        print(profilePicture)

        targetDev = UserData(name=user.login, email=None, photo=profilePicture)
        targetDev.makeDirs()

        targetDev.cloningRepos(GITHUB_TOKEN, userName)

        Emails.listCommits()
        Emails.catchEmails(userNamex=user.login, displayNamex=displayName)
        targetDev.email = Emails.criandoListaEmaisls(userName=user.login)
        print(f"E-mails capturados: {targetDev.email}")
        
        doa_calc = DOACalculator(base_path="gitClones", output_path="./tablesDoa")
        resultados = doa_calc.calc_doa(targetDev.email) 
        targetDev.filtroArquivos()
        
        targetDev.captureImports()
        targetDev.getLinesAddRemov(GITHUB_TOKEN)
        for repo in targetDev.linesAddRemov:
            print(f"Nome do Repositório: {repo['nome']}")
            print(f"Linhas Adicionadas: {repo['linhaAdd']}")
            print(f"Linhas Removidas: {repo['linhaRemov']}")
            print(f"Linguagem: {repo['linguagem']}")    
            print("-" * 40)

        targetDev.mainLanguage()
        print(f"Linguagem Principal: {targetDev.mainLang}")
            
        print("-" * 40)
        print(f"Nome: {targetDev.name}")
        print(f"E-mail: {targetDev.email}")
        print(f"Foto: {targetDev.photo}")
        
        Imports.SeparatesByLanguages()
        Imports.uniqueImports()
        Imports.dropStarndarLibs()

        print("-=" * 40)
        targetDev.getCommitsByLanguage(GITHUB_TOKEN)
        print("Total de Commits por Linguagem:")
        for lang_commit in targetDev.totalCommits:
            print(f"Linguagem: {lang_commit['linguagem']}, Total de Commits: {lang_commit['totalCommits']}")

        CreatePrompt.generatePrompt(targetDev.mainLang, targetDev.name)

        CreateGraphics.plotLinesByLanguage(targetDev)
        CreateGraphics.plotCommitsByLanguage(targetDev)
        CreateGraphics.plotAuthoringFiles(targetDev)

        print("\n" + "-=" * 40)
        specialization = input("Cole a linha 'Specialization' da resposta da IA: ").strip()
        skills_raw = input("Cole a linha 'Skills' da resposta da IA (separadas por vírgula): ").strip()

        dados = {
            "dev_name": targetDev.name,
            "photo": targetDev.photo,
            "email": targetDev.email[0],
            "main_language": targetDev.mainLang,
            "specialization": specialization,
            "skills": skills_raw,
        }

        dados_js = json.dumps(dados, ensure_ascii=False)

        with open("Dashboard/dados.js", "w", encoding="utf-8") as f:
            f.write(f"const dados = {dados_js};")

        Main.salvarNoExcel(
            nome=targetDev.name,
            linguagem=targetDev.mainLang,
            numArquivos=len(resultados)  
        )


    def salvarNoExcel(nome, linguagem, numArquivos, arquivo='Senioridade.xlsx'):
        nova_linha = {
            'Nome': nome,
            'Linguagem Principal': linguagem,
            'Numero Arquivos de Autoria': numArquivos
        }

        if os.path.exists(arquivo):
            df_existente = pd.read_excel(arquivo)
            df_atualizado = pd.concat(
                [df_existente, pd.DataFrame([nova_linha])],
                ignore_index=True
            )
        else:
            df_atualizado = pd.DataFrame([nova_linha])

        df_atualizado.to_excel(arquivo, index=False)
        print(f"✅ Dados de '{nome}' salvos em '{arquivo}'")



if __name__ == '__main__':
    devList = ['johnatan-si', 'enzoavalentim']

    for nome in devList:
        Main.curriculo(nome)