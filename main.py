from determine_type import determine_type_file, save_json
from connexions import regroup_connexions
from gen_policy import gen_policy
from tqdm import tqdm
import ipaddress
import gc

IS_LOOPING = True

def looping():
    """
    Boucle principale pour traiter les fichiers de manière interactive.
    Demande le chemin du fichier, regroupe les connexions et génère la politique.
    """
    
    global IS_LOOPING

    file_path = input("Enter a csv file path (or 'exit' to quit): ")

    while IS_LOOPING and file_path and file_path.lower() != 'exit':

        data = determine_type_file(file_path) # lit le fichier et retourne une liste de dictionnaires
        
        connexions = regroup_connexions(data, file_path) # regroupe les connexions par interfaces, subnets, IPs et services
        
        if not connexions:
            print("Error verifying connexions or no connexions found.")
            file_path = input("Enter the file path (or 'exit' to quit): ")
            continue
        
        save_json(f"{file_path}_regrouped.json", connexions) # sauvegarde les connexions dans un fichier JSON pour pouvoir les analyser plus tard (optionnel)
        print(f"Regrouped connexions saved to {file_path}_regrouped.json")
        
        gen_policy(connexions) # génère la politique Fortinet à partir des connexions regroupées
        
        file_path = input("Enter the file path (or 'exit' to quit): ") # demande un nouveau fichier à traiter car il le fait en boucle
        
        if file_path.lower() == 'exit':
            IS_LOOPING = False
        
        gc.collect() # libère la mémoire après chaque itération (opti opti)

if __name__ == "__main__":
    looping()
