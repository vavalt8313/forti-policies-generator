from sys import argv
import json


def wrong_services_obj(input_file, output_file=f"forti_objects.json"):
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

    current_section = "else"
    current_name = None
    
    while True:
        try:
            f = open(input_file, 'r', encoding='utf-8')
            f.close()
            break
        except FileNotFoundError:
            print(f"File {input_file} not found. Please provide a valid file path.")
            input_file = input("Enter the FortiGate configuration file path: ")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if line.startswith('config firewall service custom'):
                current_section = 'svc'
            elif line.startswith('config'):
                current_section = 'else'
            elif line == 'end':
                current_section = None
                current_name = None

            elif line.startswith('edit ') and current_section == 'svc':
                parts = line.split('"')
                if len(parts) > 1:
                    current_name = parts[1]
            
            elif current_name and current_section == 'svc':
                
                if current_section == 'svc' and line.startswith('set tcp-portrange'):
                    parts = line.split()
                    if len(parts) >= 3:
                        for port_range in parts[2:]:
                            is_classed = False
                            
                            for each_port in port_range.split(":"):
                                splited_port = each_port.split('-')
                                if not is_classed and '-' in each_port and (each_port.startswith("0-") or abs(int(splited_port[1]) - int(splited_port[0])) > 10):
                                    inventory["bad"]["tcp"][current_name] = port_range
                                    is_classed = True
                            
                            if is_classed:
                                continue

                            if port_range in inventory["good"]["tcp"].values():
                                inventory["bad"]["tcp"][current_name] = port_range
                            else:
                                inventory["good"]["tcp"][current_name] = port_range
                
                elif current_section == 'svc' and line.startswith('set udp-portrange'):
                    parts = line.split()
                    if len(parts) >= 3:
                        for port_range in parts[2:]:
                            for each_port in port_range.split(":"):
                                splited_port = each_port.split('-')
                                if '-' in each_port and (each_port.startswith("0-") or abs(int(splited_port[1]) - int(splited_port[0])) > 10):
                                    inventory["bad"]["udp"][current_name] = each_port
                                elif each_port in inventory["good"]["udp"].values():
                                    inventory["bad"]["udp"][current_name] = each_port
                                else:
                                    inventory["good"]["udp"][current_name] = each_port

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4)

    print("Extraction des objets forti terminée.")
    
    return inventory

if __name__ == "__main__":
    
    if len(argv) > 1:
        wrong_services_obj(argv[1])
    else:
        wrong_services_obj("forti_config.txt")