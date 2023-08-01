import slixmpp
from aioconsole import ainput
import asyncio

class MyCliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.conectado = False


        self.add_event_handler("session_start", self.start)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.conectado = True
        print("Sesión iniciada correctamente.")
        asyncio.create_task(self.interactuar_con_cliente())

    async def interactuar_con_cliente(self):

        print("Comandos disponibles:")
        print("1. show_contacts() -> Mostrar todos los contactos y su estado.")
        print("2. add_contact(jid) -> Agregar un usuario a los contactos.")
        print("3. contact_details(jid) -> Mostrar detalles de contacto de un usuario.")
        print("4. send_message(to_jid, message) -> Enviar un mensaje a un usuario.")
        print("5. exit() -> Salir del programa.")

        while self.conectado:
            try:
                opcion = await ainput("Ingrese el número de la opción (o '5' para salir): ")
                if opcion == '1':
                    self.show_contacts()
                elif opcion == '2':
                    jid = input("Ingrese el JID del usuario que desea agregar: ")
                    self.add_contact(jid)
                elif opcion == '3':
                    jid = input("Ingrese el JID del usuario del que desea ver detalles: ")
                    self.contact_details(jid)
                elif opcion == '4':
                    jid = input("Ingrese el JID del usuario al que desea enviar el mensaje: ")
                    message = input("Ingrese el mensaje: ")
                    self.send_message(jid, message)
                elif opcion == '5':
                    self.conectado = False
                    self.disconnect()
                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
            except Exception as e:
                print(f"Error: {e}")

    def show_contacts(self):
        contacts = self.client_roster.keys()
        for contact in contacts:
            pres = self.client_roster.presence(contact)
            print(f"Contacto: {contact}, Estado: {pres['show']} - {pres['status']}")

    def add_contact(self, jid):
        self.send_presence_subscription(pto=jid)

    def contact_details(self, jid):
        pres = self.client_roster.presence(jid)
        print(f"Contacto: {jid}, Estado: {pres['show']} - {pres['status']}")

    def message_received(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Mensaje recibido de {msg['from']}: {msg['body']}")

    def send_message(self, to_jid, message):
        self.send_message(mto=to_jid, mbody=message, mtype='chat')