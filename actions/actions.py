# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Configura el nivel de logging para ver la salida de debug
logging.basicConfig(level=logging.INFO)

# Diccionario de respuestas para cada opción y pregunta
RESPUESTAS = {
    "formalizacion_item01": {
        "consulta": "Es un permiso otorgado por la municipalidad para que un negocio inicie su actividad comercial  en un local que ha sido clasificado como de riesgo bajo",
        "necesidad": "a",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item02": {
        "consulta": "a",
        "necesidad": "a",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item03": {
        "consulta": "a",
        "necesidad": "a",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item04": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item05": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item06": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item07": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item08": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item09": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "formalizacion_item10": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "gestion_item01": {
        "consulta": "Es una inspección técnica de seguridad que se realiza en establecimientos con nivel de riesgo bajo.",
        "necesidad": "Solicitud de ITSE, indicando número y fecha de pago. Declaración jurada de cumplimiento de Seguridad en Edificaciones.",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "gestion_item02": {
        "consulta": "Es el proceso para actualizar el certificado de inspección técnica de seguridad en edificaciones para establecimientos con un nivel de riesgo bajo.",
        "necesidad": "Solicitud de  renovación ITSE, indicando número y fecha de pago. Declaración jurada de cumplimiento de Seguridad en Edificaciones.",
        "costo": "El costo al derecho de trámite es de S/ 132.40"
    },
    "gestion_item03": {
        "consulta": "Es una inspección técnica de seguridad que se realiza en establecimientos con riesgo medio después de que han comenzado sus actividades.",
        "necesidad": "Solicitud de ITSE, indicando número y fecha de pago. Declaración jurada de cumplimiento de Seguridad en Edificaciones",
        "costo": "El costo al derecho de trámite es de S/ 162.70"
    },
    "gestion_item04": {
        "consulta": "Es el proceso para actualizar el certificado de inspección técnica de seguridad en edificaciones para establecimientos con un nivel de riesgo medio.",
        "necesidad": "Solicitud de  renovación ITSE, indicando número y fecha de pago. Declaración jurada de cumplimiento de Seguridad en Edificaciones.",
        "costo": "El costo al derecho de trámite es de S/ 151.60"
    },
    "gestion_item05": {
        "consulta": "Evaluación de seguridad previa al inicio de actividades en establecimientos con alto riesgo.",
        "necesidad": "Solicitud de ITSE, indicando número y fecha de pago. Documentos técnicos en copia simple.",
        "costo": "El costo al derecho de trámite es de S/ 367.20"
    },
    "gestion_item06": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "gestion_item07": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "gestion_item08": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "gestion_item09": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "gestion_item10": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "orientacion_item01": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "orientacion_item02": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "registro_item01": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "registro_item02": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "registro_item03": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "registro_item04": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "obras_item01": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "obras_item02": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "obras_item03": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "obras_item04": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "obras_item05": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    },
    "obras_item06": {
        "consulta": "",
        "necesidad": "",
        "costo": "El costo al derecho de trámite es de S/ 229.20"
    }
}

class ActionResponderPregunta(Action):
    def name(self) -> Text:
        return "action_responder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        opcion = tracker.get_slot("opcion")
        intent = tracker.latest_message['intent'].get('name')
        logging.info(f"Intent detected: {intent}, Slot 'opcion': {opcion}")

        # Verifica si 'opcion' está definida y es válida en RESPUESTAS
        if not opcion or opcion not in RESPUESTAS:
            dispatcher.utter_message(text="La opción seleccionada no es válida o no está disponible.")
            return []

        # Elimina el prefijo 'pregunta_' para obtener la clave de consulta
        clave_intento = intent.replace("pregunta_", "")
        respuesta = RESPUESTAS[opcion].get(clave_intento)

        # Si la respuesta no está definida en el diccionario RESPUESTAS, da una respuesta genérica
        if respuesta:
            dispatcher.utter_message(text=respuesta)
        else:
            dispatcher.utter_message(text="Lo siento, no tengo una respuesta para esa consulta específica.")

        return []

class ActionSetOpcion(Action):
    def name(self) -> Text:
        return "action_set_opcion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        opcion = next(tracker.get_slot("opcion"), None)
        logging.info(f"Setting slot 'opcion' to: {opcion}")

        # Valida si 'opcion' fue detectada en la entidad y existe en RESPUESTAS
        if opcion and opcion in RESPUESTAS:
            dispatcher.utter_message(text=f"Has seleccionado la opción: {opcion}")
            return [SlotSet("opcion", opcion)]
        else:
            # Maneja el caso en que no se encuentra una opción válida
            dispatcher.utter_message(text="No se ha podido identificar una opción válida. Por favor, elige una opción de la lista.")
            return [SlotSet("opcion", None)]
