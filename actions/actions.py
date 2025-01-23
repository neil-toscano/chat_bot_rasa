# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, EventType
from rasa_sdk.events import ReminderCancelled
from datetime import datetime, timedelta
import requests

class ActionSetReminder(Action):
    def name(self) -> str:
        return "action_set_reminder"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain) -> list[EventType]:
        # Configura el recordatorio para 5 minutos en el futuro
        events = [ReminderCancelled()]

        reminder_time = datetime.now() + timedelta(minutes=2)
        entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=reminder_time,
            entities=entities,
            name="delayed_message_reminder",    
            kill_on_user_message=False  # Cambiado a False para que el mensaje se envíe incluso si el usuario escribe
        )

        # Mensaje inmediato
        events.append(reminder)
        dispatcher.utter_message(text="¡Hola! Gracias por tu mensaje.")
        return [reminder]

class ActionReactToReminder(Action):
    def name(self) -> str:
        return "action_react_to_reminder"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain) -> list[EventType]:
        # Obtener el ID del remitente
        sender_id = tracker.sender_id
        
        # Obtener metadatos si están disponibles
        metadata = tracker.get_slot("session_started_metadata") or {}
        
        # Datos que enviaremos en el POST
        data = {
            "message": "👩‍💻 ¡Hola! ¿Sigues ahí? Si necesitas más información, no dudes en llamarnos al 📞 (01) 641 4300. Estaremos encantados de ayudarte.",
            "sender_id": sender_id,
        }

        try:
            response = requests.post('http://localhost:3000/api/v1/whatsapp', json=data)
            if response.status_code == 200:
                dispatcher.utter_message(text=f"¡Hola de nuevo {sender_id}! Han pasado 5 minutos desde tu último mensaje.")
            else:
                print(f"Error en la llamada al endpoint: {response.status_code}")
                print(f"Sender ID: {sender_id}")
                print(f"Metadata: {metadata}")
        except Exception as e:
            print(f"Error al hacer el POST: {str(e)}")

        return []
        
class ActionConsultarDocumento(Action):
    def name(self) -> str:
        return "action_consultar_documento"

    def run(self, dispatcher, tracker, domain):
        # Obtener el DNI del slot
        dni = tracker.get_slot('dni')

        if dni:
            # Llamada a la API con el DNI (reemplaza con la URL de tu API real)
            api_url = f"https://api.ejemplo.com/consulta-tramite?dni={dni}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                estado = data.get("estado", "No se encontró información.")
                mensaje = f"El estado de tu documento/trámite con DNI {dni} es: {estado}."
            else:
                mensaje = "Lo siento, no pude obtener información sobre tu documento en este momento."
        else:
            mensaje = "No proporcionaste un DNI válido."

        dispatcher.utter_message(text=mensaje)
        return []
# class ForgetReminders(Action):

#     def name(self) -> Text:
#         return "action_forget_reminders"

#     async def run(
#         self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(f"Okay, I'll cancel all your reminders.")

#         # Cancel all reminders
#         return [ReminderCancelled()]