import os
import shutil
from pathlib import Path
import pandas as pd

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

    @staticmethod
    def uniqueImports():
 
        folder = Path('importTables')
        
        for arquivo_path in folder.iterdir():
            if arquivo_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(arquivo_path)
                
                if 'Imports' in df.columns:
                    df = df[df['Imports'].notna()]        
                    df = df[df['Imports'].str.strip() != '']  
                    df = df.drop_duplicates(subset=['Imports']).reset_index(drop=True)

                    df['Imports'] = df['Imports'].str.replace('import','').str.strip()
                    df['Imports'] = df['Imports'].str.replace('#import','').str.strip()
                    df['Imports'] = df['Imports'].str.replace('using','').str.strip()

                    df.to_excel(arquivo_path, index=False)
                    print(f"Arquivo processado: {arquivo_path.name}")

                else:
                    print(f"A coluna 'Imports' não existe em {arquivo_path.name}")

    @staticmethod
    def dropStarndarLibs():

        python = pd.read_excel("importTables/Python.xlsx") #Coluna X
        java = pd.read_excel("importTables/Java.xlsx")
        javascript = pd.read_excel("importTables/JavaScript.xlsx")
        c = pd.read_excel("importTables/C.xlsx")
        cpp = pd.read_excel("importTables/CPP.xlsx")
        cs = pd.read_excel("importTables/CS.xlsx") 
      

        pythonStdLibs = pd.read_csv("standardLibs/standardLibsPython.csv") #Coluna Y
        cStdLibs = pd.read_csv("standardLibs/standardLibsC.csv") #Coluna Y
        cppStdLibs = pd.read_csv("standardLibs/standardLibsCPP.csv") #Coluna Y
        csStdLibs = pd.read_csv("standardLibs/standardLibsCS.csv") #Coluna Y


        #Python
        dfFiltradoPython = python[~python['Imports'].isin(pythonStdLibs['Imports'])]
        dfFiltradoPython.to_excel('importTables/Python.xlsx', index=False)

        #Java
        prefixosPadrao = ('java.', 'javax.', 'jdk.')
        dfFiltradoJava = java[~java['Imports'].str.startswith(prefixosPadrao)]    
        dfFiltradoJava.to_excel('importTables/Java.xlsx', index=False)

        #JavaScript
        #Bibliotecas padrão estão “embutidas” no ambiente de execução

        #C
        dfFiltradoC = c[~c['Imports'].isin(cStdLibs['Imports'])]
        dfFiltradoC.to_excel('importTables/C.xlsx', index=False)

        #C++
        dfFiltradoCPP = cpp[~cpp['Imports'].isin(cppStdLibs['Imports'])]
        dfFiltradoCPP.to_excel('importTables/CPP.xlsx', index=False)

        #C#
        dfFiltradoCs = cs[~cs['Imports'].isin(csStdLibs['Imports'])]
        dfFiltradoCs.to_excel('importTables/CS.xlsx', index=False)

        print("Linhas removidas com sucesso!")
