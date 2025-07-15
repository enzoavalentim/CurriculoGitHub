from userData import UserData

from github import Github
from collections import Counter, defaultdict
from pydriller import Repository
import os
import git  
import shutil
import matplotlib.pyplot as plt
import os

class Main:

    GITHUB_TOKEN = ""
    g = Github(GITHUB_TOKEN)
    userName = 'johnatan-si'
    user = g.get_user(userName)
    profilePicture = user.avatar_url
    email = UserData.getEmail(userName=user.login, GitToken=GITHUB_TOKEN)

    TargetDev = UserData( name=user.login, email=email or "email@nao-encontrado.com", photo=profilePicture)
    TargetDev.cloningRepos(GITHUB_TOKEN, userName)
    

    #print(f"Nome: {targetDev.name}")
    #print(f"E-mail: {targetDev.email}")
    #print(f"Foto: {targetDev.photo}")

    
    
