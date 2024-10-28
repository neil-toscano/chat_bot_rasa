import os
import yaml

def consolidate_yaml_files():
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

    # Ruta a la carpeta 'domain' que contiene los módulos
    yaml_directory = 'domain'  

    # Vaciar el contenido de 'domain.yml' antes de consolidar
    with open('domain.yml', 'w', encoding='utf-8') as outfile:
        outfile.write("")  # Borra el contenido anterior de domain.yml

    for root, dirs, files in os.walk(yaml_directory):
        for filename in files:
            if filename.endswith('.yml'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data:
                        # Combinar cada sección de acuerdo a su tipo
                        for key, value in data.items():
                            if key in ["intents", "entities", "actions", "e2e_actions"]:
                                consolidated_data[key].extend(value)
                            elif key in ["slots", "responses", "forms"]:
                                consolidated_data[key].update(value)

    # Elimina duplicados de listas como intents, entities, actions
    for key in ["intents", "entities", "actions", "e2e_actions"]:
        consolidated_data[key] = list(set(consolidated_data[key]))

    # Guardar el archivo consolidado
    with open('domain.yml', 'w', encoding='utf-8') as outfile:
        yaml.dump(consolidated_data, outfile, default_flow_style=False, allow_unicode=True)

if __name__ == "__main__":
    consolidate_yaml_files()
