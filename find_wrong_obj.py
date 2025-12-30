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
            print(f"File {input_file} not found. Please provide a valid file path.")
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
    if '-' not in port_part:
        return False
    
    if port_part.startswith("0-"):
        return True
        
    parts = port_part.split('-')
    if len(parts) >= 2:
        try:
            if abs(int(parts[1]) - int(parts[0])) > 10:
                return True
        except ValueError:
            pass
            
    return False

def process_tcp_line(current_name, line, inventory):
    """
    Analyse une ligne de configuration TCP et met à jour l'inventaire.
    
    Args:
        current_name (str): Nom de l'objet en cours.
        line (str): La ligne de configuration 'set tcp-portrange ...'.
        inventory (dict): L'inventaire global.
    """
    parts = line.split()
    if len(parts) < 3:
        return

    for port_range in parts[2:]:
        is_classed = False
        
        for each_port in port_range.split(":"):
            # Vérifie si la plage est incorrecte
            if not is_classed and is_bad_port_range(each_port):
                inventory["bad"]["tcp"][current_name] = port_range
                is_classed = True
        
        if is_classed:
            continue

        # Vérification des doublons ou ajout aux bons objets
        if port_range in inventory["good"]["tcp"].values():
            inventory["bad"]["tcp"][current_name] = port_range
        else:
            inventory["good"]["tcp"][current_name] = port_range

def process_udp_line(current_name, line, inventory):
    """
    Analyse une ligne de configuration UDP et met à jour l'inventaire.
    
    Args:
        current_name (str): Nom de l'objet en cours.
        line (str): La ligne de configuration 'set udp-portrange ...'.
        inventory (dict): L'inventaire global.
    """
    parts = line.split()
    if len(parts) < 3:
        return

    for port_range in parts[2:]:
        for each_port in port_range.split(":"):
            if is_bad_port_range(each_port):
                inventory["bad"]["udp"][current_name] = each_port
            elif each_port in inventory["good"]["udp"].values():
                inventory["bad"]["udp"][current_name] = each_port
            else:
                inventory["good"]["udp"][current_name] = each_port

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

            # Détection de la section
            if line.startswith('config firewall service custom'):
                current_section = 'svc'
            elif line.startswith('config'):
                current_section = 'else'
            elif line == 'end':
                current_section = None
                current_name = None

            # Détection du nom de l'objet
            elif line.startswith('edit ') and current_section == 'svc':
                parts = line.split('"')
                if len(parts) > 1:
                    current_name = parts[1]
            
            elif current_name and current_section == 'svc':
                # Analyse des plages de ports
                if line.startswith('set tcp-portrange'):
                    process_tcp_line(current_name, line, inventory)
                elif line.startswith('set udp-portrange'):
                    process_udp_line(current_name, line, inventory)

def wrong_services_obj(input_file, output_file="forti_objects.json"):
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
    
    # Validation du fichier d'entrée
    valid_input_file = get_valid_input_file(input_file)

    # Analyse du fichier
    parse_config_file(valid_input_file, inventory)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4)

    print("Extraction des objets forti terminée.")
    
    return inventory

if __name__ == "__main__":
    
    if len(argv) > 1:
        wrong_services_obj(argv[1])
    else:
        input_file = input("Please enter the FortiGate configuration file path: ")
        wrong_services_obj(input_file=input_file)