import json


def get_forti_objects(input_file, output_file="forti_objects.json"):
    inventory = {}

    current_section = None
    current_name = None

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if line.startswith('config firewall address'):
                current_section = 'addr'
            elif line.startswith('config'):
                current_section = 'else'
            elif line == 'end':
                current_section = None
                current_name = None

            elif line.startswith('edit ') and current_section == 'addr':
                parts = line.split('"')
                if len(parts) > 1:
                    current_name = parts[1]

            elif current_name and current_section == 'addr':
                
                if current_section == 'addr' and line.startswith('set subnet'):
                    parts = line.split() 
                    if len(parts) >= 3:
                        inventory[parts[2]] = current_name

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4)

    print("Extraction des objets forti terminée.")
    
    return inventory