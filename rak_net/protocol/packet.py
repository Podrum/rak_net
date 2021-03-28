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

from binary_utils.binary_stream import binary_stream
from rak_net.utils.internet_address import internet_address
import socket

class packet(binary_stream):
    def decode_header(self) -> None:
        self.pos += 1
      
    def decode(self) -> None:
        self.decode_header()
        if hasattr(self, "decode_payload"):
            self.decode_payload()
        
    def encode_header(self) -> None:
        self.write_unsigned_byte(self.packet_id)
      
    def encode(self) -> None:
        self.encode_header()
        if hasattr(self, "encode_payload"):
            self.encode_payload()
        
    def read_address(self) -> object:
        version: int = self.read_unsigned_byte()
        if version == 4:
            hostname_parts: list = []
            for i in range(0, 4):
                hostname_parts.append(str(~self.read_unsigned_byte() & 0xff))
            hostname: str = ".".join(hostname_parts)
            port: int = self.read_unsigned_short_be()
            return internet_address(hostname, port, version)
        if version == 6:
            self.read_unsigned_short_le() # Domain
            port: int = self.read_unsigned_short_be()
            self.read_unsigned_int_be() # Test out IPV4 (Family)
            hostname: str = socket.inet_ntop(socket.AF_INET6, self.read(16))
            self.read_unsigned_int_be() # Test out IPV6 (Family)
            return internet_address(hostname, port, version)
      
    def write_address(self, address: object) -> None:
        if address.version == 4:
            self.write_unsigned_byte(address.version)
            hostname_parts: list = address.hostname.split(".")
            for part in hostname_parts:
                self.write_unsigned_byte(~int(part) & 0xff)
            self.write_unsigned_short_be(address.port)
        elif address.version == 6:
            self.write_unsigned_byte(address.version)
            self.write_unsigned_short_le(socket.AF_INET6) # Domain
            self.write_unsigned_short_be(address.port)
            self.write_unsigned_int_be(0) # Test out IPV4 (Family)
            self.write(socket.inet_pton(socket.AF_INET6, address.hostname))
            self.write_unsigned_int_be(0) # Test out IPV6 (Family)
            
    def read_string(self) -> str:
        return self.read(self.read_unsigned_short_be()).decode()
    
    def write_string(self, value: str) -> None:
        self.write_unsigned_short_be(len(value))
        self.write(value.encode())
