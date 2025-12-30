from tqdm import tqdm
import ipaddress
import gc

STANDARD_SERVICES = {
    "80": "HTTP",
    "443": "HTTPS",
    "22": "SSH",
    "21": "FTP",
    "53": "DNS",
    "4242": "Custom-Service-4242"
}

def analyse_line(connexions: dict, line: dict, interfaces_key: tuple) -> dict:
    """
    Analyse une ligne de log et met à jour le dictionnaire des connexions.

    Args:
        connexions (dict): Le dictionnaire des connexions en cours.
        line (dict): La ligne de log à analyser.
        interfaces_key (str): La clé représentant les interfaces source et destination.

    Returns:
        dict: Le dictionnaire mis à jour.
    """
    
    subnet = ""
    
    srcip = line.get("srcip")
    if not srcip:
        return connexions # Si pas d'IP source, on ne fait rien

    try:
        subnet = ipaddress.IPv4Network(f"{srcip}/24", strict=False) # Je crée un subnet /24 à partir de l'IP source
    except ValueError:
        print(f"Invalid IP address found: {srcip}. Skipping this entry.")
        return connexions


    if connexions[interfaces_key].get(str(subnet)): # Si une connexion pour ce subnet existe déjà

        if connexions[interfaces_key][str(subnet)].get(line.get("dstip")): # Si une connexion pour cette IP de destination existe déjà dans ce subnet

            if (line.get("service") not in connexions[interfaces_key][str(subnet)][line.get("dstip")]) and line.get("service") is not None: # Si le service n'existe pas encore dans cette IP de destination
                connexions[interfaces_key][str(subnet)][line.get("dstip")].append(line.get("service")) # Je l'ajoute à la liste des services pour cette IP de destination

        elif line.get("dstip") is not None and line.get("service") is not None: # Si l'IP de destination n'existe pas encore dans ce subnet
            connexions[interfaces_key][str(subnet)][line.get("dstip")] = [line.get("service")] # Je crée une nouvelle entrée pour cette IP de destination avec le service dans une liste

    elif line.get("dstip") is not None and line.get("service") is not None and subnet is not None: # Si le subnet n'existe pas encore
        connexions[interfaces_key][str(subnet)] = {line.get("dstip"): [line.get("service")]} # Je crée une nouvelle entrée pour ce subnet avec un dictionnaire contenant l'IP de destination et le service dans une liste
    
    return connexions # Je retourne le dictionnaire mis à jour

def regroup_connexions(data: tuple, file_path: str) -> dict:
    """
    Regroupe les connexions à partir des données lues dans le fichier.

    Args:
        data (tuple): Les données lues du fichier.
        file_path (str): Le chemin du fichier (pour l'affichage).

    Returns:
        dict: Un dictionnaire contenant les connexions regroupées.
    """

    connexions = {}

    if not len(data): # Si c'est vide
        print("No data found or error reading the file.")
        return None

    print(f"Processing your file: {file_path}:")
    for line in tqdm(data, desc="Regrouping connexions: "): #tqdm pour afficher une barre de progression parce que c'est joli et utile

        interfaces_key = str(line.get("srcintf")) + "//\\\\" + str(line.get("dstintf")) # Je crée une clé unique pour chaque paire d'interfaces en les séparant par "//\\"
                                                                                        # parce qu'on peut pas mettre de tuple en clé de dictionnaire directement
        
        if connexions.get(interfaces_key) is None: # Si la clé n'existe pas encore
            connexions[interfaces_key] = {} # Je crée un dictionnaire vide pour cette paire d'interfaces

        connexions = analyse_line(connexions, line, interfaces_key) # J'analyse la ligne et je mets à jour le dictionnaire des connexions
        
    gc.collect() # opti opti (libération mémoire)
    return connexions