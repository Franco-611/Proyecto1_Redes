import slixmpp

class XMPPClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
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