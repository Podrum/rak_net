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

from rak_net.connection import Connection
from rak_net.protocol.handler.offline_ping_handler import OfflinePingHandler
from rak_net.protocol.handler.open_connection_request_1_handler import OpenConnectionRequest1Handler
from rak_net.protocol.handler.open_connection_request_2_handler import OpenConnectionRequest2Handler
from rak_net.protocol.protocol_info import ProtocolInfo
from rak_net.utils.internet_address import InternetAddress
from rak_net.utils.udp_socket import UdpSocket
import random
import sys
import time


class Server:
    def __init__(self, protocol_version: int, hostname: str, port: int, ipv: int = 4, tps: int = 100) -> None:
        self.tick_sleep_time: float = 1 / tps
        self.protocol_version: int = protocol_version
        self.address: InternetAddress = InternetAddress(hostname, port, ipv)
        self.guid: int = random.randint(0, sys.maxsize)
        self.socket: UdpSocket = UdpSocket(True, ipv, hostname, port)
        self.connections: dict[(str, Connection)] = {}
        self.start_time: int = int(time.time() * 1000)
            
    def get_time_ms(self) -> int:
        return int(time.time() * 1000) - self.start_time
            
    def add_connection(self, address: InternetAddress, mtu_size: int) -> None:
        self.connections[address.token] = Connection(address, mtu_size, self)
        
    def remove_connection(self, address: InternetAddress) -> None:
        if address.token in self.connections:
            del self.connections[address.token]
            
    def get_connection(self, address: InternetAddress) -> Connection:
        if address.token in self.connections:
            return self.connections[address.token]
            
    def send_data(self, data: bytes, address: InternetAddress) -> None:
        self.socket.send(data, address.hostname, address.port)
            
    def tick(self) -> None:
        for connection in dict(self.connections).values():
            connection.update()

    def handle(self) -> None:
        recv: tuple = self.socket.receive()
        if recv[0]:
            address: InternetAddress = InternetAddress(recv[1][0], recv[1][1])
            if address.token in self.connections:
                self.get_connection(address).handle(recv[0])
            elif recv[0][0] in [ProtocolInfo.OFFLINE_PING, ProtocolInfo.OFFLINE_PING_OPEN_CONNECTIONS]:
                self.send_data(OfflinePingHandler.handle(recv[0], address, self), address)
            elif recv[0][0] == ProtocolInfo.OPEN_CONNECTION_REQUEST_1:
                self.send_data(OpenConnectionRequest1Handler.handle(recv[0], address, self), address)
            elif recv[0][0] == ProtocolInfo.OPEN_CONNECTION_REQUEST_2:
                self.send_data(OpenConnectionRequest2Handler.handle(recv[0], address, self), address)
