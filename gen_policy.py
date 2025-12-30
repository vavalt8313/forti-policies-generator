from get_forti_objects import get_forti_objects
from determine_services_or_ip import determine_services_or_ip
from determine_type import write_file
import ipaddress

STANDARD_SERVICES = {
    "80": "HTTP",
    "443": "HTTPS",
    "22": "SSH",
    "21": "FTP",
    "53": "DNS",
    "67": "DHCP",
    "68": "DHCP",
    "123": "NTP",
    "135": "DCE-RPC",
    "161": "SNMP",
    "162": "SNMP",
    "389": "LDAP",
    "445": "SMB",
    "514": "SYSLOG",
    "3389": "RDP"
}

unique_addresses = set()
unique_custom_services = set()

def get_netmask(ip_string):
    """Convertit 10.0.0.0/24 en '10.0.0.0 255.255.255.0'"""
    try:
        if "/" in ip_string:
            net = ipaddress.IPv4Network(ip_string, strict=False)
            return f"{net.network_address} {net.netmask}"
        else:
            return f"{ip_string} 255.255.255.255"
    except ValueError:
        return f"{ip_string} 255.255.255.255"

def gen_policy(data, forti_objects_file="FW_objects.txt"):
    """
    Génère la configuration Fortinet à partir des données agrégées.

    Args:
        data (dict): Les données de connexion regroupées.
        forti_objects_file (str): Le fichier contenant les objets Fortinet existants. Le nom par défaut est "FW_objects.txt" mais si il ne le trouve pas il demandera à l'utilisateur le bon nom.

    Returns:
        str: La configuration générée.
    """

    output = []
    forti_objects = get_forti_objects(forti_objects_file) # Récupère les objets Forti existants depuis le fichier fourni
    sorted_data = determine_services_or_ip(data) # Détermine si on groupe par services ou par IP et me le retourne dans un dictionnaire

    # Collecte des adresses uniques pour la création d'objets
    for interfaces_key, connexion in data.items():
        for src_subnet, destinations in connexion.items():
            unique_addresses.add(src_subnet) # Ajout des subnets source
            for dst_ip, service in destinations.items():
                unique_addresses.add(dst_ip) # Ajout des IPs de destination

    # Création des objets d'adresse manquants
    output.append("config firewall address")
    for addr in sorted(unique_addresses):
        if forti_objects.get(addr):
            continue # Si l'objet existe déjà, je ne le recrée pas

        output.append(f'    edit "{addr}"')
        output.append(f'        set subnet {get_netmask(addr)}')
        output.append("    next")
    output.append("end\n")

    output.append("config firewall policy")

    # Génération des politiques de sécurité
    for interfaces_key, connexion in sorted_data.items(): # Pour chaque interface source//destination (rappel: data["intf_src//\\intf_dst"][subnet][ip] = [services])
        src_intf, dst_intf = interfaces_key.split("//\\\\")

        # Politiques groupées par IP
        for subnet, data_ip in connexion["ip"].items():
            for ip, services in data_ip.items():

                output.append("    edit 0")
                output.append(f'        set name "Policy_ip_{subnet.replace("/", "_")}_{ip}"')
                output.append(f'        set srcintf "{src_intf}"')
                output.append(f'        set dstintf "{dst_intf}"')
                output.append(f'        set srcaddr "{subnet if forti_objects.get(subnet) is None else forti_objects.get(subnet)}"') # Je vérifie si l'objet existe déjà, si oui j'utilise son nom
                output.append(f'        set dstaddr "{ip if forti_objects.get(ip) is None else forti_objects.get(ip)}"') # Je vérifie si l'objet existe déjà, si oui j'utilise son nom
                
                svc_str = ""
                
                for service_name in services:
                    svc_str += ' "' + service_name + '"'
                output.append(f'        set service{svc_str}')
                
                output.append('        set action accept')
                output.append('        set schedule "always"')
                output.append('        set logtraffic all')
                output.append("    next")
        
        # Politiques groupées par Service
        for subnet, data_service in connexion["service"].items():
            for service, ip_list in data_service.items():

                output.append("    edit 0")
                output.append(f'        set name "Policy_service_{subnet.replace("/", "_")}_{service}"')
                output.append(f'        set srcintf "{src_intf}"')
                output.append(f'        set dstintf "{dst_intf}"')
                output.append(f'        set srcaddr "{subnet if forti_objects.get(subnet) is None else forti_objects.get(subnet)}"') # Je vérifie si l'objet existe déjà, si oui j'utilise son nom
                
                ip_str = ""
                
                for ip in ip_list:
                    ip_str += f' "{ip if forti_objects.get(ip) is None else forti_objects.get(ip)}"' # Je vérifie si l'objet existe déjà, si oui j'utilise son nom
                output.append(f'        set dstaddr{ip_str}')
                
                output.append(f'        set service "{service}"')
                
                output.append('        set action accept')
                output.append('        set schedule "always"')
                output.append('        set logtraffic all')
                output.append("    next")

    output.append("end")

    result = "\n".join(output) # Je crée une grosse chaîne de caractères avec des sauts de ligne entre chaque élément de la liste pour écrire qu'une seule fois dans le fichier (opti opti)

    write_file("generated_fortinet_policy.txt", result) # J'écris le résultat dans un fichier
    print("Forti policy generation completed. Check 'generated_fortinet_policy.txt' for the output.")
    return result