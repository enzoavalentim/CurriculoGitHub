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

    targetDev = UserData(name=user.login, email=None, photo=profilePicture)
    targetDev.getEmail(userName=user.login, GitToken=GITHUB_TOKEN)

    print(f"Nome: {targetDev.name}")
    print(f"E-mail: {targetDev.email}")
    print(f"Foto: {targetDev.photo}")


    #TargetDev.cloningRepos(GITHUB_TOKEN, userName)
    

    
    
