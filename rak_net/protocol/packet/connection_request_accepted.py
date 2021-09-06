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

from rak_net.protocol.packet.packet import Packet
from rak_net.protocol.protocol_info import ProtocolInfo
from rak_net.utils.internet_address import InternetAddress


class ConnectionRequestAccepted(Packet):
    def __init__(self, data: bytes = b"", pos: int = 0):
        super().__init__(data, pos)
        self.packet_id: int = ProtocolInfo.CONNECTION_REQUEST_ACCEPTED
        self.client_address: InternetAddress = InternetAddress("255.255.255.255", 0)
        self.system_index: int = 0
        self.system_addresses: list[InternetAddress] = []
        self.request_timestamp: int = 0
        self.accepted_timestamp: int = 0
  
    def decode_payload(self) -> None:
        self.client_address = self.read_address()
        self.system_index = self.read_unsigned_short_be()
        self.system_addresses.clear()
        for i in range(0, 20):
            self.system_addresses.append(self.read_address())
        self.request_timestamp = self.read_unsigned_long_be()
        self.accepted_timestamp = self.read_unsigned_long_be()
        
    def encode_payload(self) -> None:
        self.write_address(self.client_address)
        self.write_unsigned_short_be(self.system_index)
        for address in self.system_addresses:
            self.write_address(address)
        self.write_unsigned_long_be(self.request_timestamp)
        self.write_unsigned_long_be(self.accepted_timestamp)
