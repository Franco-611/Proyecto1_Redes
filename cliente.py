import slixmpp
from aioconsole import ainput
import asyncio
import os
from pathlib import Path

class MyCliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.conectado = False
        self.usu = jid

        self.message_queue = asyncio.Queue()


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
        contactos = []

        if not contacts:
            print("No tienes contactos.")
            return
        
        for jid in contacts:
            user = jid

            connection = roster.presence(jid)
            show = 'Desconectado'
            status = ''
            if user != self.usu:
                for answer, presence in connection.items():
                    if presence:
                        show = presence['show']
                    if presence['status']:
                        status = presence['status']

                    if show == 'dnd':
                        show = 'Ocupado'
                    if show == 'xa':
                        show = 'No disponible'
                    if show == 'away':
                        show = 'Ausente'
                    if show == '':
                        show = 'Disponible'
                contactos.append((user, show, status))

        print("\nTus contactos son los siguentes: \n")
        for c in contactos:
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
                show = 'Desconectado'
                status = ''

                for answer, presence in connection.items():
                    if presence:
                        show = presence['show']
                    if presence['status']:
                        status = presence['status']

                    if show == 'dnd':
                        show = 'Ocupado'
                    if show == 'xa':
                        show = 'No disponible'
                    if show == 'away':
                        show = 'Ausente'
                    if show == '':
                        show = 'Disponible'


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
                try:
                    self.send_message(mto=to_jid, mbody=message, mtype='chat')
                except:
                    print("Error al enviar el mensaje.")

    async def notify_received(self, msg):
        if msg['type'] in ('chat', 'normal'):
            message = f"Mensaje recibido de {msg['from']}: {msg['body']}"
            await self.message_queue.put(message)
        
    async def handle_subscription_request(self, msg):
        print(f"Solicitud de suscripción recibida de {msg['from']}")
        self.send_presence(pto=msg['from'], ptype='subscribed')  
        print(f"Suscripción aprobada para {msg['from']}")

    async def mostrar_mensajes_recibidos(self):
        while self.conectado:
            message = await self.message_queue.get()
            print(message)

    async def change_message(self, msg):
        estado  = ''
        self.send_presence(pshow=estado, pstatus=msg) 
        await self.get_roster()
        print("Mensaje de presencia cambiado correctamente.")

    async def send_file(self, to_jid, file_path):
        try:
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                html_body = f"<a href='file://{filename}'>{filename}</a>"
                mhtml = {'body': html_body}
                self.send_message(mto=to_jid, mbody=filename, mtype='chat', mhtml=mhtml)
                await self.send_file_transfer(to_jid, file)
            print("Archivo enviado con éxito.")
        except Exception as e:
            print(f"Error al enviar el archivo: {e}")

    async def send_file_transfer(self, to_jid, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_transfer = self['xep_0363'].upload(to_jid, file)
                await file_transfer.send()
            print("Archivo enviado con éxito.")
        except Exception as e:
            print(f"Error al enviar el archivo: {e}")

    async def crear_grupo(self, nombre_grupo):
        try:
            # Crear una sala de chat (grupo) utilizando MUC
            respuesta = await self.plugin['xep_0045'].join_muc(
                room=nombre_grupo,
                nick=self.usu,
                wait=True
            )

            if respuesta['muc']['#status_code'] == 201:
                print(f"Se ha creado el grupo '{nombre_grupo}' correctamente.")
                print(f"Puedes invitar a otros usuarios con el comando: /invite usuario@servidor")
            else:
                print(f"No se pudo crear el grupo '{nombre_grupo}'.")

        except Exception as e:
            print(f"Error al crear el grupo '{nombre_grupo}': {str(e)}")

    async def invitar_usuario(self, nombre_grupo, jid_usuario):
        try:
            # Invitar a un usuario a unirse al grupo utilizando MUC
            respuesta = await self.plugin['xep_0045'].invite(
                room=nombre_grupo,
                jid=jid_usuario,
                reason='¡Únete a nuestro grupo de chat!'
            )

            if respuesta['muc']['#status_code'] == 170:
                print(f"Se ha enviado una invitación a '{jid_usuario}' para unirse al grupo '{nombre_grupo}'.")
            else:
                print(f"No se pudo enviar la invitación a '{jid_usuario}'.")
        except Exception as e:
            print(f"Error al enviar la invitación a '{jid_usuario}': {str(e)}")

    def delete_count(self):
        try:
            delete_stanza = f"""
                <iq type="set" id="delete-account">
                <query xmlns="jabber:iq:register">
                    <remove jid="{self.usu}"/>
                </query>
                </iq>
            """
            response = self.send_raw(delete_stanza)

            print("Solicitud de eliminación de cuenta enviada correctamente.")
            self.disconnect()
        except Exception as e:
            print(f"Error al enviar la solicitud de eliminación de cuenta: {e}")

    async def interactuar_con_cliente(self):
        
        #asyncio.create_task(self.mostrar_mensajes_recibidos())

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
                print("7) Enviar un archivo.")
                print("8) Desconectarse.")
                print("9) Eliminar cuenta.")
                print("*****************************************************\n")

                opcion = await ainput("Ingrese el número de la opción deseada: \n")

                if opcion == '1':
                    print("Opcion elegida 1:")
                    await self.show_contacts()
                elif opcion == '2':
                    jid = input("Ingrese el JID del usuario que desea agregar: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 2:")
                    await self.add_contact(jid)
                elif opcion == '3':
                    jid = input("Ingrese el JID del usuario del que desea ver detalles: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 3:")
                    await self.contact_details(jid)
                elif opcion == '4':
                    jid = input("Ingrese el JID del usuario al que desea enviar el mensaje: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 4: \n")
                    await self.sendmessage(jid)
                elif opcion == '6':
                    mensaje = input("Ingrese el nuevo mensaje a definir: ")
                    print("Opcion elegida 6: \n")
                    await self.change_message(mensaje)
                elif opcion == '7':
                    jid = input("Ingrese el JID del usuario al que desea enviar el archivo: ")
                    jid = f"{jid}@alumchat.xyz"
                    file_path = "prueba.txt"  # Ruta predeterminada "prueba.txt"
                    custom_path = input(f"Ingrese la ruta del archivo (deje en blanco para usar la ruta predeterminada '{file_path}'): ")
                    if custom_path.strip():
                        file_path = custom_path.strip()
                    print("Opcion elegida 7: \n")
                    await self.send_file(jid, file_path)
                elif opcion == '8':
                    self.conectado = False
                    await self.disconnect()
                    exit()
                elif opcion == '9':
                    print("Opcion elegida 9: \n")
                    confirmation = input("Esta seguro de eliminar la cuenta (s/n): ")
                    if confirmation == 's':
                        self.conectado = False
                        self.delete_count()
                    else:
                        pass
                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
            except Exception as e:
                print(f"Error: {e}")

