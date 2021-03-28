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

from rak_net.constant.protocol_info import protocol_info
from rak_net.protocol.incompatible_protocol_version import incompatible_protocol_version
from rak_net.protocol.open_connection_reply_1 import open_connection_reply_1
from rak_net.protocol.open_connection_request_1 import open_connection_request_1

class open_connection_request_1_handler:
    @staticmethod
    def handle(data: bytes, address: object, server: object) -> bytes:
        packet: object = open_connection_request_1(data)
        packet.decode()
        if packet.protocol_version == protocol_info.protocol_version:
            new_packet: object = open_connection_reply_1()
            new_packet.magic: bytes = protocol_info.magic
            new_packet.server_guid: int = server.guid
            new_packet.use_security: bool = False
            new_packet.mtu_size: int = packet.mtu_size
        else:
            new_packet: object = incompatible_protocol_version()
            new_packet.protocol_version: int = protocol_info.protocol_version
            new_packet.magic: bytes = protocol_info.magic
            new_packet.server_guid: int = server.guid
        new_packet.encode()
        return new_packet.data
