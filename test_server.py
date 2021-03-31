from rak_net.server import server

rak_server: object = server("MCPE;Dedicated Server;428;1.16.210;0;10;13253860892328930865;Bedrock level;Survival;1;19132;19133;", "0.0.0.0", 19132)
    
while True:
    rak_server.handle()
