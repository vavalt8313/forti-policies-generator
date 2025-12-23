from tqdm import tqdm
import ipaddress

STANDARD_SERVICES = {
    "80": "HTTP",
    "443": "HTTPS",
    "22": "SSH",
    "21": "FTP",
    "53": "DNS",
    "4242": "Custom-Service-4242"
}

def analyse_line(connexions: dict, line: dict, interfaces_key: tuple) -> dict:
    srcip = line.get("srcip")
    if not srcip:
        return connexions
    try:
        subnet = ipaddress.IPv4Network(f"{srcip}/24", strict=False)
    except ValueError:
        print(f"Invalid IP address found: {srcip}. Skipping this entry.")
        return connexions
    
    
    if connexions[interfaces_key].get(str(subnet)):

        if connexions[interfaces_key][str(subnet)].get(line.get("dstip")):

            if (line.get("service") not in connexions[interfaces_key][str(subnet)][line.get("dstip")]) and line.get("service") is not None:
                connexions[interfaces_key][str(subnet)][line.get("dstip")].append(line.get("service"))

        elif line.get("dstip") is not None and line.get("service") is not None:
            connexions[interfaces_key][str(subnet)][line.get("dstip")] = [line.get("service")]

    elif line.get("dstip") is not None and line.get("service") is not None and subnet is not None:
        connexions[interfaces_key][str(subnet)] = {line.get("dstip"): [line.get("service")]}
    
    return connexions

def regroup_connexions(data: tuple, file_path: str) -> dict:
    """***Regroup the connexions from the data read from the file.***\n
    Keyword arguments:\n
    data -- *The data read from the file*.\n
    file_path -- *The path to the file to read*.\n
    Return: *A dictionary containing the regrouped connexions*.
    """

    connexions = {}
    subnet = ""

    if not len(data):
        print("No data found or error reading the file.")
        return None

    print(f"Processing your file: {file_path}:")
    for line in tqdm(data, desc="Regrouping connexions: "):
        interfaces_key = str(line.get("srcintf")) + "//\\\\" + str(line.get("dstintf"))
        if connexions.get(interfaces_key) is None:
            connexions[interfaces_key] = {}
        connexions = analyse_line(connexions, line, interfaces_key)
    return connexions