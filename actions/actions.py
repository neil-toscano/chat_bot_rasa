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
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, EventType
from rasa_sdk.events import ReminderCancelled
from datetime import datetime, timedelta
from rasa_sdk.types import DomainDict
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

class ValidateConsultaDocumentoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_consulta_documento_form"

    @staticmethod
    def valid_dni_range() -> List[int]:
        """Define un rango válido de DNI (ajustar según los requisitos)."""
        return range(10000000, 99999999)  # Ejemplo para DNIs de 8 dígitos

    def validate_documentoId(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida el valor del slot documentoId."""

        if isinstance(slot_value, str) and slot_value.isdigit():
            dni = int(slot_value)
            if dni in self.valid_dni_range():
                # Validación exitosa
                return {"documentoId": dni}
            else:
                dispatcher.utter_message(
                    text="El DNI proporcionado no está en el rango válido. Por favor, inténtalo de nuevo."
                )
        else:
            dispatcher.utter_message(
                text="El DNI ingresado no es válido. Asegúrate de ingresar un número de DNI correcto."
            )
        # Si la validación falla, se solicita nuevamente el slot
        return {"documentoId": None}
# class ForgetReminders(Action):

#     def name(self) -> Text:
#         return "action_forget_reminders"

#     async def run(
#         self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(f"Okay, I'll cancel all your reminders.")

#         # Cancel all reminders
#         return [ReminderCancelled()]