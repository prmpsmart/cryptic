# def recv(self, read: int = 1024):
#     try:
#         return self.socket.recv(read)
#     except Exception:
#         if self.socket:
#             self.socket.close()
#         self.socket = None
#         self.connected = False
#         self.keep_alive = False
#         raise

# def send(self, data: bytes) -> int:
#     try:
#         return self.socket.send(data)
#     except:
#         self.keep_alive = False
