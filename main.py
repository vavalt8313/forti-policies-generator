from determine_type import determine_type_file, save_json
from connexions import regroup_connexions
from gen_policy import gen_policy
from tqdm import tqdm
import ipaddress
import gc

IS_LOOPING = True

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
