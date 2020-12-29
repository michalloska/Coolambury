import logging
import threading
import sys
import json
import msghandling as mh
import networking as nw

class Server:
    def __init__(self):
        self._resources = {}
        self._resources['rooms'] = {}
        self._resources['clients'] = []
        self._load_config_file()
        self._server_socket = nw.create_and_bind_socket(self._resources['config'])

        self._map_message_handlers()
        logging.debug('[SERVER] Initializing server...')

    def _load_config_file(self):
        try:
            config_path = sys.argv[1]
            with open(config_path, 'r') as config_file:
                self._resources['config'] = json.load(config_file)
        except:
            logging.error('[SERVER] Error occurred when loading configuration file!')
            exit()

    def _map_message_handlers(self):
        self._msg_mapping = {
                                'CreateRoomReq': mh.handle_CreateRoomReq,
                                'JoinRoomReq': mh.handle_JoinRoomReq,
                                'WriteChatReq': mh.handle_ChatMessageReq,
                                'ExitClientReq': mh.handle_ExitClientReq
                             }


    def start(self):
        logging.debug('[SERVER] server is starting...')
        self._server_socket.listen()

        while True:
            conn, addr = self._server_socket.accept()

            new_client = nw.ClientConnection(conn, addr, self._resources, self._msg_mapping)
            self._resources['clients'].append(new_client)
            thread = threading.Thread(target=new_client.handle_client_messages)
            thread.start()

            logging.debug('[SERVER] Active connections: {}'.format(threading.activeCount() - 1))

                                                     
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    coolambury_server = Server()
    coolambury_server.start()
    