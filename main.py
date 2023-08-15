## Author: Diego Franco

# Importamos las clases que vamos a utilizar
from cliente import MyCliente
import xmpp
import asyncio

# Función para registrar una cuenta
def registrar_cuenta(jid, password):
        
    # Creamos un objeto JID
	jid = xmpp.JID(jid)
    # Creamos un objeto cliente
	account = xmpp.Client(jid.getDomain(), debug=[])
    
    # Nos conectamos al servidor
	account.connect()
	return bool(
	    xmpp.features.register(account, jid.getDomain(), {
	        'username': jid.getNode(),
	        'password': password
	    }))

# Función para iniciar sesión
def iniciar_sesion(jid, password):

    # Creamos un objeto cliente
    xmpp = MyCliente(jid, password)

    # Nos conectamos al servidor
    xmpp.connect(disable_starttls=True)
    xmpp.process(forever=False)

# Función para cerrar el bucle de eventos
def cerrar_bucle_eventos():

    # Cerramos el bucle de eventos
    loop = asyncio.get_event_loop()
    loop.stop()
    loop.close()

# Función principal
if __name__ == "__main__":
    # Se muestra el mensaje de bienvenida
    print("Bienvenido al cliente de mensajería XMPP")
    # Configuramos el bucle de eventos
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    while True:
        # Mostramos el menú de opciones
        choice = input("¿Que deseas realizar? \n  (1) Crear un nuevo usuario \n  (2) Iniciar sesión con uno existente  \n  (3) Salir \n ")

        # Dependiendo de la opción elegida, se ejecuta una acción

        if choice == "1":
            # Se solicitan los datos para crear la cuenta
            jid = input("Nuevo JID: ")
            password = input("Nueva contraseña: ")

            jid = f"{jid}@alumchat.xyz"

            if registrar_cuenta(jid, password) :
                print("¡Cuenta creada exitosamente!")
            else:
                print("Error al crear la cuenta. Por favor, intente nuevamente.")
                break
            
            # Se da la opcion de iniciar sesión con la cuenta recién creada
            iniciar_sesion_choice = input("¿Deseas iniciar sesión con la cuenta recién creada? (s/n): ")
            if iniciar_sesion_choice.lower() == "s":
                iniciar_sesion(jid, password)

            print("¡Hasta luego!")
            break

        elif choice == "2":
            # Se solicitan los datos para iniciar sesión
            jid = input("JID: ")
            password = input("Contraseña: ")

            jid = f"{jid}@alumchat.xyz"
            iniciar_sesion(jid, password)
            break

        elif choice == "3":
            # Se cierra el bucle de eventos y se termina el programa
            cerrar_bucle_eventos()
            print("¡Hasta luego!")
            break

        else:
            print("Opción inválida. Por favor, elige '1' o '2' o '3'.")
