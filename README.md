# Outils d'Automatisation et d'Audit FortiGate

Ce dépôt contient une suite d'outils Python conçus pour faciliter la gestion, l'audit et la génération de configurations pour les pare-feux FortiGate.

Le projet se divise en deux applications principales :
1.  **`find_wrong_obj.py`** : Un auditeur d'objets de service.
2.  **`main.py`** : Un générateur de politiques de sécurité basé sur l'analyse de logs.

---

## Prérequis

Avant d'utiliser ces outils, assurez-vous d'avoir installé :
-   **Python 3.x**
-   Les dépendances nécessaires via le fichier `requirements.txt` :
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation via Makefile

Un `Makefile` est fourni pour simplifier l'exécution des tâches (compatible Windows et Linux).

-   **`make all`** : Lance le générateur de politiques (`main.py`).
-   **`make wrong_objects`** : Lance l'analyseur d'objets (`find_wrong_obj.py`).
-   **`make clear`** : Supprime les fichiers JSON générés par les programmes.

> **Note pour les utilisateurs Windows :**
> L'utilitaire `make` n'est pas installé par défaut sur Windows. Pour l'utiliser, vous devez l'installer via l'une de ces méthodes :
>
> 1.  **Via Winget** (Windows 10/11) :
>     ```powershell
>     winget install GnuWin32.Make
>     ```
> 2.  **Via Chocolatey** (si installé) :
>     ```powershell
>     choco install make
>     ```

---

## 1. Analyseur d'Objets de Service (`find_wrong_obj.py`)

Ce script a pour but d'analyser un fichier de configuration FortiGate (export texte) afin d'identifier les objets de service personnalisés (`custom service`) qui ne respectent pas les bonnes pratiques de configuration.

### Fonctionnement
Le script parcourt la configuration et classe les objets TCP et UDP en deux catégories (**Good** ou **Bad**) selon les critères suivants :
-   **Bad (Incorrect)** :
    -   La plage de ports commence par `0` (ex: `0-65535`).
    -   L'écart de la plage de ports est supérieur à **10** (ex: `100-200`).
    -   L'objet est un doublon d'un autre objet avec un nom different
-   **Good (Correct)** : Tous les autres objets respectant les critères.

### Utilisation
Lancez le script via la ligne de commande en spécifiant le fichier de configuration à analyser :

```bash
python find_wrong_obj.py <chemin_du_fichier_config>
```

> **Note :** Si aucun fichier n'est spécifié, le script demandera à l'utilisateur de le saisir.

### Résultat
Le script génère un fichier de sortie nommé **`forti_objects_sorted_bad_good.json`**. Ce fichier contient l'inventaire structuré des objets, facilitant ainsi la correction des configurations.

---

## 2. Générateur de Politiques (`main.py`)

Cette application interactive permet de traiter des fichiers de logs (au format CSV) pour en extraire les flux réseaux et générer automatiquement des propositions de politiques de sécurité.

### Fonctionnalités
-   **Analyse de logs** : Lecture et interprétation des fichiers CSV.
-   **Regroupement intelligent** : Consolidation des connexions par interfaces, sous-réseaux, adresses IP et services.
-   **Export JSON** : Sauvegarde des données regroupées pour une analyse ultérieure (`<nom_fichier>_regrouped.json`).
-   **Génération de politique** : Création des règles de pare-feu correspondantes.
-   **Mode Interactif** : Traitement en boucle de plusieurs fichiers sans redémarrage.

### Utilisation
Lancez l'application principale :

```bash
python main.py
```

L'application vous invitera ensuite à saisir le chemin de votre fichier CSV :

```text
Enter a csv file path (or 'exit' to quit): chemin/vers/mes_logs.csv
```

Une fois le traitement terminé, vous pouvez soit indiquer un nouveau fichier à traiter, soit taper `exit` pour fermer l'application.

>**Note importante: **
>Le programme vous proposera également de fournir un fichier de configuration Forti afin de remplacer les adresses ip par les noms réels des objets pour que les règles puissent être directement implémentées.
>Par défaut il va le chercher automatiquement sous le nom de `FW_objects.txt` mais s'il ne le trouve pas le programme vous proposera de rentrer le chemin vers le fichier.
>
>*Marche avec les fichiers `.txt` et `.conf`*

---






