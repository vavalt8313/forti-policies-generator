from tqdm import tqdm
import json
import csv
import re
import gc


def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def write_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def read_csv(file_path):
    tableau_resultat = []
    
    # Explication du Regex :
    # (\w+)       -> Capture la Clé (lettres/chiffres)
    # =           -> Le signe égal
    # (?:         -> Début du groupe pour la Valeur (choix multiple)
    #   "([^"]*)" -> Choix 1 : Valeur entre guillemets (capture le contenu sans les guillemets)
    #   |         -> OU
    #   (\S+)     -> Choix 2 : N'importe quoi tant qu'il n'y a pas d'espace
    # )
    pattern = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lecteur = csv.reader(f, delimiter=",")
            for ligne in tqdm(lecteur, desc="Reading CSV lines"):
                dico_ligne = {}
                for element in ligne:
                    element = element.strip()
                    if not element:
                        continue

                    matches = pattern.findall(element)

                    if matches:
                        for cle, val_quote, val_simple in matches:
                            valeur = val_quote if val_quote else val_simple
                            dico_ligne[cle] = valeur

                if len(dico_ligne):
                    tableau_resultat.append(dico_ligne)
                
                gc.collect()

        return tableau_resultat

    except Exception as e:
        print(f"Erreur lors de la lecture : {e}")
        return []

def determine_type_file(file_path: str) -> tuple:
    """***Read the filepath, read the file with the good method and return a tuple of the content line by line***.
    
    **Keyword arguments:** 
    file_path -- *The path to the file to read*.
    
    **Return:** *A tuple containing the content of the file*.
    """

    if file_path.endswith('.json'):
        return tuple(load_json(file_path))

    elif file_path.endswith('.csv'):
        return tuple(read_csv(file_path))

    else:
        return tuple(read_file(file_path))
