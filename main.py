from cliente import MyCliente
import xmpp
import asyncio

def registrar_cuenta(jid, password):
    
	jid = xmpp.JID(jid)
	account = xmpp.Client(jid.getDomain(), debug=[])
	account.connect()
	return bool(
	    xmpp.features.register(account, jid.getDomain(), {
	        'username': jid.getNode(),
	        'password': password
	    }))


def iniciar_sesion(jid, password):
    xmpp = MyCliente(jid, password)

    xmpp.connect(disable_starttls=True)
    xmpp.process(forever=False)



if __name__ == "__main__":
    print("Bienvenido al cliente de mensajería XMPP")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    while True:
        choice = input("¿Que deseas realizar? \n  (1) Crear un nuevo usuario \n  (2) Iniciar sesión con uno existente  \n  (3) Salir \n ")

        if choice == "1":
            jid = input("Nuevo JID: ")
            password = input("Nueva contraseña: ")

            jid = f"{jid}@alumchat.xyz"

            if registrar_cuenta(jid, password) :
                print("¡Cuenta creada exitosamente!")
            else:
                print("Error al crear la cuenta. Por favor, intente nuevamente.")
                break
            
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
