## Author: Diego Franco

# Importamos las clases que vamos a utilizar
import slixmpp
from aioconsole import ainput
import asyncio
import time
import base64

# Creamos la clase que hereda de ClientXMPP
class MyCliente(slixmpp.ClientXMPP):
    # Definimos el constructor de la clase
    def __init__(self, jid, password):

        # Llamamos al constructor de la clase padre
        super().__init__(jid, password)

        # Se definene los atributos de la clase
        self.conectado = False
        self.usu = jid
        self.primera = True
        self.cont = []
        self.estados = []

        # Se definen los manejadores de eventos
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('message', self.recibir_mensaje)
        self.add_event_handler('groupchat_invite', self.aceptGroup)
        self.add_event_handler('changed_status', self.presence_handler)

        # Se registran los plugins
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0004')

    # Se define el metodo start que se ejecuta cuando se inicia la sesion
    async def start(self, event):
        # Se obtiene el roster al iniciar la sesion
        self.send_presence()
        self.get_roster()
        self.conectado = True
        print("Sesión iniciada correctamente. \n")
        await self.get_roster()
        await self.show_contacts()

        # Se definen los metodos que se ejecutarán en un hilo distinto
        asyncio.create_task(self.interactuar_con_cliente())
        asyncio.create_task(self.subscription_request())

    # Se define el metodo para mostrar los contactos
    async def show_contacts(self):
        # Se obtiene el roster y sus keys
        roster = self.client_roster
        contacts = roster.keys()
        contactos = []

        # Se recorren los contactos para saber si si hay o no
        if not contacts and not self.primera:
            print("No tienes contactos.")
            return
        
        # Se recorren los contactos para obtener su estado
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

                    # Se hace la codificacion de los estados
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
                    self.estados.append((user, show))
                contactos.append((user, show, status))
        
        # Se muestran los contactos
        if not self.primera:
            print("\nTus contactos son los siguentes: \n")
            for c in contactos:
                print(f"Contacto: {c[0]}")
                print(f"Estado: {c[1]}")
                print(f"Mensaje de estado: {c[2]}")
                print("")
            print("")
        self.primera = False

    # Se define el metodo para agegar un contacto
    async def add_contact(self, jid):
        # Se envia la solicitud de suscripcion
        self.send_presence_subscription(pto=jid)
        await self.get_roster()
        print("Contacto agregado correctamente.")

    # Se define el metodo para pedir informacion de un contacto en especifico
    async def contact_details(self, jid):
            # Se obtiene el roster y sus keys
            roster = self.client_roster
            contacts = roster.keys()

            # Se recorren los contactos para saber si si existe el contacto solicitado
            if jid in contacts:
                connection = roster.presence(jid)
                show = 'Desconectado'
                status = ''

                # Se recorren los contactos para obtener el estado del contacto indicado
                for answer, presence in connection.items():
                    if presence:
                        show = presence['show']
                    if presence['status']:
                        status = presence['status']

                    # Se hace la codificacion de los estados
                    if show == 'dnd':
                        show = 'Ocupado'
                    if show == 'xa':
                        show = 'No disponible'
                    if show == 'away':
                        show = 'Ausente'
                    if show == '':
                        show = 'Disponible'

                # Se muestra la informacion del contacto
                print("\nDetalles del contacto:\n")
                print(f"Usuario: {jid}")
                print(f"Estado: {show}")
                print(f"Mensaje de estado: {status}")
                print("")

            else: 
                print("El usuario no se encuentra en tus contactos.")
                return

    # Se define el metodo para mandar un mensaje a un contacto
    async def sendmessage(self, to_jid):
        # Se muestra el contacto al que se le va a mandar el mensaje y la manera de salir del "chat"
        print(" - Estas en el chat de ->")
        print(to_jid)
        print("Si deseas salir de este chat envia -> 'salir' \n")

        permanecer = True

        while  permanecer:
            # Se obtiene el mensaje a mandar
            message = await ainput('-> ')
            if message == 'salir':
                permanecer = False
            else:
                try:
                    # Se manda el mensaje
                    self.send_message(mto=to_jid, mbody=message, mtype='chat')
                except:
                    print("Error al enviar el mensaje.")
    
    # Se define el metodo para mandar un mensaje a un grupo
    async def sendmessage_group(self, to_jid):
        # Se muestra el grupo al que se le va a mandar el mensaje y la manera de salir del "chat"
        print(" - Estas en el chat del grupo ->")
        print(to_jid)
        print("Si deseas salir de este chat envia -> 'salir' \n")

        permanecer = True

        while  permanecer:
            # Se obtiene el mensaje a mandar
            message = await ainput('-> ')
            if message == 'salir':
                permanecer = False
            else:
                try:
                    # Se manda el mensaje
                    self.send_message(mto=to_jid, mbody=message, mtype='groupchat')
                except:
                    print("Error al enviar el mensaje.")
    
    # Se define el metodo para cambiar el mensaje de presencia
    async def change_message(self, msg):
        # Se cambia el mensaje de presencia
        estado  = ''
        self.send_presence(pshow=estado, pstatus=msg) 
        await self.get_roster()
        print("Mensaje de presencia cambiado correctamente.")

    # Se define el metodo para recibir mensajes
    async def recibir_mensaje(self, msg):
        # Se verifica si el mensaje es de tipo chat o normal
        if msg['type'] in ('chat', 'normal'):
            # Se verifica si el mensaje es un archivo
            if "file|" in msg['body']:
                # Se obtiene el archivo decodificado, la extension y el emisor
                extension = msg['body'].split('|')[1]
                archivo = msg['body'].split('|')[2]
                final = base64.b64decode(archivo.encode())
                
                # Se escribe un archivo con el nombre recibido y la extension recibida
                with open(f"recibido.{extension}", 'wb') as file:
                    file.write(final)

                message = f"Archivo recibido de {msg['from']}"

            else:
                # Si no es un archivo se muestra el mensaje normal
                message = f"Mensaje recibido de {msg['from']}: {msg['body']}"
            print(message)
    
        # Se verifica si el mensaje es de tipo groupchat
        if msg['type'] == 'groupchat':
            # Se obtiene el grupo y el emisor
            grupo = str(msg['from']).split('/')[0]
            emisor = str(msg['from']).split('/')[1]
            if emisor in self.usu:
                return
            # Se muestra el mensaje recibido
            message = f"Mensaje recibido del grupo {grupo} de {emisor}: {msg['body']}"
            print(message)

    # Se define el metodo para enviar un archivo
    async def send_file1(self, jid, file_path):
        try:
            # Se obtiene el archivo y se codifica, ademas de obtener la extension del mismo
            file_extension = file_path.split('.')[-1]
            with open(file_path, 'rb') as file:
                file_data = file.read()
                file_data_base64 = base64.b64encode(file_data).decode('utf-8')

            # Se cre el mensaje con el archivo codificado en un formato especifico
            message = "file|" + file_extension + "|" + file_data_base64 

            # Se envia el mensaje con el archivo codificado
            self.send_message(mto=jid, mbody=message, mtype='chat')
            print(f"File '{file_path}' enviado a {jid}")
        except Exception as e:
            print(f"Error sending file: {e}")

    # Se define el metodo para crear un grupo
    async def crear_grupo(self, nombre_grupo):
        invitar = True
        try:   
            # Se crea el grupo
            self.plugin['xep_0045'].join_muc(nombre_grupo, self.boundjid.user)

            await asyncio.sleep(2)

            # Se genera el formulario para configurar el grupo y se configura
            form = self.plugin['xep_0004'].make_form(ftype='submit', title='Configuracion de sala de chat')

            form['muc#roomconfig_roomname'] = nombre_grupo
            form['muc#roomconfig_persistentroom'] = '1'
            form['muc#roomconfig_publicroom'] = '1'
            form['muc#roomconfig_membersonly'] = '0'
            form['muc#roomconfig_allowinvites'] = '1'
            form['muc#roomconfig_enablelogging'] = '1'
            form['muc#roomconfig_changesubject'] = '1'
            form['muc#roomconfig_maxusers'] = '100'
            form['muc#roomconfig_whois'] = 'anyone'
            form['muc#roomconfig_roomdesc'] = 'Chat de prueba'
            form['muc#roomconfig_roomowners'] = [self.boundjid.user]
            
            # Se configura el grupo
            await self.plugin['xep_0045'].set_room_config(nombre_grupo, config=form)

            print(f"Sala de chat '{nombre_grupo}' creada correctamente.")

            # Se invita a los usuarios que se deseen
            while invitar:
                # Se obtiene el usuario a invitar
                usuario_invitado = await ainput("Ingresa el JID del usuario que deseas invitar al grupo: ")
                usuario_invitado = f"{usuario_invitado}@alumchat.xyz"

                # Se envia la invitacion
                self.plugin['xep_0045'].invite(
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

    # Se define el metodo para unirse a un grupo
    async def unirse_grupo(self, nombre_grupo):
        try:
            # Se une al grupo con el nombre recibido
            self.plugin['xep_0045'].join_muc(nombre_grupo, self.boundjid.user)
            print(f"Te has unido al grupo '{nombre_grupo}' correctamente.")
        except Exception as e:
            # Si no se puede unir al grupo, se muestra el error
            print(f"Error al unirse al grupo '{nombre_grupo}': {str(e)}")

    # Se define el metodo para autoaceptar invitaciones a grupos
    async def aceptGroup(self, group):
        try:    
            # Se obtiene el nombre del grupo
            nombre_grupo = group["from"]
            print(f"Se ha unido al grupo '{nombre_grupo}'.")

            # Se une al grupo
            self.plugin['xep_0045'].join_muc(nombre_grupo, self.boundjid.user)

            self.send_presence(pto=nombre_grupo, ptype="available")

        except:
            pass

    # Se define la funcion para eliminar una cuenta
    def delete_count(self):
        try:
            # Se crea la stanza para eliminar la cuenta
            delete_stanza = f"""
                <iq type="set" id="delete-account">
                <query xmlns="jabber:iq:register">
                    <remove jid="{self.usu}"/>
                </query>
                </iq>
            """
            # Se envia la stanza de eliminacion de cuenta
            response = self.send_raw(delete_stanza)

            print("Solicitud de eliminación de cuenta enviada correctamente.")
            # Se desconecta del servidor
            self.disconnect()
        except Exception as e:
            print(f"Error al enviar la solicitud de eliminación de cuenta: {e}")

    # Se define la funcion para estar pendiente de las solicitudes de suscripcion
    async def subscription_request(self):
        await asyncio.sleep(2)
        while self.conectado:
            # Se obtiene el roster de los nuevos contactos
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
                    # Se obtiene el estado de los contactos
                    for answer, presence in connection.items():
                        if presence:
                            show = presence['show']
                        if presence['status']:
                            status = presence['status']

                        # Se codifica el estado
                        if show == 'dnd':
                            show = 'Ocupado'
                        if show == 'xa':
                            show = 'No disponible'
                        if show == 'away':
                            show = 'Ausente'
                        if show == '':
                            show = 'Disponible'
                    conta.append(user)

            # Se verifica si hay nuevos contactos
            if conta == self.cont:
                pass
            else:
                for i in conta:
                    if i not in self.cont:
                        if i:
                            # Se muestra la solicitud de suscripcion nueva y se agrega a la lista de contactos ya existentes
                            print("Solicitud de suscripción recibida del usuario: ")
                            print(i)
                            self.cont.append(i)
            time.sleep(1)

    # Se define la funcion para identificar los cambios de estado de los contactos
    def presence_handler(self, presence):

        # Se obtiene el contacto con cambio de estado
        quien = presence['from']

        # Se verifica si el nuevo estado es ausente o desconectado y se indica
        if presence['type'] == 'available':
            # Si el contacto es un grupo, se ignora
            if '@conference' in quien.full:
                pass
            else:
                print(f"El contacto {presence['from']} está disponible")
        elif presence['type'] == 'unavailable':
            # Si el contacto es un grupo, se ignora
            if '@conference' in quien.full:
                pass
            else:
                print(f"El contacto {presence['from']} está no disponible")
    
    # Se define la funcion para interactuar con el cliente
    async def interactuar_con_cliente(self):

        while self.conectado:
            try:
                
                # Se muestra el menu de opciones
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

                # Se obtiene la opcion elegida
                opcion = await ainput("Ingrese el número de la opción deseada: \n")

                # Se verifica la opcion elegida
                if opcion == '1':

                    # Se muestra el estado de los contactos haciendo uso de la funcion show_contacts
                    print("Opcion elegida 1:")
                    await self.show_contacts()
                elif opcion == '2':

                    # Se obtiene el JID del usuario a agregar y se agrega haciendo uso de la funcion add_contact
                    jid = input("Ingrese el JID del usuario que desea agregar: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 2:")
                    await self.add_contact(jid)
                elif opcion == '3':

                    # Se obtiene el JID del usuario del que se desea ver detalles y se muestran haciendo uso de la funcion contact_details
                    jid = input("Ingrese el JID del usuario del que desea ver detalles: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 3:")
                    await self.contact_details(jid)
                elif opcion == '4':

                    # Se obtiene el JID del usuario con el que se desea chatear y se chatea haciendo uso de la funcion sendmessage
                    jid = input("Ingrese el JID del usuario al que desea enviar el mensaje: ")
                    jid = f"{jid}@alumchat.xyz"
                    print("Opcion elegida 4: \n")
                    await self.sendmessage(jid)
                elif opcion == '5':

                    # Se muestra un submenu para las opciones de grupos
                    print("*****************************************************")
                    print("Menú de opciones:")
                    print("1) Crear un nuevo grupo.")
                    print("2) Ingresar a un grupo existente.")
                    print("3) Enviar mensaje a un grupo.")
                    print("*****************************************************")

                    # Se obtiene la opcion elegida
                    opcion1 = await ainput("Ingrese el número de la opción deseada: \n")
                    if opcion1 == '1':

                        # Se obtiene el nombre del grupo a crear y se crea haciendo uso de la funcion crear_grupo
                        nombre_grupo = input("Ingrese el nombre del grupo que deseas crear: ")
                        nombre_grupo = f"{nombre_grupo}@conference.alumchat.xyz"
                        await self.crear_grupo(nombre_grupo)
                    elif opcion1 == '2':

                        # Se obtiene el nombre del grupo al que se desea unir y se une haciendo uso de la funcion unirse_grupo
                        nombre_grupo = input("Ingrese el nombre del grupo al que desea unirse: ")
                        nombre_grupo = f"{nombre_grupo}@conference.alumchat.xyz"
                        await self.unirse_grupo(nombre_grupo)
                    elif opcion1 == '3':

                        # Se obtiene el nombre del grupo al que se desea enviar el mensaje y se envia haciendo uso de la funcion sendmessage_group
                        grupo = input("Ingrese el nombre del grupo al que desea enviar el mensaje: ")
                        grupo = f"{grupo}@conference.alumchat.xyz"
                        await self.sendmessage_group(grupo)
                elif opcion == '6':

                    # Se obtiene el mensaje a definir y se define haciendo uso de la funcion change_message
                    mensaje = input("Ingrese el nuevo mensaje a definir: ")
                    print("Opcion elegida 6: \n")
                    await self.change_message(mensaje)
                elif opcion == '7':

                    # Se obtiene el JID del usuario al que se desea enviar el archivo y la ruta del archivo a enviar, y se envia haciendo uso de la funcion send_file1
                    jid = input("Ingrese el JID del usuario al que desea enviar el archivo: ")
                    jid = f"{jid}@alumchat.xyz"
                    file_path = "prueba.txt"
                    custom_path = input(f"Ingrese la ruta del archivo (deje en blanco para usar la ruta predeterminada '{file_path}'): ")
                    if custom_path.strip():
                        file_path = custom_path.strip()
                    print("Opcion elegida 7: \n")
                    await self.send_file1(jid, file_path)
                elif opcion == '8':

                    # Se desconecta el cliente haciendo uso de la funcion disconnect
                    self.conectado = False
                    await self.disconnect()
                elif opcion == '9':

                    # Se elimina la cuenta haciendo uso de la funcion delete_count luego de una confirmacion
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


## Algunas de las funciones fueron creadas por IA y modificadas por mi para adaptarlas a los requerimientos del proyecto. Ademas de ello se puede tener como referencia el siguiente enlace: https://slixmpp.readthedocs.io/