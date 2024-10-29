import os
import yaml

# Consolidación de archivos de domain
def consolidate_domain_files():
    consolidated_data = {
        "version": "3.1",
        "intents": [],
        "entities": [],
        "slots": {},
        "responses": {},
        "actions": [],
        "forms": {},
        "e2e_actions": []
    }

    yaml_directory = 'domain'  # Carpeta de domain modularizado

    with open('domain.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("")  # Borra el contenido anterior

    for root, dirs, files in os.walk(yaml_directory):
        for filename in files:
            if filename.endswith('.yml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data:
                        for key, value in data.items():
                            if key in ["intents", "entities", "actions", "e2e_actions"]:
                                consolidated_data[key].extend(value)
                            elif key in ["slots", "responses", "forms"]:
                                consolidated_data[key].update(value)

    for key in ["intents", "entities", "actions", "e2e_actions"]:
        consolidated_data[key] = list(set(consolidated_data[key]))

    with open('domain.yml', 'w', encoding='utf-8') as outfile:
        yaml.dump(consolidated_data, outfile, default_flow_style=False, allow_unicode=True)

# Consolidación de archivos de nlu
def consolidate_nlu_files():
    consolidated_data = {"version": "3.1", "nlu": []}
    yaml_directory = 'nlu'  # Carpeta de nlu modularizado

    with open('data/nlu.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("")  # Borra el contenido anterior

    for root, dirs, files in os.walk(yaml_directory):
        for filename in files:
            if filename.endswith('.yml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data and "nlu" in data:
                        consolidated_data["nlu"].extend(data["nlu"])

    with open('data/nlu.yml', 'w', encoding='utf-8') as outfile:
        yaml.dump(consolidated_data, outfile, default_flow_style=False, allow_unicode=True)

# Consolidación de archivos de stories
def consolidate_stories_files():
    consolidated_data = {"version": "3.1", "stories": []}
    yaml_directory = 'stories'  # Carpeta de stories modularizado

    with open('data/stories.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("")  # Borra el contenido anterior

    for root, dirs, files in os.walk(yaml_directory):
        for filename in files:
            if filename.endswith('.yml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data and "stories" in data:
                        consolidated_data["stories"].extend(data["stories"])

    with open('data/stories.yml', 'w', encoding='utf-8') as outfile:
        yaml.dump(consolidated_data, outfile, default_flow_style=False, allow_unicode=True)

if __name__ == "__main__":
    consolidate_domain_files()
    consolidate_nlu_files()
    consolidate_stories_files()
    print("Consolidación completada para domain.yml, nlu.yml, y stories.yml")
