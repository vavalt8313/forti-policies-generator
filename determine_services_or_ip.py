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

    result = {
    }

    # Global collections for subnet grouping
    service_to_ips_global = defaultdict(set)
    ip_service_to_subnets = defaultdict(set)

    for intf, data_for_intf in data.items():

        result[intf] = {
            "ip": {},
            "service": {}
        }

        for subnet, data_for_subnet in data_for_intf.items():
            # Collect data for this subnet
            service_to_ips = defaultdict(list)
            ip_to_services = defaultdict(list)
            for ip, services in data_for_subnet.items():
                for service in services:
                    if ip not in service_to_ips[service]:
                        service_to_ips[service].append(ip)
                    if service not in ip_to_services[ip]:
                        ip_to_services[ip].append(service)
                    # Global collections
                    service_to_ips_global[service] = [ip, intf]
                    ip_service_to_subnets[(ip, service)].add(subnet)

            # Determine grouping
            group_by_service = any(len(ips) > 1 for ips in service_to_ips.values())
            group_by_ip = False
            if not group_by_service:
                for ip, svcs in ip_to_services.items():
                    if len(svcs) > 1:
                        # Check if all services are unique to this IP
                        unique = all(len(service_to_ips[svc]) == 1 and service_to_ips[svc][0] == ip for svc in svcs)
                        if unique:
                            group_by_ip = True
                            break

            # Populate result based on grouping
            if group_by_service:
                if subnet not in result[intf]["service"]:
                    result[intf]["service"][subnet] = {}
                for svc, ips in service_to_ips.items():
                    result[intf]["service"][subnet][svc] = ips
            elif group_by_ip:
                if subnet not in result[intf]["ip"]:
                    result[intf]["ip"][subnet] = {}
                for ip, svcs in ip_to_services.items():
                    result[intf]["ip"][subnet][ip] = svcs

    # Populate subnet grouping
    #for service, infos in service_to_ips_global.items():
    #    ips, intf = infos
    #    if len(ips) == 1:
    #        ip = next(iter(ips))
    #        subnets = ip_service_to_subnets[(ip, service)]
    #        if len(subnets) > 1:
    #            if service not in result[intf]["subnet"]:
    #                result[intf]["subnet"][service] = {}
    #            result[intf]["subnet"][service][ip] = list(subnets)

    save_json("test.json", result)
    return result
