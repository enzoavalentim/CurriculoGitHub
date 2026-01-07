from userData import UserData
from Emails import Emails   
from github import Github
from CalcDOA import DOACalculator  
from Imports import Imports

import pandas as pd


class CreatePrompt:

    @staticmethod
    def generatePrompt(mainLang, name):
            
            file_path = f"./importTables/{mainLang}.xlsx"
            df = pd.read_excel(file_path)

            imports_list = df["Imports"].dropna().astype(str).tolist()
            imports_text = "\n".join(imports_list)

            prompt = f"""Analyze the following libraries and determine developer specialization, providing a concise and categorized answer.
It is essential that in the specialization line the developer is classified as one of the following:
Front-end Developer, Back-end Developer, Full-stack Developer, Data Scientist, Data Engineer,
Machine Learning Engineer, Mobile Developer, DevOps Engineer, Cloud Engineer, Security Engineer,
Application Security Engineer, Game Developer, Embedded Systems Developer, AR/VR Developer or Blockchain Developer.

Disregard Java standard libraries and words like 'NAO ENCONTRADO'.

Libraries:
***
{imports_text}
***

Response format:

Specialization: Back-end Developer
Skills: search algorithms, APIs, databases
"""
            with open(f"{name}-prompt.txt", "w", encoding="utf-8") as file:
                file.write(prompt)
            return 
    
