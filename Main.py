from userData import UserData
from Emails import Emails   
from github import Github
from CalcDOA import DOACalculator  

class Main:

    GITHUB_TOKEN = ""
    g = Github(GITHUB_TOKEN)
    userName = 'johnatan-si'


    user = g.get_user(userName)
    print(user)
    profilePicture = user.avatar_url
    displayName = user.name
    print(displayName)

    targetDev = UserData(name=user.login, email=None, photo=profilePicture)

    targetDev.cloningRepos(GITHUB_TOKEN, userName)

    Emails.listCommits()
    Emails.catchEmails(userNamex=user.login, displayNamex=displayName)
    targetDev.email = Emails.criandoListaEmaisls(userName=user.login)
    print(f"E-mails capturados: {targetDev.email}")
    
    doa_calc = DOACalculator(base_path="gitClones", output_path="./tablesDoa")
    resultados = doa_calc.calc_doa(targetDev.email)   
    targetDev.filtroArquivos()
    
    targetDev.captureImports()
    targetDev.getLinesAddRemov()
    for repo in targetDev.linesAddRemov:
        print(f"Nome do Repositório: {repo['nome']}")
        print(f"Linhas Adicionadas: {repo['linhaAdd']}")
        print(f"Linhas Removidas: {repo['linhaRemov']}")
        print("-" * 40)
        
    print("-" * 40)
    print(f"Nome: {targetDev.name}")
    print(f"E-mail: {targetDev.email}")
    print(f"Foto: {targetDev.photo}")
    

    


    

    
    
