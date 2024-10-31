import os
import yaml
from ruamel.yaml import YAML

# Consolidación de archivos de domain
def consolidate_domain_files():
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    combined_content = {
        "version": "3.1",
        "intents": [],
        "responses": {}
    }

    # Función para leer archivos recursivamente
    for root, _, files in os.walk("domain"):
        for filename in files:
            if filename.endswith(".yml"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = yaml.load(file)
                    
                    # Verificar que el contenido no sea None
                    if content is None:
                        continue
                    
                    # Combinar intents y responses de cada archivo
                    if "intents" in content:
                        combined_content["intents"].extend(content["intents"])
                    
                    if "responses" in content:
                        combined_content["responses"].update(content["responses"])

    # Escribir el archivo combinado en el archivo principal
    with open("domain.yml", 'w', encoding='utf-8') as output:
        yaml.dump(combined_content, output)

# Consolidación de archivos de nlu
def consolidate_nlu_files():
    consolidated_data = {"version": "3.1", "nlu": []}
    yaml_directory = 'nlu'  # Carpeta de nlu modularizado

    for root, dirs, files in os.walk(yaml_directory):
        for filename in files:
            if filename.endswith('.yml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data and "nlu" in data:
                        for intent_data in data["nlu"]:
                            formatted_intent = {
                                "intent": intent_data["intent"],
                                "examples": "\n".join(f"  {line}" for line in intent_data["examples"].strip().splitlines())
                            }
                            consolidated_data["nlu"].append(formatted_intent)

    with open('data/nlu.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("version: \"3.1\"\n\n")
        for intent in consolidated_data["nlu"]:
            outfile.write(f"# >> {intent['intent'].replace('_', ' ').upper()} :\n")
            outfile.write(f"- intent: {intent['intent']}\n")
            outfile.write("  examples: |\n")
            outfile.write(f"{intent['examples']}\n\n")

# Consolidación de archivos de stories
def consolidate_stories_files():
    consolidated_data = {"version": "3.1", "stories": []}
    yaml_directory = 'stories'  # Carpeta de stories modularizado

    for root, dirs, files in os.walk(yaml_directory):
        for filename in files:
            if filename.endswith('.yml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data and "stories" in data:
                        consolidated_data["stories"].extend(data["stories"])

    with open('data/stories.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("version: \"3.1\"\n\nstories:\n")
        for story in consolidated_data["stories"]:
            outfile.write(f"\n# >> {story['story'].upper()} :\n")
            outfile.write(f"- story: {story['story']}\n")
            outfile.write("  steps:\n")
            for step in story["steps"]:
                if "intent" in step:
                    outfile.write(f"  - intent: {step['intent']}\n")
                if "action" in step:
                    outfile.write(f"  - action: {step['action']}\n")

if __name__ == "__main__":
    consolidate_domain_files()
    consolidate_nlu_files()
    consolidate_stories_files()
    print("Consolidación completada para domain.yml, data/nlu.yml, y data/stories.yml")