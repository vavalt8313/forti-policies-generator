from collections import defaultdict
from determine_type import save_json

def determine_services_or_ip(data: dict) -> dict:
    """
    Docstring pour determine_services_or_ip

    :param data: Description
    :type data: dict
    :return: Description
    :rtype: dict
    """

    print("Determining grouping by services or IP...")

    result = {
    }

    service_to_ips_global = defaultdict(set)
    ip_service_to_subnets = defaultdict(set)

    for intf, data_for_intf in data.items():

        result[intf] = {
            "ip": {},
            "service": {}
        }

        for subnet, data_for_subnet in data_for_intf.items():
            service_to_ips = defaultdict(list)
            ip_to_services = defaultdict(list)
            for ip, services in data_for_subnet.items():
                for svc in services:
                    if ip not in service_to_ips[svc]:
                        service_to_ips[svc].append(ip)
                    if svc not in ip_to_services[ip]:
                        ip_to_services[ip].append(svc)
                    service_to_ips_global[svc] = [ip, intf]
                    ip_service_to_subnets[(ip, svc)].add(subnet)

            for svc, ips in service_to_ips.items():
                if len(ips) > 1:
                    if subnet not in result[intf]["service"]:
                        result[intf]["service"][subnet] = {}
                    result[intf]["service"][subnet][svc] = ips

            for ip, services in ip_to_services.items():
                if len(services) > 1 or (len(services) == 1 and len(service_to_ips[services[0]]) == 1):
                    if subnet not in result[intf]["ip"]:
                        result[intf]["ip"][subnet] = {}
                    result[intf]["ip"][subnet][ip] = services

    save_json("test.json", result)
    return result
