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
from rak_net.protocol.new_incoming_connection import new_incoming_connection
from rak_net.utils.reliability_tool import reliability_tool

class connection:
    def __init__(self, address: object, mtu_size: int, server: object) -> None:
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
    
    def update(self):
        self.send_ack_queue()
        self.send_nack_queue()
        self.send_queue()
            
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
                lost_packet: object = self.recovery_queue[sequence_number]
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
                        
    def handle_fragmented_frame(self, packet: object) -> None:
        if packet.compound_id not in self.fragmented_packets:
            self.fragmented_packets[packet.compound_id]: dict = {packet.index: packet}
        else:
            self.fragmented_packets[packet.compound_id][packet.index]: int = packet
        if len(self.fragmented_packets[packet.compound_id]) == packet.compound_size:
            new_frame: object = frame()
            new_frame.body: bytes = b""
            for i in range(0, packet.compound_size):
                new_frame.body += self.fragmented_packets[packet.compound_id][i].body
            del self.fragmented_packets[packet.compound_id]
            self.handle_frame(new_frame)
                        
    def handle_frame(self, packet: object) -> None:
        if packet.fragmented:
            self.handle_fragmented_frame(packet)
        else:
            if not self.connected:
                if packet.body[0] == protocol_info.connection_request:
                    new_frame: object = frame()
                    new_frame.reliability: int = 0
                    new_frame.body: bytes = connection_request_handler.handle(packet.body, self.address, self.server)
                    self.add_to_queue(new_frame)
                elif packet.body[0] == protocol_info.new_incoming_connection:
                    packet_1: object = new_incoming_connection(packet.body)
                    packet_1.decode()
                    if packet_1.server_address.port == self.server.address.port:
                        self.connected: bool = True
                        if hasattr(self.server, "interface"):
                            if hasattr(self.server.interface, "on_new_incoming_connection"):
                                self.server.interface.on_new_incoming_connection(self)
            elif packet.body[0] == protocol_info.online_ping:
                new_frame: object = frame()
                new_frame.reliability: int = 0
                new_frame.body: bytes = online_ping_handler.handle(packet.body, self.address, self.server)
                self.add_to_queue(new_frame, False)
            elif packet.body[0] == protocol_info.disconnect:
                self.disconnect()
            else:
                if hasattr(self.server, "interface"):
                    if hasattr(self.server.interface, "on_frame"):
                        self.server.interface.on_frame(packet, self)
        
    def send_queue(self) -> None:
        if len(self.queue.frames) > 0:
            self.queue.sequence_number: int = self.server_sequence_number
            self.server_sequence_number += 1
            self.recovery_queue[self.queue.sequence_number]: object = self.queue
            self.queue.encode()
            self.send_data(self.queue.data)
            self.queue: object = frame_set()
            
    def add_to_queue(self, packet: object, is_imediate: bool = True) -> None:
        if reliability_tool.reliable(packet.reliability):
            packet.reliable_frame_index: int = self.server_reliable_frame_index
            self.server_reliable_frame_index += 1
            if packet.reliability == 3:
                packet.ordered_frame_index: int = self.channel_index[packet.order_channel]
                self.channel_index[packet.order_channel] += 1
        if packet.get_size() > self.mtu_size:
            fragmented_body: list = []
            for i in range(0, len(packet.body), self.mtu_size):
                fragmented_body.append(packet.body[i:i + self.mtu_size])
            for index, body in enumerate(fragmented_body):
                new_packet: object = frame()
                new_packet.fragmented: bool = True
                new_packet.reliability: int = packet.reliability
                new_packet.compound_id: int = self.compound_id
                new_packet.compound_size: int = len(fragmented_body)
                new_packet.index: int = index
                new_packet.body: bytes = body
                if index != 0:
                    new_packet.reliable_frame_index: int = self.server_reliable_frame_index
                    self.server_reliable_frame_index += 1
                if new_packet.reliability == 3:
                    new_packet.ordered_frame_index: int = packet.ordered_frame_index
                    new_packet.order_channel: int = packet.order_channel
                if is_imediate:
                    self.queue.frames.append(new_packet)
                    self.send_queue()
                else:
                    frame_size: int = new_packet.get_size()
                    queue_size: int = self.queue.get_size()
                    if frame_size + queue_size >= self.mtu_size:
                        self.send_queue()
                    self.queue.frames.append(new_packet)
            self.compound_id += 1
        else:
            if is_imediate:
                self.queue.frames.append(packet)
                self.send_queue()
            else:
                frame_size: int = packet.get_size()
                queue_size: int = self.queue.get_size()
                if frame_size + queue_size >= self.mtu_size:
                    self.send_queue()
                self.queue.frames.append(packet)
        
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
            
    def disconnect(self) -> None:
        new_frame: object = frame()
        new_frame.reliability: int = 0
        new_frame.body: bytes = b"\x15"
        self.add_to_queue(new_frame)
        self.server.remove_connection(self.address)
        if hasattr(self.server, "interface"):
            if hasattr(self.server.interface, "on_disconnect"):
                self.server.interface.on_disconnect(self)
