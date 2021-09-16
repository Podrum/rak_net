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

from copy import copy
from rak_net.protocol.handler.online_ping_handler import OnlinePingHandler
from rak_net.protocol.handler.connection_request_handler import ConnectionRequestHandler
from rak_net.protocol.handler.connection_request_accepted_handler import ConnectionRequestAcceptedHandler
from rak_net.protocol.packet.ack import Ack
from rak_net.protocol.packet.frame import Frame
from rak_net.protocol.packet.frame_set import FrameSet
from rak_net.protocol.packet.nack import Nack
from rak_net.protocol.packet.new_incoming_connection import NewIncomingConnection
from rak_net.protocol.packet.online_ping import OnlinePing
from rak_net.protocol.packet.online_pong import OnlinePong
from rak_net.protocol.protocol_info import ProtocolInfo
from rak_net.utils.internet_address import InternetAddress
from rak_net.utils.reliability_tool import ReliabilityTool
from time import time


class Connection:
    def __init__(self, address: InternetAddress, mtu_size: int, server) -> None:
        self.address: InternetAddress = address
        self.mtu_size: int = mtu_size
        self.server = server
        self.connected: bool = False
        self.recovery_queue: dict[(int, FrameSet)] = {}
        self.ack_queue: list[int] = []
        self.nack_queue: list[int] = []
        self.fragmented_packets: dict[(int, (int, Frame))] = {}
        self.compound_id: int = 0
        self.receive_sequence_numbers: list[int] = []
        self.send_sequence_number: int = 0
        self.receive_sequence_number: int = 0
        self.send_reliable_frame_index: int = 0
        self.receive_reliable_frame_index: int = 0
        self.queue: FrameSet = FrameSet()
        self.send_order_channel_index: list[int] = [0] * 32
        self.send_sequence_channel_index: list[int] = [0] * 32
        self.last_receive_time: float = time()
        self.ms: int = 0
        self.last_ping_time: float = time()
    
    def update(self):
        if (time() - self.last_receive_time) >= 10:
            self.disconnect()
        if self.connected:
            if time() - self.last_ping_time >= 1:
                self.last_ping_time = time()
                self.ping()
        self.send_ack_queue()
        self.send_nack_queue()
        self.send_queue()
        
    def ping(self) -> None:
        packet: OnlinePing = OnlinePing()
        packet.client_timestamp = self.server.get_time_ms()
        packet.encode()
        new_frame: Frame = Frame()
        new_frame.reliability = 0
        new_frame.body = packet.data
        self.add_to_queue(new_frame)
            
    def send_data(self, data: bytes) -> None:
        self.server.send_data(data, self.address)

    def handle(self, data: bytes) -> None:
        self.last_receive_time = time()
        if data[0] == ProtocolInfo.ACK:
            self.handle_ack(data)
        elif data[0] == ProtocolInfo.NACK:
            self.handle_nack(data)
        elif (data[0] & ProtocolInfo.FRAME_SET) != 0:
            self.handle_frame_set(data)
        
    def handle_ack(self, data: bytes) -> None:
        packet: Ack = Ack(data)
        packet.decode()
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                del self.recovery_queue[sequence_number]
    
    def handle_nack(self, data: bytes) -> None:
        packet: Nack = Nack(data)
        packet.decode()
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                lost_packet: FrameSet = self.recovery_queue[sequence_number]
                lost_packet.sequence_number = self.send_sequence_number
                self.send_sequence_number += 1
                lost_packet.encode()
                self.send_data(lost_packet.data)
                del self.recovery_queue[sequence_number]
        
    def handle_frame_set(self, data: bytes) -> None:
        packet: FrameSet = FrameSet(data)
        packet.decode()
        if packet.sequence_number not in self.receive_sequence_numbers:
            if packet.sequence_number in self.nack_queue:
                self.nack_queue.remove(packet.sequence_number)
            self.receive_sequence_numbers.append(packet.sequence_number)
            self.ack_queue.append(packet.sequence_number)
            hole_size: int = packet.sequence_number - self.receive_sequence_number
            if hole_size > 0:
                for sequence_number in range(self.receive_sequence_number + 1, hole_size):
                    if sequence_number not in self.receive_sequence_numbers:
                        self.nack_queue.append(sequence_number)
            self.receive_sequence_number = packet.sequence_number
            for frame in packet.frames:
                if not ReliabilityTool.reliable(frame.reliability):
                    self.handle_frame(frame)
                else:
                    hole_size: int = frame.reliable_frame_index - self.receive_reliable_frame_index
                    if hole_size == 0:
                        self.handle_frame(frame)
                        self.receive_reliable_frame_index += 1
                        
    def handle_fragmented_frame(self, frame: Frame) -> None:
        if frame.compound_id not in self.fragmented_packets:
            self.fragmented_packets[frame.compound_id] = {frame.index: frame}
        else:
            self.fragmented_packets[frame.compound_id][frame.index] = frame
        if len(self.fragmented_packets[frame.compound_id]) == frame.compound_size:
            new_frame: Frame = Frame()
            new_frame.body = b""
            for i in range(0, frame.compound_size):
                new_frame.body += self.fragmented_packets[frame.compound_id][i].body
            del self.fragmented_packets[frame.compound_id]
            self.handle_frame(new_frame)
                        
    def handle_frame(self, frame: Frame) -> None:
        if frame.fragmented:
            self.handle_fragmented_frame(frame)
        else:
            if not self.connected:
                if frame.body[0] == ProtocolInfo.CONNECTION_REQUEST:
                    new_frame: Frame = Frame()
                    new_frame.reliability = 0
                    new_frame.body = ConnectionRequestHandler.handle(frame.body, self.address, self.server)
                    self.add_to_queue(new_frame)
                elif frame.body[0] == ProtocolInfo.CONNECTION_REQUEST_ACCEPTED:
                    new_frame: Frame = Frame()
                    new_frame.reliability = 0
                    new_frame.body = ConnectionRequestAcceptedHandler.handle(frame.body, self.address, self.server)
                    self.add_to_queue(new_frame)
                    self.connected = True
                elif frame.body[0] == ProtocolInfo.NEW_INCOMING_CONNECTION:
                    packet: NewIncomingConnection = NewIncomingConnection(frame.body)
                    packet.decode()
                    if packet.server_address.port == self.server.address.port:
                        self.connected = True
                        if hasattr(self.server, "interface"):
                            if hasattr(self.server.interface, "on_new_incoming_connection"):
                                self.server.interface.on_new_incoming_connection(self)
            elif frame.body[0] == ProtocolInfo.ONLINE_PING:
                new_frame: Frame = Frame()
                new_frame.reliability = 0
                new_frame.body = OnlinePingHandler.handle(frame.body, self.address, self.server)
                self.add_to_queue(new_frame)
            elif frame.body[0] == ProtocolInfo.ONLINE_PONG:
                packet: OnlinePong = OnlinePong(frame.body)
                packet.decode()
                self.ms = (self.server.get_time_ms() - packet.client_timestamp)
            elif frame.body[0] == ProtocolInfo.DISCONNECT:
                self.disconnect()
            else:
                if hasattr(self.server, "interface"):
                    if hasattr(self.server.interface, "on_frame"):
                        self.server.interface.on_frame(frame, self)
        
    def send_queue(self) -> None:
        if len(self.queue.frames) > 0:
            self.queue.sequence_number = self.send_sequence_number
            self.send_sequence_number += 1
            self.recovery_queue[self.queue.sequence_number] = self.queue
            self.queue.encode()
            self.send_data(self.queue.data)
            self.queue = FrameSet()
            
    def append_frame(self, frame: Frame, immediate: bool) -> None:
        if immediate:
            packet: FrameSet = FrameSet()
            packet.frames.append(frame)
            packet.sequence_number = self.send_sequence_number
            self.send_sequence_number += 1
            self.recovery_queue[packet.sequence_number] = packet
            packet.encode()
            self.send_data(packet.data)
        else:
            frame_size: int = frame.get_size()
            queue_size: int = self.queue.get_size()
            if frame_size + queue_size >= self.mtu_size:
                self.send_queue()
            self.queue.frames.append(frame)
            
    def add_to_queue(self, frame: Frame) -> None:
        if ReliabilityTool.ordered(frame.reliability):
            frame.ordered_frame_index = self.send_order_channel_index[frame.order_channel]
            self.send_order_channel_index[frame.order_channel] += 1
        elif ReliabilityTool.sequenced(frame.reliability):
            frame.ordered_frame_index = self.send_order_channel_index[frame.order_channel]
            frame.sequenced_frame_index = self.send_sequence_channel_index[frame.order_channel]
            self.send_sequence_channel_index[frame.order_channel] += 1
        if frame.get_size() > self.mtu_size:
            fragmented_body: list[bytes] = []
            for i in range(0, len(frame.body), self.mtu_size):
                fragmented_body.append(frame.body[i:i + self.mtu_size])
            for index, body in enumerate(fragmented_body):
                new_frame: Frame = Frame()
                new_frame.fragmented = True
                new_frame.reliability = frame.reliability
                new_frame.compound_id = self.compound_id
                new_frame.compound_size = len(fragmented_body)
                new_frame.index = index
                new_frame.body = body
                if ReliabilityTool.reliable(frame.reliability):
                    new_frame.reliable_frame_index = self.send_reliable_frame_index
                    self.send_reliable_frame_index += 1
                if ReliabilityTool.sequenced_or_ordered(frame.reliability):
                    new_frame.ordered_frame_index = frame.ordered_frame_index
                    new_frame.order_channel = frame.order_channel
                if ReliabilityTool.sequenced(frame.reliability):
                    new_frame.sequenced_frame_index = frame.sequenced_frame_index
                self.append_frame(new_frame, True)
            self.compound_id += 1
        else:
            if ReliabilityTool.reliable(frame.reliability):
                frame.reliable_frame_index = self.send_reliable_frame_index
                self.send_reliable_frame_index += 1
            self.append_frame(frame, False)
        
    def send_ack_queue(self) -> None:
        if len(self.ack_queue) > 0:
            packet: Ack = Ack()
            packet.sequence_numbers = copy(self.ack_queue)
            packet.encode()
            self.ack_queue.clear()
            self.send_data(packet.data)
                
    def send_nack_queue(self) -> None:
        if len(self.nack_queue) > 0:
            packet: Nack = Nack()
            packet.sequence_numbers = copy(self.nack_queue)
            packet.encode()
            self.nack_queue.clear()
            self.send_data(packet.data)
            
    def disconnect(self) -> None:
        new_frame: Frame = Frame()
        new_frame.reliability = 0
        new_frame.body = b"\x15"
        self.add_to_queue(new_frame)
        self.server.remove_connection(self.address)
        if hasattr(self.server, "interface"):
            if hasattr(self.server.interface, "on_disconnect"):
                self.server.interface.on_disconnect(self)
