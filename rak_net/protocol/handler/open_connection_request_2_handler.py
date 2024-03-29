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

from rak_net.protocol.packet.open_connection_reply_2 import OpenConnectionReply2
from rak_net.protocol.packet.open_connection_request_2 import OpenConnectionRequest2
from rak_net.protocol.protocol_info import ProtocolInfo
from rak_net.utils.internet_address import InternetAddress


class OpenConnectionRequest2Handler:
    @staticmethod
    def handle(data: bytes, address: InternetAddress, server) -> bytes:
        packet: OpenConnectionRequest2 = OpenConnectionRequest2(data)
        packet.decode()
        new_packet: OpenConnectionReply2 = OpenConnectionReply2()
        new_packet.magic = ProtocolInfo.MAGIC
        new_packet.server_guid = server.guid
        new_packet.client_address = address
        new_packet.mtu_size = packet.mtu_size
        new_packet.use_encryption = False
        new_packet.encode()
        server.add_connection(address, packet.mtu_size)
        return new_packet.data
