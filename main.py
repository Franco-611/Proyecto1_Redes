from cliente import XMPPClient
from getpass import getpass

def registrar_cuenta(jid, password):
    xmpp = XMPPClient(jid, password)
    xmpp.use_tls = True
    xmpp.connect(address=('alumchat.xyz', 5222))

    if xmpp.connect():
        while not xmpp.state.ensure('session_started'):
            pass

        try:
            xmpp.register_plugin("xep_0077")
            xmpp.register_plugin("xep_0030")
            xmpp['xep_0077'].register(jid, password)
            print("Cuenta registrada exitosamente.")
        except Exception as e:
            print(f"Error al registrar la cuenta: {e}")

        xmpp.disconnect()
    else:
        print("Error en la conexión.")

def iniciar_sesion(jid, password):
    xmpp = XMPPClient(jid, password)
    xmpp.use_tls = False 
    xmpp.connect(address=('alumchat.xyz', 5222)) 

    if xmpp.connect():

        while not xmpp.state.ensure('session_started'):
            pass

        print("Sesión iniciada correctamente.")

        interactuar_con_cliente(xmpp)

    

        while True:
            try:
                command = input("Ingrese el comando (o 'exit' para salir): ")
                if command.lower() == 'exit':
                    break
                else:
                    eval(command)
            except Exception as e:
                print(f"Error: {e}")
        xmpp.disconnect()
    else:
        print("Error en la conexión. No se pudo iniciar sesión.")

def interactuar_con_cliente(xmpp):

    print("Comandos disponibles:")
    print("1. show_contacts() -> Mostrar todos los contactos y su estado.")
    print("2. add_contact(jid) -> Agregar un usuario a los contactos.")
    print("3. contact_details(jid) -> Mostrar detalles de contacto de un usuario.")
    print("4. send_message(to_jid, message) -> Enviar un mensaje a un usuario.")

    while True:
        try:
            opcion = input("Ingrese el número de la opción (o '5' para salir): ")
            if opcion == '1':
                xmpp.show_contacts()
            elif opcion == '2':
                jid = input("Ingrese el JID del usuario que desea agregar: ")
                xmpp.add_contact(jid)
            elif opcion == '3':
                jid = input("Ingrese el JID del usuario del que desea ver detalles: ")
                xmpp.contact_details(jid)
            elif opcion == '4':
                jid = input("Ingrese el JID del usuario al que desea enviar el mensaje: ")
                message = input("Ingrese el mensaje: ")
                xmpp.send_message(jid, message)
            elif opcion == '5':
                break
            else:
                print("Opción inválida. Por favor, ingrese un número válido.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Bienvenido al cliente de mensajería XMPP")

    while True:
        choice = input("¿Que deseas realizar? \n  (1) Crear un nuevo usuario \n  (2) Iniciar sesión con uno existente  \n  (3) Salir \n  -> ")

        if choice == "1":
            jid = input("Nuevo JID: ")
            password = input("Nueva contraseña: ")

            jid = f"{jid}@alumchat.xyz"

            registrar_cuenta(jid, password)
            
            iniciar_sesion_choice = input("¿Deseas iniciar sesión con la cuenta recién creada? (s/n): ")
            if iniciar_sesion_choice.lower() == "s":
                iniciar_sesion(jid, password)

            print("¡Hasta luego!")
            break

        elif choice == "2":
            jid = input("JID: ")
            password = input("Contraseña: ")

            jid = f"{jid}@alumchat.xyz"
            iniciar_sesion(jid, password)
            break

        elif choice == "3":
            print("¡Hasta luego!")
            break

        else:
            print("Opción inválida. Por favor, elige '1' o '2' o '3'.")
