from collections import defaultdict
from determine_type import save_json

def determine_services_or_ip(data: dict) -> dict:
    """
    Détermine si les politiques doivent être groupées par Service ou par IP.

    Args:
        data (dict): Les données de connexion initiales.

    Returns:
        dict: Les données restructurées avec des clés 'ip' et 'service'.
    """

    print("Determining grouping by services or IP...")

    result = {
    }

    service_to_ips_global = defaultdict(set)
    ip_service_to_subnets = defaultdict(set)

    for intf, data_for_intf in data.items(): # Pour chaque interface source//destination (rappel: data["intf_src//\\intf_dst"][subnet][ip] = [services]) (lisible dans fichier_regrouped.json)

        result[intf] = { # Je crée le prototype du dictionnaire de résultat pour cette interface
            "ip": {},
            "service": {}
        }

        for subnet, data_for_subnet in data_for_intf.items(): # Pour chaque subnet source (data["intf_src//\\intf_dst"][subnet][ip] = [services])
            service_to_ips = defaultdict(list)
            ip_to_services = defaultdict(list)


            # Cartographie des relations IP <-> Service
            for ip, services in data_for_subnet.items(): # Pour chaque IP de destination (data["intf_src//\\intf_dst"][subnet][ip] = [services])
                for svc in services: # Pour chaque service dans la liste des services pour cette IP de destination
                    
                    if ip not in service_to_ips[svc]:
                        service_to_ips[svc].append(ip) # Je crée une liste des IPs pour chaque service
                    if svc not in ip_to_services[ip]:
                        ip_to_services[ip].append(svc) # Et une liste des services pour chaque IP pour pouvoir accéder aux deux infos facilement
                    
                    service_to_ips_global[svc] = [ip, intf] # Je crée une liste globale des IPs pour chaque service (pour savoir si un service est utilisé par plusieurs IPs sur différentes interfaces)
                    ip_service_to_subnets[(ip, svc)].add(subnet) # Je crée une liste globale des subnets pour chaque paire (IP, service) (pour savoir si une IP utilise un service sur plusieurs subnets)


            # Groupement par Service si plusieurs IPs partagent le même service
            for svc, ips in service_to_ips.items(): # Pour chaque service (service_to_ips[service] = [liste_ips])
                
                if len(ips) > 1: # Si plusieurs IPs utilisent ce service dans ce subnet
                    
                    if subnet not in result[intf]["service"]: # Si le subnet n'existe pas encore dans le dictionnaire résultat pour les services
                        result[intf]["service"][subnet] = {}  # Je crée une nouvelle entrée pour ce subnet
                    
                    result[intf]["service"][subnet][svc] = ips # Je crée une nouvelle entrée pour ce service avec la liste des IPs associées


            # Groupement par IP sinon
            for ip, services in ip_to_services.items():
                if len(services) > 1 or (len(services) == 1 and len(service_to_ips[services[0]]) == 1): # Si l'IP utilise plusieurs services ou 
                                                                                                        # si elle utilise un service unique qui n'est pas partagé avec d'autres IPs
                    if subnet not in result[intf]["ip"]: # Si le subnet n'existe pas encore dans le dictionnaire résultat pour les IPs
                        result[intf]["ip"][subnet] = {}  # Je crée une nouvelle entrée pour ce subnet

                    result[intf]["ip"][subnet][ip] = services # Je crée une nouvelle entrée pour cette IP avec la liste des services associés

    save_json("decoupe_services_ou_ip.json", result) # Sauvegarde du résultat pour debug (optionnel)
    return result
