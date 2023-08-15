# Interactive Chat - AlumChat 💬🌟

Welcome to AlumChat, an interactive chat application implemented in Python using the `slixmpp` library for XMPP communication. Engage in lively conversations with individuals and groups while enjoying additional features such as sending file messages, updating your presence status, and more! 😄📝📎

## Requirements 📋

- Python 3.x
- Libraries: `slixmpp`, `aioconsole`

## Setup and Installation 🛠️

1. Begin by cloning this repository to your local machine.
2. Install the necessary dependencies by running `pip install slixmpp aioconsole` in your terminal. 🚀

## Usage 🚀

1. Start the chat by running the `main.py` script.
2. When prompted, enter your JID (Jabber ID) and password.
3. Explore the intuitive interactive menu to manage contacts and perform various chat actions.

## Features 🌟

- 📋 Display a list of contacts along with their availability status.
- ➕ Add new contacts to your list.
- 📞 Initiate one-on-one conversations.
- 🗣️ Participate in lively group discussions.
- 📄 Share files seamlessly within the chat.
- 🎉 Update your presence status and status message.
- 🚪 Safely disconnect from the chat when done.
- 🗑️ Delete your user account if needed.

## Clarifications and File Transfer 📄📦

When it comes to transferring files within AlumChat, a special encoding approach has been adopted for seamless exchange. Base64 encoding has been employed to enable efficient encoding and decoding of files, ensuring their successful transmission between users. It's important to note that both the sender and the recipient must adhere to this specific encoding format for file transfers to be successful.

The use of Base64 encoding allows files to be represented as text, making them compatible with the chat's text-based communication. However, keep in mind that this encoding might slightly increase the size of the transmitted data due to the nature of text-based representation.

To ensure a smooth file transfer experience:
1. **Sender:** Files are encoded using Base64 before being sent.
2. **Recipient:** Upon receiving a file message, the recipient decodes the Base64 data to retrieve the original file.

By following this standardized approach, AlumChat ensures that file transfers are consistent and reliable across different users' devices.

Feel free to refer to the code in the repository for more details on how file transfers are implemented using Base64 encoding.

If you have any questions or need further assistance regarding file transfers, don't hesitate to reach out or consult the [official documentation](https://slixmpp.readthedocs.io/) for additional information.

## Contribution 🤝

If you're eager to contribute to AlumChat's growth, don't hesitate to fork this repository and send pull requests loaded with bug fixes, features, or enhancements! 🌱💡📦

## Notes and References 📝🔗

- This project heavily relies on the powerful `slixmpp` library for XMPP communication. More details can be found in the [official documentation](https://slixmpp.readthedocs.io/).

## Credits and Acknowledgments 👏👤

Developed with passion by [Diego Franco](https://github.com/Franco-611).

---

Embark on your exciting chat journey with AlumChat! Should any questions or concerns arise, please don't hesitate to create an issue in this repository. Happy chatting! 🎉🌐📱
