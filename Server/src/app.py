import socket
import threading
import logging


import common
import config
from server import Server

class App:
    def __init__(self):
        self.server = Server(config.Config())

    def run(self):
        self.server.start()

if __name__ == '__main__':
    logging.basicConfig(filename='Server/logs/server.log', filemode='w', level=logging.DEBUG)
    while True:
        app = App()
        app.run()
