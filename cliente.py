import slixmpp

class MyCliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # Ping
        self.register_plugin('xep_0045') # MUC
        self.register_plugin('xep_0085') # Notifications
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub

        self.add_event_handler("session_start", self.start)

    def start(self, event):
        self.send_presence()
        self.get_roster()

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