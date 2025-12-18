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

def get_service_name(port):
    """Renvoie le nom standard ou prépare un nom custom"""
    port = str(port)
    if port in STANDARD_SERVICES:
        return STANDARD_SERVICES[port]
    else:
        unique_custom_services.add(port)
        return f"TCP-{port}"

def gen_policy(data):
    """Génère la configuration Fortinet à partir des données agrégées."""

    output = []

    for std_or_custom, connexion in data.items():
        for src_subnet, destinations in connexion.items():
            unique_addresses.add(src_subnet)
            for dst_ip, ports in destinations.items():
                unique_addresses.add(dst_ip)
                for port in ports:
                    get_service_name(port)

    output.append("config firewall address")
    for addr in sorted(unique_addresses):
        output.append(f'    edit "{addr}"')
        output.append(f'        set subnet {get_netmask(addr)}')
        output.append("    next")
    output.append("end\n")

    if unique_custom_services:
        output.append("config firewall service custom")
        for port in sorted(unique_custom_services, key=int):
            output.append(f'    edit "TCP-{port}"')

            output.append(f'        set tcp-portrange {port}')
            output.append("    next")
        output.append("end\n")

    output.append("config firewall policy")

    for std_or_custom, connexion in data.items():
        for src_subnet, destinations in connexion.items():
            dst_list = list(destinations.keys())

            all_ports_raw = []
            for p_list in destinations.values():
                all_ports_raw.extend(p_list)

            service_names = sorted(list(set([get_service_name(p) for p in all_ports_raw])))

            output.append("    edit 0")
            output.append(f'        set name "Policy_{src_subnet.replace("/", "_")}_{std_or_custom}"')
            output.append('        set srcintf "any"')
            output.append('        set dstintf "any"')
            output.append(f'        set srcaddr "{src_subnet}"')

            dst_str = '" "'.join(dst_list)
            output.append(f'        set dstaddr "{dst_str}"')
            
            svc_str = '" "'.join(service_names)
            output.append(f'        set service "{svc_str}"')
            
            output.append('        set action accept')
            output.append('        set schedule "always"')
            output.append('        set logtraffic all')
            output.append("    next")

    output.append("end")

    result = "\n".join(output)
    write_file("generated_fortinet_policy.txt", result)
    print("Configuration Fortinet générée dans 'generated_fortinet_policy.txt'.")
    return result