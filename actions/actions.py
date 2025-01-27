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
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.events import SlotSet  # Importa SlotSet
import re 
import requests
import pytz

class ActionSetReminder(Action):
    def name(self) -> str:
        return "action_set_reminder"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain) -> list[EventType]:
        # Configura el recordatorio para 2 minutos en el futuro usando la hora de Lima (UTC-5)
        events = [ReminderCancelled()]

        lima_tz = pytz.timezone("America/Lima")  # Hora de Lima (Perú)
        reminder_time = datetime.now(lima_tz) + timedelta(minutes=5)  # Hora de Lima + 5 minutos
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
    def is_flexible_tracking_code(tracking_code: str) -> bool:
        """Valida un código de seguimiento genérico con un formato específico."""
        # Patrón general:
        # - Comienza con cualquier conjunto de letras o letras y números.
        # - Sigue con exactamente 7 dígitos.
        # - Termina con un guion seguido de 4 dígitos.
        print(f"Validando NUMERO DOCUMENTO con valor: {tracking_code}")

        pattern = r"^[A-Za-z0-9]+-\d{6,8}-\d{4}$"
        return bool(re.match(pattern, tracking_code))

    def validate_documentoId(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida el valor del slot documentoId."""

        sender_id = tracker.sender_id 
        print("===========================") 
        print("TELEFONO", sender_id)

        if isinstance(slot_value, str) and self.is_flexible_tracking_code(slot_value):
            slot_value = slot_value[0].upper() + slot_value[1:]
            try:
                consulta_url = f"https://virtual.munisjl.gob.pe:8080/api/seguimiento/{slot_value}"
                consulta_response = requests.get(consulta_url)
                data = consulta_response.json()

                print("ESTADO CODIGO RESPUESTA", consulta_response.status_code)

                if consulta_response.status_code == 200:
                    seguimiento = data.get("seguimiento", [])

                    # Crear una lista para almacenar todos los pasos del proceso
                    proceso_completo = []

                    # Recorremos el seguimiento en orden cronológico
                    for elemento in seguimiento:
                        fecha_hora = elemento.get("fecha_hora", "Fecha desconocida")
                        documento = elemento.get("documento", "Documento desconocido")
                        destinos = elemento.get("destinos", [])

                        # Limpiar el campo "Documento" para eliminar dígitos incomprensibles
                        if documento:
                            documento_limpio = re.sub(r"\s*/\s*\d+-\d+-\w+", "", documento)  # Elimina "/ 000030-2025-SFSA"
                        else:
                            documento_limpio = "Documento desconocido"

                        # Si hay destinos, los agregamos al proceso
                        if destinos and isinstance(destinos, list):
                            for destino in destinos:
                                dependencia = destino.get("dependencia", "Desconocida")
                                estado = destino.get("estado", "Desconocido")

                                # Agregamos cada paso al proceso completo
                                proceso_completo.append({
                                    "fecha_hora": fecha_hora,
                                    "documento": documento_limpio,
                                    "dependencia": dependencia,
                                    "estado": estado
                                })
                        else:
                            # Si no hay destinos, solo agregamos fecha y documento
                            proceso_completo.append({
                                "fecha_hora": fecha_hora,
                                "documento": documento_limpio,
                                "dependencia": None,  # No hay dependencia
                                "estado": None  # No hay estado
                            })

                    # Construir el mensaje con todo el proceso
                    if proceso_completo:
                        mensaje = "Aquí tienes el proceso completo de tu trámite:\n\n"
                        for i, paso in enumerate(proceso_completo, start=1):
                            mensaje += f"📌 Etapa {i}:\n"
                            mensaje += f"   📅 Fecha y Hora: {paso['fecha_hora']}\n"
                            mensaje += f"   📝 Documento: {paso['documento']}\n"

                            # Solo mostrar dependencia y estado si están disponibles
                            if paso['dependencia'] and paso['estado']:
                                mensaje += f"   🏢 Dependencia: {paso['dependencia']}\n"
                                mensaje += f"   ✅ Estado: {paso['estado']}\n"

                            # Agregar una línea separadora entre etapas
                            if i < len(proceso_completo):  # No agregar línea después de la última etapa
                                mensaje += "--------------------------------\n\n"

                        # Dividir el mensaje en partes si supera los 1024 caracteres
                        max_length = 1024
                        mensajes = [mensaje[i:i + max_length] for i in range(0, len(mensaje), max_length)]

                        # Enviar cada parte del mensaje
                        for parte in mensajes:
                            data = {
                                "message": parte,
                                "sender_id": sender_id
                            }
                            response = requests.post('http://localhost:3000/api/v1/whatsapp', json=data)

                        # Devolver el valor del slot para que el formulario continúe
                        return {"documentoId": slot_value}
                    else:
                        return {"documentoId": None}
                else:
                    print('ERROR: NO se pudo obtener respuesta de la plataforma seguimiento')
                    data = {
                            "message": "No se encontró información de seguimiento para el documento proporcionado",
                            "sender_id": sender_id
                        }
                    response = requests.post('http://localhost:3000/api/v1/whatsapp', json=data)
                    return {"documentoId": None}

            except requests.RequestException as e:
                print(e)
                data = {
                            "message": "Error al conectar con el servicio: Por favor, inténtalo más tarde.",
                            "sender_id": sender_id
                        }
                response = requests.post('http://localhost:3000/api/v1/whatsapp', json=data)
                return {"documentoId": None}
        else:
            return {"documentoId": None}

class ActionResetSlots(Action):
    def name(self):
        return "action_reset_slots"

    async def run(self, dispatcher, tracker, domain):
        print("Reseteando todos los slots................")
        return [AllSlotsReset()]