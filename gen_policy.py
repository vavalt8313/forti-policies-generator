from get_forti_objects import get_forti_objects
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
    """Génère la configuration Fortinet à partir des données agrégées."""

    output = []
    forti_objects = get_forti_objects(forti_objects_file)

    for interfaces_key, data_for_intf in data.items():
        for std_or_custom, connexion in data_for_intf.items():
            for src_subnet, destinations in connexion.items():
                unique_addresses.add(src_subnet)
                for dst_ip, service in destinations.items():
                    unique_addresses.add(dst_ip)

    output.append("config firewall address")
    for addr in sorted(unique_addresses):
        if forti_objects.get(addr):
            continue
        output.append(f'    edit "{addr}"')
        output.append(f'        set subnet {get_netmask(addr)}')
        output.append("    next")
    output.append("end\n")

    output.append("config firewall policy")

    for interfaces_key, data_for_intf in data.items():
        src_intf, dst_intf = interfaces_key.split("//\\\\")
        for std_or_custom, connexion in data_for_intf.items():
            for src_subnet, destinations in connexion.items():
                dst_list = list(destinations.keys())
                for i in range(len(dst_list)):
                    if forti_objects.get(dst_list[i]):
                        dst_list[i] = forti_objects.get(dst_list[i])

                service_names = {}
                for p_list in destinations.values():
                    for service in p_list:
                        service_names[service] = []

                output.append("    edit 0")
                output.append(f'        set name "Policy_{src_subnet.replace("/", "_")}_{std_or_custom}"')
                output.append(f'        set srcintf "{src_intf}"')
                output.append(f'        set dstintf "{dst_intf}"')
                output.append(f'        set srcaddr "{src_subnet if forti_objects.get(src_subnet) is None else forti_objects.get(src_subnet)}"')

                dst_str = '" "'.join(dst_list)
                output.append(f'        set dstaddr "{dst_str}"')
                
                svc_str = ""
                
                for service_name in service_names.keys():
                    svc_str += ' "' + service_name + '"'

                output.append(f'        set service {svc_str}')
                
                output.append('        set action accept')
                output.append('        set schedule "always"')
                output.append('        set logtraffic all')
                output.append("    next")

    output.append("end")

    result = "\n".join(output)
    write_file("generated_fortinet_policy.txt", result)
    print("Configuration Fortinet générée dans 'generated_fortinet_policy.txt'.")
    return result