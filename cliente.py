import slixmpp
from aioconsole import ainput
import asyncio

class MyCliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.conectado = False
        self.usu = jid


        self.add_event_handler("session_start", self.start)
        self.add_event_handler('subscription_request', self.handle_subscription_request)
        self.add_event_handler('message', self.notify_received)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.conectado = True
        print("Sesión iniciada correctamente. \n")
        asyncio.create_task(self.interactuar_con_cliente())

    async def show_contacts(self):
        roster = self.client_roster
        contacts = roster.keys()
        contact_list = []

        if not contacts:
            print("No tienes contactos.")
            return

        for jid in contacts:
            user = jid

            connection = roster.presence(jid)
            show = 'Disponible'
            status = ''

            for answer, presence in connection.items():
                if presence['show']:
                    show = presence['show']
                if presence['status']:
                    status = presence['status']
            if user != self.usu:
                contact_list.append((user, show, status))

        print("\nTus contactos son los siguentes: \n")
        for c in contact_list:
            print(f"Contacto: {c[0]}")
            print(f"Estado: {c[1]}")
            print(f"Mensaje de estado: {c[2]}")
            print("")
        print("")

    async def add_contact(self, jid):
        self.send_presence_subscription(pto=jid)
        await self.get_roster()
        print("Contacto agregado correctamente.")

    async def contact_details(self, jid):
            roster = self.client_roster
            contacts = roster.keys()

            if jid in contacts:
                connection = roster.presence(jid)
                show = 'Disponible'
                status = 'El usuario no tiene un estado...'

                for answer, presence in connection.items():
                    if presence['show']:
                        show = presence['show']
                    if presence['status']:
                        status = presence['status']


                print("\nDetalles del contacto:\n")
                print(f"Usuario: {jid}")
                print(f"Estado: {show}")
                print(f"Mensaje de estado: {status}")
                print("")

            else: 
                print("El usuario no se encuentra en tus contactos.")
                return

    async def sendmessage(self, to_jid):
        print(" - Estas en el chat de ->")
        print(to_jid)
        print("Si deseas salir de este chat envia -> 'salir' \n")

        permanecer = True

        while  permanecer:
            message = await ainput('-> ')
            if message == 'salir':
                permanecer = False
            else:
                self.send_message(mto=to_jid, mbody=message, mtype='chat')

    async def notify_received(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(f"Mesaje recibido de {msg['from']}: {msg['body']}")
        
    async def handle_subscription_request(self, msg):
        print(f"Solicitud de suscripción recibida de {msg['from']}")
        self.send_presence(pto=msg['from'], ptype='subscribed')  
        print(f"Suscripción aprobada para {msg['from']}")

    async def interactuar_con_cliente(self):
        while self.conectado:
            try:

                print("*****************************************************")
                print("Menú de opciones:")
                print("1) Mostrar todos los contactos y su estado.")
                print("2) Agregar un usuario a los contactos.")
                print("3) Mostrar detalles de contacto de un usuario.")
                print("4) Comunicación 1 a 1 con cualquier usuario/contacto (Chat con un usuario).")
                print("5) Participar en conversaciones grupales.")
                print("6) Definir mensaje de presencia.")
                print("7) Enviar/recibir notificaciones.")
                print("8) Enviar/recibir archivos.")
                print("9) Desconectarse.")
                print("10) Eliminar cuenta.")
                print("*****************************************************\n")

                opcion = await ainput("Ingrese el número de la opción deseada: \n")

                if opcion == '1':
                    print("Opcion elegida 1:")
                    await self.show_contacts()
                elif opcion == '2':
                    jid = input("Ingrese el JID del usuario que desea agregar: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 2:")
                    self.add_contact(jid)
                elif opcion == '3':
                    jid = input("Ingrese el JID del usuario del que desea ver detalles: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 3:")
                    await self.contact_details(jid)
                elif opcion == '4':
                    jid = input("Ingrese el JID del usuario al que desea enviar el mensaje: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 4: \n")
                    await self.sendmessage(jid )
                elif opcion == '9':
                    self.conectado = False
                    self.disconnect()
                elif opcion == '10':
                    self.conectado = False
                    self.disconnect()
                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
            except Exception as e:
                print(f"Error: {e}")

