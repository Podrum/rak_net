################################################################################
#                                                                              #
#  ____           _                                                            #
# |  _ \ ___   __| |_ __ _   _ _ __ ___                                        #
# | |_) / _ \ / _` | '__| | | | '_ ` _ \                                       #
# |  __/ (_) | (_| | |  | |_| | | | | | |                                      #
# |_|   \___/ \__,_|_|   \__,_|_| |_| |_|                                      #
#                                                                              #
# Copyright 2021 Podrum Studios                                                #
#                                                                              #
# Permission is hereby granted, free of charge, to any person                  #
# obtaining a copy of this software and associated documentation               #
# files (the "Software"), to deal in the Software without restriction,         #
# including without limitation the rights to use, copy, modify, merge,         #
# publish, distribute, sublicense, and/or sell copies of the Software,         #
# and to permit persons to whom the Software is furnished to do so,            #
# subject to the following conditions:                                         #
#                                                                              #
# The above copyright notice and this permission notice shall be included      #
# in all copies or substantial portions of the Software.                       #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
#                                                                              #
################################################################################

from rak_net.connection import connection
from rak_net.constant.protocol_info import protocol_info
from rak_net.handler.offline_ping_handler import offline_ping_handler
from rak_net.handler.open_connection_request_1_handler import open_connection_request_1_handler
from rak_net.handler.open_connection_request_2_handler import open_connection_request_2_handler
from rak_net.utils.internet_address import internet_address
from rak_net.utils.udp_server_socket import udp_server_socket
import random
import sys

class server:
    def __init__(self, hostname: str, port: int, ipv: int = 4) -> None:
        self.address: object = internet_address(hostname, port, ipv)
        self.guid: int = random.randint(0, sys.maxsize)
        self.socket: object = udp_server_socket(hostname, port, ipv)
        self.connections: dict = {}
            
    def add_connection(self, address: object, mtu_size: int) -> None:
        self.connections[address.token] = connection(address, mtu_size, self)
        
    def remove_connection(self, address: object) -> None:
        if address.token in self.connections:
            del self.connections[address.token]
            
    def get_connection(self, address: object) -> object:
        if address.token in self.connections:
            return self.connections[address.token]
            
    def send_data(self, data: bytes, address: object) -> None:
        self.socket.send(data, address.hostname, address.port)

    def handle(self) -> None:
        recv = self.socket.receive()
        if recv is not None:
            address: object = internet_address(recv[1][0], recv[1][1])
            if address.token in self.connections:
                self.get_connection(address).handle(recv[0])
            elif recv[0][0] == protocol_info.offline_ping:
                self.send_data(offline_ping_handler.handle(recv[0], address, self), address)
            elif recv[0][0] == protocol_info.open_connection_request_1:
                self.send_data(open_connection_request_1_handler.handle(recv[0], address, self), address)
            elif recv[0][0] == protocol_info.open_connection_request_2:
                self.send_data(open_connection_request_2_handler.handle(recv[0], address, self), address)
        for connection in dict(self.connections).values():
            connection.update()
