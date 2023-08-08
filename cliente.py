import slixmpp
from aioconsole import ainput
import asyncio
import os
import time
from pathlib import Path
from aioxmpp import JID
from slixmpp.plugins.xep_0066 import stanza as xep_0066

class MyCliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.conectado = False
        self.usu = jid
        self.primera = True
        self.cont = []
        
        self.message_queue = asyncio.Queue()

        self.add_event_handler("session_start", self.start)
        self.add_event_handler('subscription_request', self.handle_subscription_request)
        self.add_event_handler('message', self.notify_received)

        self.register_plugin('xep_0045')

    async def start(self, event):
        self.send_presence()
        self.get_roster()
        self.conectado = True
        print("Sesión iniciada correctamente. \n")
        await self.get_roster()
        await self.show_contacts()
        asyncio.create_task(self.interactuar_con_cliente())
        asyncio.create_task(self.subscription_request())

    async def show_contacts(self):
        roster = self.client_roster
        contacts = roster.keys()
        contactos = []

        if not contacts and not self.primera:
            print("No tienes contactos.")
            return
        
        for jid in contacts:
            user = jid

            if '@conference' in user:
                continue

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
                if self.primera:
                    self.cont.append(user)
                contactos.append((user, show, status))
        if not self.primera:
            print("\nTus contactos son los siguentes: \n")
            for c in contactos:
                print(f"Contacto: {c[0]}")
                print(f"Estado: {c[1]}")
                print(f"Mensaje de estado: {c[2]}")
                print("")
            print("")
        self.primera = False

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
    
    async def sendmessage_group(self, to_jid):
        print(" - Estas en el chat del grupo ->")
        print(to_jid)
        print("Si deseas salir de este chat envia -> 'salir' \n")

        permanecer = True

        while  permanecer:
            message = await ainput('-> ')
            if message == 'salir':
                permanecer = False
            else:
                try:
                    self.send_message(mto=to_jid, mbody=message, mtype='groupchat')
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

    # async def send_file(self, to_jid, file_path):
    #     try:
    #         with open(file_path, 'rb') as file:
    #             filename = os.path.basename(file_path)
    #             html_body = f"<a href='file://{filename}'>{filename}</a>"
    #             mhtml = {'body': html_body}
    #             self.send_message(mto=to_jid, mbody=filename, mtype='chat', mhtml=mhtml)
    #             await self.send_file_transfer(to_jid, file)
    #         print("Archivo enviado con éxito.")
    #     except Exception as e:
    #         print(f"Error al enviar el archivo: {e}")

    # async def send_file_transfer(self, to_jid, file_path):
    #     try:
    #         with open(file_path, 'rb') as file:
    #             file_transfer = self['xep_0363'].upload(to_jid, file)
    #             await file_transfer.send()
    #         print("Archivo enviado con éxito.")
    #     except Exception as e:
    #         print(f"Error al enviar el archivo: {e}")

    async def send_file(self, to_jid, file_path):
        try:
            # Verificar si el archivo existe
            if not os.path.isfile(file_path):
                print(f"El archivo '{file_path}' no existe.")
                return

            # Obtener el nombre del archivo
            file_name = os.path.basename(file_path)

            # Crear un JID para el destinatario
            dest_jid = JID.fromstr(to_jid)

            # Preparar el mensaje con el archivo adjunto
            message = self.make_message(
                mto=dest_jid,
                mtype="chat",
                msubject=f"Archivo: {file_name}",
                mbody=f"Te estoy enviando el archivo '{file_name}'",
            )

            # Crear un elemento OOB y agregar el atributo 'url' utilizando append()
            oob = xep_0066.OOB()
            oob["url"] = f"file://{file_path}"
            oob["desc"] = f"Archivo: {file_name}"
            oob["expires"] = "3600"
            message.append(oob)

            # Enviar el mensaje
            message.send()

            print(f"Archivo '{file_name}' enviado exitosamente a {to_jid}")
        except Exception as e:
            print(f"Error al enviar el archivo: {str(e)}")

    async def crear_grupo(self, nombre_grupo):
        invitar = True
        try:
            self.plugin['xep_0045'].join_muc(nombre_grupo, self.boundjid.user)

            await asyncio.sleep(2)

            form = self.plugin['xep_0004'].make_form(ftype='submit', title='Configuracion de sala de chat')

            form['muc#roomconfig_roomname'] = nombre_grupo
            form['muc#roomconfig_persistentroom'] = '1'
            form['muc#roomconfig_publicroom'] = '1'
            form['muc#roomconfig_membersonly'] = '0'
            form['muc#roomconfig_allowinvites'] = '0'
            form['muc#roomconfig_enablelogging'] = '1'
            form['muc#roomconfig_changesubject'] = '1'
            form['muc#roomconfig_maxusers'] = '100'
            form['muc#roomconfig_whois'] = 'anyone'
            form['muc#roomconfig_roomdesc'] = 'Chat de prueba'
            form['muc#roomconfig_roomowners'] = [self.boundjid.user]

            await self.plugin['xep_0045'].set_room_config(nombre_grupo, config=form)

            print(f"Sala de chat '{nombre_grupo}' creada correctamente.")

            while invitar:
                usuario_invitado = await ainput("Ingresa el JID del usuario que deseas invitar al grupo: ")
                usuario_invitado = f"{usuario_invitado}@alumchat.xyz"

                await self.plugin['xep_0045'].invite(
                    room=nombre_grupo,
                    jid=usuario_invitado,
                    reason="¡Únete a nuestro grupo de chat!"
                )
                print(f"Se ha enviado una invitación a {usuario_invitado} para unirse al grupo.")
                invitar = await ainput("¿Deseas invitar a otro usuario al grupo? (s/n): ")
                if invitar == 'n':
                    invitar = False
                


        except Exception as e:
            print(f"Error al crear el grupo '{nombre_grupo}': {str(e)}")

    async def unirse_grupo(self, nombre_grupo):
        try:
            self.plugin['xep_0045'].join_muc(nombre_grupo, self.boundjid.user)
            print(f"Te has unido al grupo '{nombre_grupo}' correctamente.")
        except Exception as e:
            print(f"Error al unirse al grupo '{nombre_grupo}': {str(e)}")

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

    async def subscription_request(self):
        await asyncio.sleep(2)
        while self.conectado:
            await self.get_roster()
            roster = self.client_roster
            contacts = roster.keys()
            conta = []
            
            for jid in contacts:
                user = jid

                if '@conference' in user:
                    continue

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
                    conta.append(user)


            if conta == self.cont:
                pass
            else:
                print("Solicitud de suscripción recibida del usuario: ")
                for i in conta:
                    if i not in self.cont:
                        print(i)
                        self.cont.append(i)
            time.sleep(1)

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
                elif opcion == '5':
                    print("*****************************************************")
                    print("Menú de opciones:")
                    print("1) Crear un nuevo grupo.")
                    print("2) Ingresar a un grupo existente.")
                    print("3) Enviar mensaje a un grupo.")
                    print("*****************************************************")
                    opcion1 = await ainput("Ingrese el número de la opción deseada: \n")
                    if opcion1 == '1':
                        nombre_grupo = input("Ingrese el nombre del grupo que deseas crear: ")
                        nombre_grupo = f"{nombre_grupo}@conference.alumchat.xyz"
                        await self.crear_grupo(nombre_grupo)
                    elif opcion1 == '2':
                        nombre_grupo = input("Ingrese el nombre del grupo al que desea unirse: ")
                        nombre_grupo = f"{nombre_grupo}@conference.alumchat.xyz"
                        await self.unirse_grupo(nombre_grupo)
                    elif opcion1 == '3':
                        grupo = input("Ingrese el nombre del grupo al que desea enviar el mensaje: ")
                        grupo = f"{grupo}@conference.alumchat.xyz"
                        await self.sendmessage_group(grupo)

                elif opcion == '6':
                    mensaje = input("Ingrese el nuevo mensaje a definir: ")
                    print("Opcion elegida 6: \n")
                    await self.change_message(mensaje)
                elif opcion == '7':
                    jid = input("Ingrese el JID del usuario al que desea enviar el archivo: ")
                    jid = f"{jid}@alumchat.xyz"
                    file_path = "prueba.txt"
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

