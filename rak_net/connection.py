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
from rak_net.handler.online_ping_handler import online_ping_handler
from rak_net.handler.connection_request_handler import connection_request_handler
from rak_net.protocol.ack import ack
from rak_net.protocol.frame import frame
from rak_net.protocol.frame_set import frame_set
from rak_net.protocol.nack import nack
from rak_net.utils.reliability_tool import reliability_tool

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
            
    def send_data(self, data: bytes) -> None:
        self.server.send_data(data, self.address)

    def handle(self, data: bytes) -> None:
        if data[0] == protocol_info.ack:
            self.handle_ack(data)
        elif data[0] == protocol_info.nack:
            self.handle_nack(data)
        elif protocol_info.frame_set_0 <= data[0] <= protocol_info.frame_set_f:
            self.handle_frame_set(data)
        
    def handle_ack(self, data: bytes) -> None:
        packet: object = ack(data)
        packet.decode()
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                del self.recovery_queue[sequence_number]
    
    def handle_nack(self, data: bytes) -> None:
        packet: object = nack(data)
        packet.decode()
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                lost_packet: object = connection.recovery_queue[sequence_number]
                lost_packet.sequence_number: int = self.server_sequence_number
                self.server_sequence_number += 1
                lost_packet.encode()
                self.send_data(lost_packet.data)
                del self.recovery_queue[sequence_number]
        
    def handle_frame_set(self, data: bytes) -> None:
        packet: object = frame_set(data)
        packet.decode()
        if packet.sequence_number not in self.client_sequence_numbers:
            if packet.sequence_number in self.nack_queue:
                self.nack_queue.remove(packet.sequence_number)
            self.client_sequence_numbers.append(packet.sequence_number)
            self.ack_queue.append(packet.sequence_number)
            hole_size: int = packet.sequence_number - self.client_sequence_number
            if hole_size > 0:
                for sequence_number in range(self.client_sequence_number + 1, hole_size):
                    if sequence_number not in self.client_sequence_numbers:
                        self.nack_queue.append(sequence_number)
            self.client_sequence_number: int = packet.sequence_number
            for frame_1 in packet.frames:
                if not reliability_tool.reliable(frame_1.reliability):
                    self.handle_frame(frame_1)
                else:
                    hole_size: int = frame_1.reliable_frame_index - self.client_reliable_frame_index
                    if hole_size == 0:
                        self.handle_frame(frame_1)
                        self.client_reliable_frame_index += 1
                        
    def handle_frame(self, packet: object) -> None:
        print("Received Frame -> " + hex(packet.body[0]))
        
    def send_ack_queue(self) -> None:
        if len(self.ack_queue) > 0:
            packet: object = ack()
            packet.sequence_numbers: list = self.ack_queue
            self.ack_queue: list = []
            packet.encode()
            self.send_data(packet.data)
                
    def send_nack_queue(self) -> None:
        if len(self.nack_queue) > 0:
            packet: object = nack()
            packet.sequence_numbers: list = self.nack_queue
            self.nack_queue: list = []
            packet.encode()
            self.send_data(packet.data)
