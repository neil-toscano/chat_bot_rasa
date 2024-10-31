import os
import yaml

# Consolidación de archivos de domain con estructura de comentarios y bloques
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
                            elif key == "slots":
                                consolidated_data["slots"].update(value)
                            elif key == "responses":
                                for response_key, response_value in value.items():
                                    consolidated_data["responses"][response_key] = response_value

    # Eliminamos duplicados en listas como "intents" y "entities"
    for key in ["intents", "entities", "actions", "e2e_actions"]:
        consolidated_data[key] = list(set(consolidated_data[key]))

    with open('domain.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("version: \"3.1\"\n\n")
        
        if consolidated_data["intents"]:
            outfile.write("intents:\n")
            for intent in consolidated_data["intents"]:
                outfile.write(f"  - {intent}\n")
            outfile.write("\n")
        
        if consolidated_data["responses"]:
            outfile.write("responses:\n\n")
            for response_key, response_content in consolidated_data["responses"].items():
                # Añade un comentario con el título del bloque de respuestas en mayúsculas
                formatted_title = response_key.replace("_", " ").upper()
                outfile.write(f"  # >> {formatted_title} :\n")
                outfile.write(f"  {response_key}:\n")
                for response in response_content:
                    yaml.dump(response, outfile, allow_unicode=True, default_style=None, default_flow_style=False, indent=4)
                outfile.write("\n")

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
