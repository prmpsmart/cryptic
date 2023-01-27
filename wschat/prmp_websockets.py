"""
+-+-+-+-+-------+-+-------------+-------------------------------+
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
"""

__all__ = (
    "PRMP_WebSocketServer",
    "PRMP_WebSocketHandler",
    "PRMP_WebSocketClient",
    "LOGGER",
    "TIME",
    "TIME2STRING",
    "logging",
)

import hmac, threading, hashlib, struct, socketserver, base64, os, logging, ssl, codecs, typing, socket, errno, datetime, time
from urllib.parse import urlparse
from http import client as HTTPStatus
import http.cookies

from base64 import encodebytes as base64encode


OPCODE = 15
FIN = MASKED = 128

OPCODE_STREAM = 0
OPCODE_TEXT = 1
OPCODE_BINARY = 2
OPCODE_CLOSE = 8
OPCODE_PING = 9
OPCODE_PONG = 10

HEADER_B1 = 1
HEADER_B2 = 3
LENGTH_SHORT = 4
LENGTH_LONG = 5
MASK = 6
PAYLOAD = 7
RSV = 112

MASK_SIZE = 4

NORMAL_PAYLOAD_LENGTH = 125
PAYLOAD_LEN_EXT16 = 126
PAYLOAD_LEN_EXT64 = 127
EXTENDED_PAYLOAD_LENGTH = 65535
HUGE_EXTENDED_PAYLOAD_LENGTH = 18446744073709551616

MAX_PAYLOAD = 33554432

STATUS_NORMAL = 1000
STATUS_GOING_AWAY = 1001
STATUS_PROTOCOL_ERROR = 1002
STATUS_UNSUPPORTED_DATA_TYPE = 1003
STATUS_STATUS_NOT_AVAILABLE = 1005
STATUS_ABNORMAL_CLOSED = 1006
STATUS_INVALID_PAYLOAD = 1007
STATUS_POLICY_VIOLATION = 1008
STATUS_MESSAGE_TOO_BIG = 1009
STATUS_INVALID_EXTENSION = 1010
STATUS_UNEXPECTED_CONDITION = 1011
STATUS_SERVICE_RESTART = 1012
STATUS_TRY_AGAIN_LATER = 1013
STATUS_BAD_GATEWAY = 1014
STATUS_TLS_HANDSHAKE_ERROR = 1015

VALID_CLOSE_STATUS = (
    STATUS_NORMAL,
    STATUS_GOING_AWAY,
    STATUS_PROTOCOL_ERROR,
    STATUS_UNSUPPORTED_DATA_TYPE,
    STATUS_INVALID_PAYLOAD,
    STATUS_POLICY_VIOLATION,
    STATUS_MESSAGE_TOO_BIG,
    STATUS_INVALID_EXTENSION,
    STATUS_UNEXPECTED_CONDITION,
    STATUS_SERVICE_RESTART,
    STATUS_TRY_AGAIN_LATER,
    STATUS_BAD_GATEWAY,
)


GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
ASCII = "ASCII"
UTF8 = "UTF-8"

DEFAULT_CLOSE_REASON = bytes("", encoding=UTF8)

HANDSHAKE_STR = (
    "HTTP/1.1 101 Switching Protocols\r\n"
    "Upgrade: WebSocket\r\n"
    "Connection: Upgrade\r\n"
    "Sec-WebSocket-Accept: %(acceptstr)s\r\n\r\n"
)

FAILED_HANDSHAKE_STR = (
    "HTTP/1.1 426 Upgrade Required\r\n"
    "Upgrade: WebSocket\r\n"
    "Connection: Upgrade\r\n"
    "Sec-WebSocket-Version: 13\r\n"
    "Content-Type: text/plain\r\n\r\n"
    "This service requires use of the WebSocket protocol\r\n"
)

SUPPORTED_REDIRECT_STATUSES = (
    HTTPStatus.MOVED_PERMANENTLY,
    HTTPStatus.FOUND,
    HTTPStatus.SEE_OTHER,
)
SUCCESS_STATUSES = SUPPORTED_REDIRECT_STATUSES + (HTTPStatus.SWITCHING_PROTOCOLS,)

DEFAULT_SOCKET_OPTION = [(socket.SOL_TCP, socket.TCP_NODELAY, 1)]
if hasattr(socket, "SO_KEEPALIVE"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1))
if hasattr(socket, "TCP_KEEPIDLE"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPIDLE, 30))
if hasattr(socket, "TCP_KEEPINTVL"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPINTVL, 10))
if hasattr(socket, "TCP_KEEPCNT"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPCNT, 3))

ADDRESS_TYPE = tuple[typing.Union[str, int]]
DATA = typing.Union[str, bytes]


LOGGER = logging.getLogger(__name__)
logging.basicConfig()

VERSION = 13


def TIME():
    return int(time.time())


def TIME2STRING(time: int = 0):
    time = time or TIME()
    return datetime.datetime.fromtimestamp(time).strftime("%d/%m/%Y ... %H:%M %p")


class PRMP_WebsocketProtocol:
    def __init__(self) -> None:

        self.header_buffer = bytearray()
        self.header_to_read = 2048

        self.fin = 0
        self.data = bytearray()
        self.opcode = 0
        self.has_mask = 0
        self.mask_array = None
        self.length = 0
        self.length_array = None
        self.index = 0
        self.request = None

        self.frag_start = False
        self.frag_type = OPCODE_BINARY
        self.frag_buffer = None
        self.frag_decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")
        self.state = HEADER_B1

        # restrict the size of header and payloawd for security reasons
        self.maxheader = EXTENDED_PAYLOAD_LENGTH + 1
        self.maxpayload = MAX_PAYLOAD

        self.socket: socket.socket = None
        self.connected = False
        self.keep_alive = True
        self.handshaked = False
        self.valid_client = False

    def _make_handshake_response(self, key: str) -> str:
        return HANDSHAKE_STR % dict(acceptstr=self._calculate_response_key(key))

    def _calculate_response_key(self, key: str) -> str:
        hash = hashlib.sha1(key.encode() + GUID.encode())
        response_key = base64.b64encode(hash.digest()).strip()
        return response_key.decode(ASCII)

    def _handlePacket(self):
        if self.opcode in [OPCODE_PONG, OPCODE_PING]:
            if len(self.data) > NORMAL_PAYLOAD_LENGTH:
                raise Exception(
                    "control frame length can not be > NORMAL_PAYLOAD_LENGTH"
                )

        elif self.opcode not in [
            OPCODE_CLOSE,
            OPCODE_STREAM,
            OPCODE_TEXT,
            OPCODE_BINARY,
        ]:
            # unknown or reserved opcode so just close
            raise Exception("unknown opcode")

        if self.opcode == OPCODE_CLOSE:
            status = STATUS_NORMAL
            reason = ""
            length = len(self.data)

            if length == 0:
                ...
            elif length >= 2:
                status = struct.unpack_from("!H", self.data[:2])[0]
                reason = self.data[2:]

                if not (status in VALID_CLOSE_STATUS or (3000 <= status < 5000)):
                    status = STATUS_PROTOCOL_ERROR

                if len(reason) > 0:
                    try:
                        reason = reason.decode("utf8", errors="strict")
                    except:
                        status = STATUS_PROTOCOL_ERROR
            else:
                status = STATUS_PROTOCOL_ERROR

            self.send_close(status, reason)
            return

        elif self.fin == 0:
            if self.opcode != OPCODE_STREAM:
                if self.opcode == OPCODE_PING or self.opcode == OPCODE_PONG:
                    raise Exception("control messages can not be fragmented")

                self.frag_type = self.opcode
                self.frag_start = True
                self.frag_decoder.reset()

                if self.frag_type == OPCODE_TEXT:
                    self.frag_buffer = []
                    utf_str = self.frag_decoder.decode(self.data, final=False)
                    if utf_str:
                        self.frag_buffer.append(utf_str)
                else:
                    self.frag_buffer = bytearray()
                    self.frag_buffer.extend(self.data)

            else:
                if self.frag_start is False:
                    raise Exception("fragmentation protocol error")

                if self.frag_type == OPCODE_TEXT:
                    utf_str = self.frag_decoder.decode(self.data, final=False)
                    if utf_str:
                        self.frag_buffer.append(utf_str)
                else:
                    self.frag_buffer.extend(self.data)

        else:
            if self.opcode == OPCODE_STREAM:
                if self.frag_start is False:
                    raise Exception("fragmentation protocol error")

                if self.frag_type == OPCODE_TEXT:
                    utf_str = self.frag_decoder.decode(self.data, final=True)
                    self.frag_buffer.append(utf_str)
                    self.data = "".join(self.frag_buffer)
                else:
                    self.frag_buffer.extend(self.data)
                    self.data = self.frag_buffer

                self.on_message()

                self.frag_decoder.reset()
                self.frag_type = OPCODE_BINARY
                self.frag_start = False
                self.frag_buffer = None

            elif self.opcode == OPCODE_PING:
                self.send_payload(False, self.data, opcode=OPCODE_PONG)
                self.on_ping()

            elif self.opcode == OPCODE_PONG:
                self.on_pong()

            else:
                if self.frag_start is True:
                    raise Exception("fragmentation protocol error")

                if self.opcode == OPCODE_TEXT:
                    try:
                        self.data = self.data.decode("utf8", errors="strict")
                    except Exception as exp:
                        raise Exception("invalid utf-8 payload")

                self.on_message()

    def _parseMessage(self, byte):
        # read in the header
        if self.state == HEADER_B1:

            self.fin = byte & FIN
            self.opcode = byte & OPCODE
            self.state = HEADER_B2

            self.index = 0
            self.length = 0
            self.length_array = bytearray()
            self.data = bytearray()

            rsv = byte & RSV
            if rsv != 0:
                raise Exception("RSV bit must be 0")

        elif self.state == HEADER_B2:
            mask = byte & FIN
            length = byte & PAYLOAD_LEN_EXT64

            if self.opcode == OPCODE_PING and length > NORMAL_PAYLOAD_LENGTH:
                raise Exception("ping packet is too large")

            if mask == MASKED:
                self.has_mask = True
            else:
                self.has_mask = False

            if length <= NORMAL_PAYLOAD_LENGTH:
                self.length = length

                # if we have a mask we must read it
                if self.has_mask is True:
                    self.mask_array = bytearray()
                    self.state = MASK
                else:
                    # if there is no mask and no payload we are done
                    if self.length <= 0:
                        try:
                            self._handlePacket()
                        finally:
                            self.state = HEADER_B1
                            self.data = bytearray()

                    # we have no mask and some payload
                    else:
                        # self.index = 0
                        self.data = bytearray()
                        self.state = PAYLOAD

            elif length == PAYLOAD_LEN_EXT16:
                self.length_array = bytearray()
                self.state = LENGTH_SHORT

            elif length == PAYLOAD_LEN_EXT64:
                self.length_array = bytearray()
                self.state = LENGTH_LONG

        elif self.state == LENGTH_SHORT:
            self.length_array.append(byte)

            if len(self.length_array) > 2:
                raise Exception("short length exceeded allowable size")

            if len(self.length_array) == 2:
                self.length = struct.unpack_from("!H", self.length_array)[0]

                if self.has_mask is True:
                    self.mask_array = bytearray()
                    self.state = MASK
                else:
                    # if there is no mask and no payload we are done
                    if self.length <= 0:
                        try:
                            self._handlePacket()
                        finally:
                            self.state = HEADER_B1
                            self.data = bytearray()

                    # we have no mask and some payload
                    else:
                        # self.index = 0
                        self.data = bytearray()
                        self.state = PAYLOAD

        elif self.state == LENGTH_LONG:

            self.length_array.append(byte)

            if len(self.length_array) > 8:
                raise Exception("long length exceeded allowable size")

            if len(self.length_array) == 8:
                self.length = struct.unpack_from("!Q", self.length_array)[0]

                if self.has_mask is True:
                    self.mask_array = bytearray()
                    self.state = MASK
                else:
                    # if there is no mask and no payload we are done
                    if self.length <= 0:
                        try:
                            self._handlePacket()
                        finally:
                            self.state = HEADER_B1
                            self.data = bytearray()

                    # we have no mask and some payload
                    else:
                        # self.index = 0
                        self.data = bytearray()
                        self.state = PAYLOAD

        # MASK STATE
        elif self.state == MASK:
            self.mask_array.append(byte)

            if len(self.mask_array) > 4:
                raise Exception("mask exceeded allowable size")

            if len(self.mask_array) == 4:
                # if there is no mask and no payload we are done
                if self.length <= 0:
                    try:
                        self._handlePacket()
                    finally:
                        self.state = HEADER_B1
                        self.data = bytearray()

                # we have no mask and some payload
                else:
                    # self.index = 0
                    self.data = bytearray()
                    self.state = PAYLOAD

        # PAYLOAD STATE
        elif self.state == PAYLOAD:
            if self.has_mask is True:
                self.data.append(byte ^ self.mask_array[self.index % 4])
            else:
                self.data.append(byte)

            # if length exceeds allowable size then we except and remove the connection
            if len(self.data) >= self.maxpayload:
                raise Exception("payload exceeded allowable size")

            # check if we have processed length bytes; if so we are done
            if (self.index + 1) == self.length:
                try:
                    self._handlePacket()
                finally:
                    # self.index = 0
                    self.state = HEADER_B1
                    self.data = bytearray()
            else:
                self.index += 1

    def falsify_variables(self):
        self.socket = None
        self.keep_alive = False
        self.connected = False

    def try_except(self, func: str, arg):
        try:
            return getattr(self.socket, func)(arg)

        except Exception as e:
            LOGGER.debug(e)
            if self.socket:
                self.socket.close()
            self.falsify_variables()

    def recv(self, read: int = 1024):
        if recv := self.try_except("recv", read):
            return recv

    def send(self, data: bytes) -> int:
        return self.try_except("send", data)

    def send_payload(self, fin: bool, message: bytes, opcode=OPCODE_TEXT) -> int:
        b1 = 0
        b2 = 0
        if fin is False:
            b1 |= FIN
        b1 |= opcode

        if isinstance(message, str):
            message = message.encode(UTF8)

        payload = bytearray()
        payload.append(b1)

        message_length = len(message)

        # Normal payload
        if message_length <= NORMAL_PAYLOAD_LENGTH:
            payload.append(b2 | message_length)

        # Extended payload
        elif NORMAL_PAYLOAD_LENGTH < message_length <= EXTENDED_PAYLOAD_LENGTH:
            payload.append(b2 | PAYLOAD_LEN_EXT16)
            payload.extend(struct.pack("!H", message_length))

        # Huge extended payload
        elif message_length < HUGE_EXTENDED_PAYLOAD_LENGTH:
            payload.append(b2 | PAYLOAD_LEN_EXT64)
            payload.extend(struct.pack("!Q", message_length))

        else:
            raise Exception("Message is too big. Consider breaking it into chunks.")

        return self.send(payload + message)

    def send_message(self, message: DATA, fragment: bool = False) -> int:
        """
        Send websocket data frame to the client.

        If data is a unicode object then the frame is sent as Text.
        If the data is a bytearray object then the frame is sent as Binary.
        """
        opcode = OPCODE_BINARY
        if isinstance(message, str):
            opcode = OPCODE_TEXT
        return self.send_payload(fragment, message, opcode=opcode)

    def send_fragment_start(self, data):
        """
        Send the start of a data fragment stream to a websocket client.
        Subsequent data should be sent using sendFragment().
        A fragment stream is completed when sendFragmentEnd() is called.

        If data is a unicode object then the frame is sent as Text.
        If the data is a bytearray object then the frame is sent as Binary.
        """
        self.send_message(data, fragment=True)

    def send_fragment(self, data):
        """
        see send_fragment_start()

        If data is a unicode object then the frame is sent as Text.
        If the data is a bytearray object then the frame is sent as Binary.
        """
        self.send_payload(True, data, opcode=OPCODE_STREAM)

    def send_fragment_end(self, data) -> int:
        """
        see send_fragment_end()

        If data is a unicode object then the frame is sent as Text.
        If the data is a bytearray object then the frame is sent as Binary.
        """
        self._sendMessage(False, OPCODE_STREAM, data)

    def send_close(
        self, status: int = STATUS_NORMAL, reason: DATA = DEFAULT_CLOSE_REASON
    ):
        """
        Send CLOSE

        Args:
            status: Status as defined in https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1
            reason: Text with reason of closing the connection
        """
        if not (STATUS_NORMAL <= status <= STATUS_TLS_HANDSHAKE_ERROR):
            raise Exception(f"CLOSE status must be between 1000 and 1015, got {status}")

        if isinstance(reason, str):
            reason = reason.encode(UTF8)

        payload = struct.pack("!H", status) + reason
        self.send_payload(False, payload, opcode=OPCODE_CLOSE)
        self.connected = False
        self.on_closed()

    def _handshake(self):
        ...

    def handle(self):
        while self.keep_alive:
            if not self.handshaked:
                self._handshake()

            elif self.valid_client:
                data = self.recv(16384)
                if not data:
                    raise Exception("remote socket closed")

                for d in data:
                    self._parseMessage(d)

    def on_connected(self):
        ...

    def on_message(self):
        ...

    def on_ping(self):
        ...

    def on_pong(self):
        ...

    def on_closed(self):
        ...


class PRMP_WebSocketHandler(PRMP_WebsocketProtocol, socketserver.StreamRequestHandler):
    def __init__(self, socket, addr, server: "PRMP_WebSocketServer"):
        PRMP_WebsocketProtocol.__init__(self)

        if server.key and server.cert:
            try:
                socket = ssl.wrap_socket(
                    socket,
                    server_side=True,
                    certfile=server.cert,
                    keyfile=server.key,
                    ssl_version=server.version,
                )
            except:  # Not sure which exception it throws if the key/cert isn't found
                LOGGER.warning(
                    " SSL not available (are the paths {} and {} correct for the key and cert?)".format(
                        server.key, server.cert
                    )
                )

        self.using_ssl = False

        socketserver.StreamRequestHandler.__init__(self, socket, addr, server)

        self.server: PRMP_WebSocketServer

    def setup(self):
        self.socket = self.request
        super().setup()

    def _read_http_headers(self) -> dict:
        headers = {}
        try:
            # first line should be HTTP GET
            http_get = self.rfile.readline().decode().strip()
            assert http_get.upper().startswith("GET")
            # remaining should be headers
            while True:
                header = self.rfile.readline().decode().strip()
                if not header:
                    break
                head, value = header.split(":", 1)
                headers[head.lower().strip()] = value.strip()
        except Exception as e:
            LOGGER.debug(" Header read error", e)

        return headers

    def _handshake(self):
        headers = self._read_http_headers()

        try:
            assert headers["upgrade"].lower() == "websocket"
        except Exception as e:
            self.keep_alive = False

        try:
            key = headers["sec-websocket-key"]
        except KeyError:
            LOGGER.warning(" Client tried to connect but was missing a key")
            self.keep_alive = False

        if not self.keep_alive:
            self.send(FAILED_HANDSHAKE_STR.encode(ASCII))

        else:
            response = self._make_handshake_response(key)
            self.handshaked = bool(self.send(response.encode()))
            self.valid_client = True
            self.server.new_client(self)
            self.connected = True
            self.on_connected()

    def send_close(
        self, status: int = STATUS_NORMAL, reason: DATA = DEFAULT_CLOSE_REASON
    ):
        super().send_close(status, reason)
        self.keep_alive = False

    def finish(self) -> None:
        super().finish()
        self.server._client_left(self)
        self.on_closed()


class PRMP_WebSocketServer(socketserver.ThreadingTCPServer):

    allow_reuse_address = True
    request_queue_size = 10
    Handler = PRMP_WebSocketHandler

    def __init__(
        self,
        server_address: tuple[str, int],
        key: str = "",
        cert: str = "",
        version=ssl.PROTOCOL_TLSv1,
        log_level: int = logging.WARNING,
    ) -> None:
        super().__init__(server_address, self.Handler)

        LOGGER.setLevel(log_level)

        self.key = key
        self.cert = cert
        self.version = version

        self.thread: threading.Thread = None
        self.clients: list[PRMP_WebSocketHandler] = []
        self.clients_map: dict[str, PRMP_WebSocketHandler] = {}

        self._deny_clients = False
        self.started = False

    def serve_forever(self, threaded_serving: bool = True):
        cls_name = self.__class__.__name__
        try:
            self.started = True
            self.on_start()
            if threaded_serving:
                self.thread = threading.Thread(
                    target=super().serve_forever, daemon=True
                )
                LOGGER.debug(f" Starting {cls_name} on thread {self.thread.getName()}.")

                self.thread.start()

            else:
                self.thread = threading.current_thread()
                LOGGER.debug(f" Starting {cls_name} on main thread.")

                super().serve_forever()

        except KeyboardInterrupt:
            LOGGER.debug(" Server terminated.")
            self.close()

        except Exception as e:
            LOGGER.error(" " + str(e), exc_info=True)
            os.sys.exit(1)
            self.close()

    def _deny_new_connections(self, status, reason):
        self._deny_clients = {
            "status": status,
            "reason": reason,
        }

    def allow_new_connections(self):
        self._deny_clients = False

    def broadcast(self, msg: DATA):
        for client in self.clients:
            client.send_message(msg)

    def new_client(self, client: "PRMP_WebSocketHandler"):
        if self._deny_clients:
            client.send_close(**self._deny_clients)
            self.close_client(client)
        else:
            self.clients.append(client)
            self.on_new_client(client)

    def _client_left(self, client: "PRMP_WebSocketHandler"):
        self.on_client_left(client)
        if client in self.clients:
            self.clients.remove(client)

    def close_client(self, client: "PRMP_WebSocketHandler"):
        client.finish()
        client.socket.close()

    def close_clients(self):
        for client in self.clients:
            self.close_client(client)

    def _disconnect_clients_abruptly(self):
        """
        Terminate clients abruptly (no CLOSE handshake) without shutting down the server
        """
        self.close_clients()

    def _disconnect_clients_gracefully(
        self, status=STATUS_NORMAL, reason=DEFAULT_CLOSE_REASON
    ):
        """
        Terminate clients gracefully without shutting down the server
        """
        for client in self.clients:
            client.send_close(status, reason)
        self.close_clients()

    def close(self, status=STATUS_NORMAL, reason=DEFAULT_CLOSE_REASON):
        """
        Send a CLOSE handshake to all connected clients before terminating server
        """
        self.started = False
        self.on_close()
        if self.clients:
            self._disconnect_clients_gracefully(status, reason)
        self.server_close()
        self.shutdown()

    def get_request(self):
        sock, addr = super().get_request()
        self.on_accept(sock, addr)
        return sock, addr

    def on_accept(self, sock, addr):
        LOGGER.info(f" Socket accepted: {addr}")

    def on_start(self):
        LOGGER.info(f" Server started at {TIME2STRING()}")

    def on_close(self):
        LOGGER.info(f" Server closed at {TIME2STRING()}")

    def on_new_client(self, client: "PRMP_WebSocketHandler"):
        LOGGER.info(f" Client connected: {client.client_address}")

    def on_client_left(
        self,
        client: "PRMP_WebSocketHandler",
    ):
        LOGGER.info(f" Client disconnected: {client.client_address}")


class SimpleCookieJar:
    def __init__(self):
        self.jar = dict()

    def add(self, set_cookie):
        if set_cookie:
            simpleCookie = http.cookies.SimpleCookie(set_cookie)

            for k, v in simpleCookie.items():
                domain = v.get("domain")
                if domain:
                    if not domain.startswith("."):
                        domain = "." + domain
                    cookie = (
                        self.jar.get(domain)
                        if self.jar.get(domain)
                        else http.cookies.SimpleCookie()
                    )
                    cookie.update(simpleCookie)
                    self.jar[domain.lower()] = cookie

    def set(self, set_cookie):
        if set_cookie:
            simpleCookie = http.cookies.SimpleCookie(set_cookie)

            for k, v in simpleCookie.items():
                domain = v.get("domain")
                if domain:
                    if not domain.startswith("."):
                        domain = "." + domain
                    self.jar[domain.lower()] = simpleCookie

    def get(self, host):
        if not host:
            return ""

        cookies = []
        for domain, simpleCookie in self.jar.items():
            host = host.lower()
            if host.endswith(domain) or host == domain[1:]:
                cookies.append(self.jar.get(domain))

        return "; ".join(
            filter(
                None,
                sorted(
                    [
                        "%s=%s" % (k, v.value)
                        for cookie in filter(None, cookies)
                        for k, v in cookie.items()
                    ]
                ),
            )
        )


class HandshakeResponse:
    CookieJar = SimpleCookieJar()

    def __init__(self, status, headers, subprotocol):
        self.status = status
        self.headers = headers
        self.subprotocol = subprotocol
        HandshakeResponse.CookieJar.add(headers.get("set-cookie"))


class PRMP_WebSocketClient(PRMP_WebsocketProtocol):
    def __init__(self, log_level: int = logging.WARNING) -> None:
        super().__init__()
        LOGGER.setLevel(log_level)

        self.handshake_response = None
        self.rfile = None
        self.started = False

    def __iter__(self):
        """
        Allow iteration over websocket, implying sequential `recv` executions.
        """
        while True:
            yield self.recv()

    def __exit__(self):
        self.send_close(reason="Closing Client")

    def __next__(self):
        return self.recv()

    def next(self):
        return self.__next__()

    def parse_url(self, url):
        """
        parse url and the result is tuple of
        (address, port, resource path and the flag of secure mode)

        Parameters
        ----------
        url: str
            url string.
        """
        if ":" not in url:
            raise ValueError("url is invalid")

        scheme, url = url.split(":", 1)

        parsed = urlparse(url, scheme="http")
        if parsed.hostname:
            address = parsed.hostname
        else:
            raise ValueError("address is invalid")
        port = 0
        if parsed.port:
            port = parsed.port

        is_secure = False
        if scheme == "ws":
            if not port:
                port = 80
        elif scheme == "wss":
            is_secure = True
            if not port:
                port = 443
        else:
            raise ValueError("scheme %s is invalid" % scheme)

        if parsed.path:
            resource = parsed.path
        else:
            resource = "/"

        if parsed.query:
            resource += "?" + parsed.query

        return address, port, resource, is_secure

    def _pack_address(self, address):
        # IPv6 address
        if ":" in address:
            return "[" + address + "]"

        return address

    def read_headers(self):
        status = None
        status_message = None
        headers = {}

        while True:
            line = self.rfile.readline().decode().strip()
            if not line:
                break

            if not status:

                status_info = line.split(" ", 2)
                status = int(status_info[1])
                if len(status_info) > 2:
                    status_message = status_info[2]
            else:
                kv = line.split(":", 1)
                if len(kv) == 2:
                    key, value = kv
                    if key.lower() == "set-cookie" and headers.get("set-cookie"):
                        headers["set-cookie"] = (
                            headers.get("set-cookie") + "; " + value.strip()
                        )
                    else:
                        headers[key.lower()] = value.strip()
                else:
                    raise Exception("Invalid header")

        return status, headers, status_message

    def _get_handshake_headers(
        self, resource: str, url: str, address: str, port: int, options: dict
    ):
        headers = ["GET %s HTTP/1.1" % resource, "Upgrade: websocket"]
        if port == 80 or port == 443:
            address_port = self._pack_address(address)
        else:
            address_port = "%s:%d" % (self._pack_address(address), port)
        if options.get("host"):
            headers.append("Host: %s" % options["host"])
        else:
            headers.append("Host: %s" % address_port)

        # scheme indicates whether http or https is used in Origin
        # The same approach is used in parse_url of _url.py to set default port
        scheme, url = url.split(":", 1)
        if not options.get("suppress_origin"):
            if "origin" in options and options["origin"] is not None:
                headers.append("Origin: %s" % options["origin"])
            elif scheme == "wss":
                headers.append("Origin: https://%s" % address_port)
            else:
                headers.append("Origin: http://%s" % address_port)

        key = self._create_sec_websocket_key()

        # Append Sec-WebSocket-Key & Sec-WebSocket-Version if not manually specified
        if not options.get("header") or "Sec-WebSocket-Key" not in options["header"]:
            key = self._create_sec_websocket_key()
            headers.append("Sec-WebSocket-Key: %s" % key)
        else:
            key = options["header"]["Sec-WebSocket-Key"]

        if (
            not options.get("header")
            or "Sec-WebSocket-Version" not in options["header"]
        ):
            headers.append("Sec-WebSocket-Version: %s" % VERSION)

        if not options.get("connection"):
            headers.append("Connection: Upgrade")
        else:
            headers.append(options["connection"])

        subprotocols = options.get("subprotocols")
        if subprotocols:
            headers.append("Sec-WebSocket-Protocol: %s" % ",".join(subprotocols))

        header = options.get("header")
        if header:
            if isinstance(header, dict):
                header = [": ".join([k, v]) for k, v in header.items() if v is not None]
            headers.extend(header)

        server_cookie = HandshakeResponse.CookieJar.get(address)
        client_cookie = options.get("cookie", None)

        cookie = "; ".join(filter(None, [server_cookie, client_cookie]))

        if cookie:
            headers.append("Cookie: %s" % cookie)

        headers.append("")
        headers.append("")

        return headers, key

    def _get_resp_headers(self, success_statuses=SUCCESS_STATUSES):
        status, resp_headers, status_message = self.read_headers()
        if status not in success_statuses:
            raise Exception(
                "Handshake status %d %s", status, status_message, resp_headers
            )
        return status, resp_headers

    _HEADERS_TO_CHECK = {
        "upgrade": "websocket",
        "connection": "upgrade",
    }

    def _validate(self, headers, key, subprotocols):
        subproto = None
        for k, v in self._HEADERS_TO_CHECK.items():
            r = headers.get(k, None)
            if not r:
                return False, None
            r = [x.strip().lower() for x in r.split(",")]
            if v not in r:
                return False, None

        if subprotocols:
            subproto = headers.get("sec-websocket-protocol", None)
            if not subproto or subproto.lower() not in [
                s.lower() for s in subprotocols
            ]:
                LOGGER.debug(" Invalid subprotocol: " + str(subprotocols))
                return False, None
            subproto = subproto.lower()

        result = headers.get("sec-websocket-accept", None)
        if not result:
            return False, None
        result = result.lower()

        if isinstance(result, str):
            result = result.encode("utf-8")

        value = (key + GUID).encode("utf-8")
        hashed = base64encode(hashlib.sha1(value).digest()).strip().lower()
        success = hmac.compare_digest(hashed, result)

        if success:
            return True, subproto
        else:
            return False, None

    def handshake(self, url, address, port, resource, options: dict):
        headers, key = self._get_handshake_headers(
            resource, url, address, port, options
        )

        header_str = "\r\n".join(headers)
        self.send(header_str.encode())

        status, resp = self._get_resp_headers()
        if status in SUPPORTED_REDIRECT_STATUSES:
            return HandshakeResponse(status, resp, None)

        success, subproto = self._validate(resp, key, options.get("subprotocols"))
        if not success:
            raise Exception("Invalid WebSocket Header")

        return HandshakeResponse(status, resp, subproto)

    def _create_sec_websocket_key(self):
        randomness = os.urandom(16)
        return base64encode(randomness).decode("utf-8").strip()

    def _connect(self, address: str = "", port: int = 80, timeout=0) -> socket.socket:
        addrinfo_list = socket.getaddrinfo(
            address, port, 0, socket.SOCK_STREAM, socket.SOL_TCP
        )

        err = None
        sock: socket.socket = None

        for addrinfo in addrinfo_list:
            family, socktype, proto = addrinfo[:3]
            sock = socket.socket(family, socktype, proto)
            if timeout:
                sock.settimeout(timeout)
            for opts in DEFAULT_SOCKET_OPTION:
                sock.setsockopt(*opts)

            address = addrinfo[4]
            err = None
            while not err:
                try:
                    sock.connect(address)
                except socket.error as error:
                    sock.close()
                    error.remote_ip = str(address[0])
                    try:
                        eConnRefused = (
                            errno.ECONNREFUSED,
                            errno.WSAECONNREFUSED,
                            errno.ENETUNREACH,
                        )
                    except AttributeError:
                        eConnRefused = (errno.ECONNREFUSED, errno.ENETUNREACH)
                    if error.errno in eConnRefused:
                        err = error
                        continue
                    else:
                        raise error
                else:
                    break
            else:
                continue
            break
        else:
            if err:
                raise err

        return sock

    def connect(
        self,
        url: str = "",
        address: str = "",
        port: int = 80,
        timeout=0,
        redirect_limit: int = 3,
        secure=False,
        resource="",
        options: dict = {},
    ):

        if url:
            address, port, resource, secure = self.parse_url(url)
        else:
            scheme = "ws"
            if secure:
                scheme += "s"
            url = f"{scheme}://{address}:{port}"

        assert address and port, "Provide valid (address and port) or url."

        self.socket = self._connect(address=address, port=port, timeout=timeout)
        self.rfile = self.socket.makefile("rb", -1)

        try:
            self.handshake_response = self.handshake(
                url, address, port, resource, options
            )
            if self.handshake_response.status in SUPPORTED_REDIRECT_STATUSES:
                for _ in range(redirect_limit):
                    url = self.handshake_response.headers["location"]
                    self.socket.close()
                    self.socket = self._connect(address=address, port=port)
                    self.handshake_response = self.handshake(
                        url, address, port, resource, options
                    )

            self.connected = True
            self.valid_client = True
            self.handshaked = True
            self.on_connected()

        except Exception as e:
            if self.socket:
                self.socket.close()
                self.socket = None
            raise

    def abort(self):
        """
        Low-level asynchronous abort, wakes up other threads that are waiting in recv_*
        """
        if self.connected:
            self.socket.shutdown(socket.SHUT_RDWR)

    def shutdown(self):
        """
        close socket, immediately.
        """
        if self.socket:
            self.keep_alive = False
            self.socket.close()
            self.socket = None
            self.connected = False

    def start(self, threaded=True):
        if self.started:
            return

        if threaded:
            threading.Thread(target=self.handle).start()
        else:
            self.handle()

        self.started = True

    def close(self, reason: str = ""):
        self.send_close(reason=reason)
        self.shutdown()

    def on_closed(self):
        LOGGER.info(" Disconnected from Server")

    def on_connected(self):
        LOGGER.info(" Connected to Server")
