from rak_net.server import server

rak_server: object = server("MCPE;Dedicated Server;428;1.16.210;0;10;13253860892328930865;Bedrock level;Survival;1;19132;19133;", "0.0.0.0", 19132)

class interface:
    def on_frame(self, packet: object, connection: object) -> None:
        print(hex(packet.body[0]))
        
    def on_disconnect(self, connection: object) -> None:
        print(f"{connection.address.token} has disconnected.")
        
    def on_new_incoming_connection(self, connection: object) -> None:
        print(f"{connection.address.token} successfully connected!")
        
rak_server.interface: object = interface()
    
while True:
    rak_server.handle()
