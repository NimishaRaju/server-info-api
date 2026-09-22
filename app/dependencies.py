from services import ServerService

FILE_PATH = "servers.json"

def get_server_service() -> ServerService:
    return ServerService(file_path=FILE_PATH)
