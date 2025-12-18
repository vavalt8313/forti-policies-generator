from determine_type import determine_type_file, save_json
from gen_policy import gen_policy
from tqdm import tqdm
import ipaddress
import gc

IS_LOOPING = True

STANDARD_SERVICES = {
    "80": "HTTP",
    "443": "HTTPS",
    "22": "SSH",
    "21": "FTP",
    "53": "DNS"
}

def regroup_connexions(data: tuple, file_path: str) -> dict:
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """

    connections = {"standard": {}, "custom": {}}
    subnet = ""
    
    if not len(data):
        print("No data found or error reading the file.")
        return None
    
    
    print(f"Processing your file: {file_path}:")
    for line in tqdm(data, desc="Regrouping connexions: "):
        srcip = line.get("srcip")
        if not srcip:
            continue
        
        try:
            subnet = ipaddress.IPv4Network(f"{srcip}/24", strict=False)
        except ValueError:
            print(f"Invalid IP address found: {srcip}. Skipping this entry.")
            continue
        
        std_or_custom = "standard" if str(line.get("dstport")) in STANDARD_SERVICES else "custom"
        
        if connections[std_or_custom].get(str(subnet)):
            if connections[std_or_custom][str(subnet)].get(line.get("dstip")):
                if (line.get("dstport") not in connections[std_or_custom][str(subnet)][line.get("dstip")]) and line.get("dstport") is not None:
                    connections[std_or_custom][str(subnet)][line.get("dstip")].append(line.get("dstport"))
            elif line.get("dstip") is not None and line.get("dstport") is not None:
                connections[std_or_custom][str(subnet)][line.get("dstip")] = [line.get("dstport")]
        elif line.get("dstip") is not None and line.get("dstport") is not None and subnet is not None:
            connections[std_or_custom][str(subnet)] = {line.get("dstip"): [line.get("dstport")]}
    return connections
        



def looping():
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    
    global IS_LOOPING

    file_path = input("Enter the file path (or 'exit' to quit): ")

    while IS_LOOPING and file_path and file_path.lower() != 'exit':
        data = determine_type_file(file_path)
        
        connexions = regroup_connexions(data, file_path)
        if not connexions:
            print("Error verifying connexions or no connexions found.")
            file_path = input("Enter the file path (or 'exit' to quit): ")
            continue
        
        save_json(f"{file_path}_regrouped.json", connexions)
        print(f"Regrouped connexions saved to {file_path}_regrouped.json")
        gen_policy(connexions)
        
        file_path = input("Enter the file path (or 'exit' to quit): ")
        if file_path.lower() == 'exit':
            IS_LOOPING = False
        gc.collect()

if __name__ == "__main__":
    looping()
