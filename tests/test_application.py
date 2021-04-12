"""Test Coroutine Application"""

from src.application import Server, Client


def _test_server():
    """Test coroutine server"""
    server = Server(5000)
    client = Client(5000)
    client.send("hi")
    server.mainloop()