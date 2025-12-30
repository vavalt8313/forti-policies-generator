from tqdm import tqdm
import json
import csv
import re
import gc


def read_file(file_path):
    """Lit un fichier texte ligne par ligne."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def write_file(file_path, data):
    """Écrit des données dans un fichier."""
    with open(file_path, 'w') as file:
        file.write(data)

def load_json(file_path):
    """Charge des données depuis un fichier JSON."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    """Sauvegarde des données dans un fichier JSON."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def read_csv(file_path):
    """
    Lit un fichier CSV (format logs) et extrait les paires clé-valeur.
    Gère les valeurs entre guillemets via Regex.
    """
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
            lecteur = csv.reader(f, delimiter=",") # Lecture du CSV avec comme séparateur des virgules

            for ligne in tqdm(lecteur, desc="Reading CSV lines"): #tqdm c'est une fonction qui affiche une barre de progression dans le for pour savoir où on en est
                dico_ligne = {}
                for element in ligne:
                    element = element.strip() # Nettoyage des espaces inutiles
                    if not element:
                        continue # Je skip si l'élément est vide

                    matches = pattern.findall(element) # Trouve toutes les correspondances du regex dans l'élément

                    if matches:
                        for cle, val_quote, val_simple in matches: # Pour chaque correspondance trouvée
                            valeur = val_quote if val_quote else val_simple # Je regarde si il trouve une valeur entre guillemets et 
                                                                            # si cette valeur est nulle je prends tout ce qui est apres le = comme valeur
                            dico_ligne[cle] = valeur

                if len(dico_ligne): # Si la ligne n'est pas vide
                    tableau_resultat.append(dico_ligne) # Je l'ajoute au tableau
                
        gc.collect() # opti opti (libération mémoire)

        return tableau_resultat

    except Exception as e:
        print(f"Erreur lors de la lecture : {e}")
        return []

def determine_type_file(file_path: str) -> tuple: # Je retourne un tuple pour faire plaisir à Thibaud
    """
    Détermine le type de fichier et utilise la méthode de lecture appropriée.

    Args:
        file_path (str): Le chemin du fichier à lire.

    Returns:
        tuple: Un tuple contenant le contenu du fichier.
    """

    if file_path.endswith('.json'):
        return tuple(load_json(file_path))

    elif file_path.endswith('.csv'):
        return tuple(read_csv(file_path))

    else:
        return tuple(read_file(file_path))
