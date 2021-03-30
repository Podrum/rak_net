from rak_net.server import server

rak_server = server("MCPE;Dedicated Server;390;1.14.60;0;10;13253860892328930865;Bedrock level;Survival;1;19132;19133;", "0.0.0.0", 19132)
while True:
    rak_server.handle()
