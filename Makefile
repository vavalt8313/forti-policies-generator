JSON_FILES	=	decoupe_services.json \
				wrong_objects.json \
				forti_objects.json \
				*_regrouped.json

# Détection du système d'exploitation
ifeq ($(OS),Windows_NT)
    PYTHON = python
    RM = del /Q
else
    PYTHON = python3
    RM = rm -f
endif

.PHONY: all wrong_objects clear

# Lance l'application principale
all:
	$(PYTHON) main.py

# Lance l'analyseur d'objets
wrong_objects:
	$(PYTHON) find_wrong_obj.py

# Supprime les fichiers JSON générés (ignore les erreurs si aucun fichier n'existe)
clear:
	-$(RM) *.json