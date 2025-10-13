import os
import shutil
from pathlib import Path
import pandas as pd
import csv 

class Imports:

    @staticmethod
    def SeparatesByLanguages():

        if os.path.exists("importTables"):
            shutil.rmtree("importTables")
        os.makedirs("importTables", exist_ok=True)

        tabelaJava = pd.DataFrame(columns=['Imports'])
        tabelaPython = pd.DataFrame(columns=['Imports'])
        tabelaJavaScript = pd.DataFrame(columns=['Imports'])
        tabelaC = pd.DataFrame(columns=['Imports'])
        tabelaCPP = pd.DataFrame(columns=['Imports'])
        tabelaCS = pd.DataFrame(columns=['Imports'])

        folderPath = Path("./tablesDoa")

        for tabela_path in folderPath.iterdir():
            df = pd.read_excel(tabela_path)


            df['Imports'] = df['Imports'].fillna('').astype(str).str.split('\n')
            df_exploded = df.explode('Imports').reset_index(drop=True)

            for index, row in df_exploded.iterrows():
                imports = row['Imports']
                arquivo = row['Arquivo']
                
                if arquivo.endswith('.java'):
                    tabelaJava = pd.concat([tabelaJava, pd.DataFrame({'Imports':[imports]})], ignore_index=True)
                elif arquivo.endswith('.py'):
                    tabelaPython = pd.concat([tabelaPython, pd.DataFrame({'Imports':[imports]})], ignore_index=True)
                elif arquivo.endswith('.js'):
                    tabelaJavaScript = pd.concat([tabelaJavaScript, pd.DataFrame({'Imports':[imports]})], ignore_index=True)
                elif arquivo.endswith('.c'):
                    tabelaC = pd.concat([tabelaC, pd.DataFrame({'Imports':[imports]})], ignore_index=True)
                elif arquivo.endswith('.cpp'):
                    tabelaCPP = pd.concat([tabelaCPP, pd.DataFrame({'Imports':[imports]})], ignore_index=True)
                elif arquivo.endswith('.cs'):
                    tabelaCS = pd.concat([tabelaCS, pd.DataFrame({'Imports':[imports]})], ignore_index=True)

        tabelaJava.to_excel("importTables/Java.xlsx", index=False)
        tabelaPython.to_excel("importTables/Python.xlsx", index=False)
        tabelaJavaScript.to_excel("importTables/JavaScript.xlsx", index=False)
        tabelaC.to_excel("importTables/C.xlsx", index=False)
        tabelaCPP.to_excel("importTables/CPP.xlsx", index=False)
        tabelaCS.to_excel("importTables/CS.xlsx", index=False)

        
