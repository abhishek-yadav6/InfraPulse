from backend.services.server_service import get_servers

servers = get_servers()

for server in servers:
    print(server)