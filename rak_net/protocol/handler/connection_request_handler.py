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

from rak_net.protocol.packet.connection_request import ConnectionRequest
from rak_net.protocol.packet.connection_request_accepted import ConnectionRequestAccepted
from rak_net.utils.internet_address import InternetAddress
import time


class ConnectionRequestHandler:
    @staticmethod
    def handle(data: bytes, address: InternetAddress, server) -> bytes:
        packet: ConnectionRequest = ConnectionRequest(data)
        packet.decode()
        new_packet: ConnectionRequestAccepted = ConnectionRequestAccepted()
        new_packet.client_address = address
        new_packet.system_index = 0
        new_packet.server_guid = server.guid
        new_packet.system_addresses = [InternetAddress("255.255.255.255", 19132)] * 20
        new_packet.request_timestamp = packet.request_timestamp
        new_packet.accepted_timestamp = round(time.time() * 1000)
        new_packet.encode()
        return new_packet.data
