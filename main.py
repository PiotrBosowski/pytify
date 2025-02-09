from pytify import webserver
from pytify import settings

if __name__ == "__main__":
    webserver.run(host=settings.host, port=settings.port)
