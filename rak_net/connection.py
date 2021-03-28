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
from rak_net.protocol.ack import ack
from rak_net.protocol.frame_set import frame_set
from rak_net.protocol.nack import nack

class connection:
    def __init__(self, address: object, mtu_size: int, server: object):
        self.address: object = address
        self.mtu_size: int = mtu_size
        self.server: object = server
        self.connected: bool = False
        self.recovery_queue: dict = {}
        self.ack_queue: list = []
        self.nack_queue: list = []
        self.fragmented_packets: dict = {}
        self.compound_id: int = 0
        self.client_sequence_numbers: list = []
        self.server_sequence_number: int = 0
        self.client_sequence_number: int = 0
        self.server_reliable_frame_index: int = 0
        self.client_reliable_frame_index: int = 0
        self.queue: object = frame_set()
        self.channel_index: list = [0] * 32

    def handle(self, data: bytes) -> None:
        if data[0] == protocol_info.ack:
            handle_ack(data)
        elif data[0] == protocol_info.nack:
            handle_nack(data)
        elif protocol_info.frame_set_0 <= data[0] <= protocol_info.frame_set_f:
            handle_frame_set(data)
        
    def handle_ack(self, data: bytes) -> None:
        pass
    
    def handle_nack(self, data: bytes) -> None:
        pass
        
    def handle_frame_set(self, data: bytes) -> None:
        pass
