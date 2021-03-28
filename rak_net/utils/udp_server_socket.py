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

import socket

class udp_server_socket:
    def __init__(self, hostname: str, port: int, version: int = 4) -> None:
        self.hostname: str = hostname
        self.port: int = port
        self.version: int = version
        if version == 4:
            self.socket: object = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        elif version == 6:
            self.socket: object = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.SOL_UDP)
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        else:
            raise Exception(f"Unknown address version {version}")
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            self.socket.bind((hostname, port))
        except socket.error:
            raise Exception(f"Failed to bind to {str(port)}")
        self.socket.setblocking(False)
            
    def receive(self) -> tuple:
        try:
            return self.socket.recvfrom(65535)
        except Exception:
            return
      
    def send(self, data: bytes, hostname: str, port: int) -> None:
        try:
            self.socket.sendto(data, (hostname, port))
        except Exception:
            return
        
    def close(self) -> None:
        self.socket.close()
