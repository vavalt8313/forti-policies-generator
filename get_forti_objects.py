import json
import gc


def get_forti_objects(input_file, output_file="forti_objects.json"):
    """
    Extrait les objets d'adresse d'un fichier de configuration FortiGate.

    Args:
        input_file (str): Le chemin du fichier de configuration.
        output_file (str): Le chemin du fichier de sortie JSON.

    Returns:
        dict: Un dictionnaire mappant les sous-réseaux aux noms d'objets.
    """
    inventory = {}

    current_section = None
    current_name = None
    
    # Récupération du fichier de configuration FortiGate si necessaire
    
    try:
        f = open(input_file, 'r', encoding='utf-8') # Test si le fichier existe
        f.close() # Si oui je le ferme tout de suite (opti opti)
    except FileNotFoundError:
        input_file = input("Config FortiGate file not found. Please provide the correct file path or type 'no' to skip: ")
        if not input_file or input_file.lower() == 'no':
            print("No file path provided. Giving up on Forti object extraction.")
            gc.collect() # opti opti (libération mémoire)
            return inventory
        try:
            f = open(input_file, 'r', encoding='utf-8')
            f.close()
        except FileNotFoundError:
            print("File not found. Giving up on Forti object extraction")
            gc.collect() # opti opti (libération mémoire)
            return inventory


    # Extraction des objets d'adresse du fichier de configuration

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip() # Nettoyage des espaces inutiles

            if line.startswith('config firewall address'): # Détection de la section des objets d'adresse pour récupérer les noms des adresses ip
                current_section = 'addr'
            elif line.startswith('config'): # Pour toutes les autres sections je mets en 'else' car elles ne m'intéressent pas
                current_section = 'else'
            elif line == 'end': # Fin de section
                current_section = None
                current_name = None

            elif line.startswith('edit ') and current_section == 'addr': # Si je suis dans la section des adresses et que je suis sur la ligne du nom de l'objet
                parts = line.split('"') # Je découpe la ligne par rapport aux guillemets car le nom est toujours entre guillemets et c'est les seuls guillemets de la ligne
                if len(parts) > 1:
                    current_name = parts[1] # La liste ressemble à ['edit ', 'NomDeLObjet', 'blablabla (s'il y a des trucs après)'] donc je prends l'élément 1 qui est le nom de l'objet

            elif current_name and current_section == 'addr': # Si j'ai un nom d'objet en cours et que je suis dans la section des adresses
                if line.startswith('set subnet'): # Je cherche la ligne qui contient l'adresse ip
                    parts = line.split() # Je découpe la ligne par les espaces
                    if len(parts) >= 3:
                        inventory[parts[2]] = current_name  # La ligne ressemble à ['set', 'subnet', 'AdresseIP'] donc je prends
                                                            # l'élément 2 qui est l'adresse ip et je le stocke dans le dictionnaire avec le nom de l'objet

    with open(output_file, 'w', encoding='utf-8') as f: 
        json.dump(inventory, f, indent=4) # J'enregistre le dictionnaire dans un fichier JSON pour le verifier plus tard si besoin (optionnel)

    print("Forti objects extraction completed.")
    
    gc.collect() # opti opti (libération mémoire)
    
    return inventory