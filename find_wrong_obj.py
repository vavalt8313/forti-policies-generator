from sys import argv
import json


def get_valid_input_file(input_file):
    """
    Vérifie l'existence du fichier d'entrée.
    Boucle tant que le fichier n'est pas trouvé.
    
    Args:
        input_file (str): Chemin initial du fichier.
        
    Returns:
        str: Le chemin valide du fichier.
    """
    while True:
        try:
            with open(input_file, 'r', encoding='utf-8'):
                return input_file
        except FileNotFoundError:
            print(f"File {input_file} not found. Please provide the file path of a FortiGate configuration file.")
            input_file = input("Enter the FortiGate configuration file path: ")

def is_bad_port_range(port_part):
    """
    Détermine si une plage de ports est incorrecte.
    Critères : commence par 0 ou plage > 10 ports.
    
    Args:
        port_part (str): La chaîne représentant le port ou la plage (ex: "80", "100-200").
        
    Returns:
        bool: True si la plage est mauvaise, False sinon.
    """
    if '-' not in port_part: # alors c'est un port simple donc pas une plage
        return False
    
    if port_part.startswith("0-"): # c'est forcement une mauvaise plage
        return True
        
    parts = port_part.split('-') # Je découpe la plage en deux parties (port de début et port de fin de plage)
    if len(parts) >= 2:
        try:
            if abs(int(parts[1]) - int(parts[0])) > 10: # Si la plage est plus grande que 10 ports
                                                        # (j'utilise abs au cas où l'ordre est inversé)
                return True
        except ValueError:
            pass
            
    return False

def process_line(current_name, line, inventory, protocol):
    """
    Analyse une ligne de configuration TCP et met à jour l'inventaire.
    
    Args:
        current_name (str): Nom de l'objet en cours.
        line (str): La ligne de configuration 'set tcp-portrange ...'.
        inventory (dict): L'inventaire global.
        protocol (str): "tcp" ou "udp".
    """
    parts = line.split()    # Je découpe la ligne par les espaces
                            # (la liste ressemble à ['set', 'tcp-portrange', 'XX', 'YY', ...])
    if len(parts) < 3:
        return

    for port_range in parts[2:]:
        is_classed = False
        
        for each_port in port_range.split(":"):

            if not is_classed and is_bad_port_range(each_port): # Si c'est une mauvaise plage
                inventory["bad"][protocol][current_name] = port_range 
                is_classed = True # Pour ne pas reclasser plusieurs fois le même objet
        
        if is_classed:
            continue

        if port_range in inventory["good"][protocol].values(): # Si c'est un doublon d'une bonne plage
            inventory["bad"][protocol][current_name] = port_range # Je le classe en mauvais
        else:
            inventory["good"][protocol][current_name] = port_range # Sinon je le classe en bon

def parse_config_file(input_file, inventory):
    """
    Lit le fichier de configuration et extrait les objets de service.
    
    Args:
        input_file (str): Chemin du fichier.
        inventory (dict): Dictionnaire à remplir.
    """
    current_section = "else"
    current_name = None

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if line.startswith('config firewall service custom'): # Je suis dans la section des services
                current_section = 'svc'
            elif line.startswith('config'): # Pour toutes les autres sections je mets en 'else' pour les skip
                current_section = 'else'
            elif line == 'end': # Fin de section
                current_section = None
                current_name = None

            elif line.startswith('edit ') and current_section == 'svc': # Si je suis dans la section des services 
                                                                        # et que je suis sur la ligne du nom de l'objet

                parts = line.split('"') # Je découpe la ligne par rapport aux guillemets car le nom est toujours
                                        # entre guillemets et c'est les seuls guillemets de la ligne
                if len(parts) > 1:
                    current_name = parts[1] # La liste ressemble à ['edit ', 'NomDeLObjet', 'blablabla (s'il y a des trucs après)']
                                            # donc je prends l'élément 1 qui est le nom de l'objet
            
            elif current_name and current_section == 'svc': # Si j'ai un nom d'objet en cours et que je suis dans la section des services
                
                if line.startswith('set tcp-portrange'):
                    process_line(current_name, line, inventory, "tcp") # J'analyse la ligne TCP
                
                elif line.startswith('set udp-portrange'):
                    process_line(current_name, line, inventory, "udp") # J'analyse la ligne UDP

def wrong_services_obj(input_file, output_file="forti_objects_sorted_bad_good.json"):
    """
    Analyse un fichier de configuration FortiGate pour identifier les objets de service incorrects.

    Args:
        input_file (str): Le chemin du fichier de configuration.
        output_file (str): Le chemin du fichier de sortie JSON.

    Returns:
        dict: Un dictionnaire contenant l'inventaire des objets 'good' et 'bad'.
    """
    inventory = {
        "bad": {
            "tcp": {},
            "udp": {}
        },
        "good": {
            "tcp": {},
            "udp": {}
        }
    }
    
    valid_input_file = get_valid_input_file(input_file) # Je m'assure que le fichier d'entrée est valide

    parse_config_file(valid_input_file, inventory) # Je parse le fichier de configuration

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4) # J'écris l'inventaire dans le fichier de sortie

    print("Extraction des objets forti terminée.")
    
    return inventory

if __name__ == "__main__":
    
    if len(argv) > 1:
        wrong_services_obj(argv[1])
    else:
        input_file = input("Please enter the FortiGate configuration file path: ")

        wrong_services_obj(input_file=input_file)
