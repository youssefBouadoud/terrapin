import queue
import socket
import ssl
import threading
import struct
from networking.tlv_parser import TLVParser
from networking import config, tlv_definitions

class Client:
    def __init__(self):
        self.sock = None
        self.tlv_parser = TLVParser(tlv_definitions.tag_definitions)
        self.lock = threading.Lock()
        self.event_queue = queue.Queue()

    def connect(self, server_address, port, certfile):
        try:
            self.sock = socket.socket()
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.load_verify_locations(certfile)

            self.sock = context.wrap_socket(self.sock, server_side=False)
            self.sock.connect((server_address, port))
            threading.Thread(target=self.listen_to_server).start()
            return True
        except socket.error as e:
            print(e)
            return False

    def listen_to_server(self):
        while True:
            raw_packet_length = self.recv_all(2)
            if not raw_packet_length:
                break

            packet_length = struct.unpack("!H", raw_packet_length)[0]
            data = self.recv_all(packet_length - 2)
            print("data", data)
            if not data:
                break
            self.event_queue.put(data)

    def send_packet(self, packet):
        with self.lock:
            self.sock.sendall(packet)

    def recv_packet(self):
        if raw_packet_length := self.recv_all(2) is None:
            return None
        packet_length = struct.unpack("!H", raw_packet_length)[0]
        data = self.recv_all(packet_length - 2)
        return data

    def recv_all(self, num_bytes):
        data = bytearray()
        while len(data) < num_bytes:
            packet = self.sock.recv(num_bytes - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def send_login_request(self, username, password):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_LOGIN, [
            (config.TAG_USERNAME, username),
            (config.TAG_PASSWORD, password)
        ])
        self.send_packet(packet)

    def send_register_request(self, username, password):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_REGISTER, [
            (config.TAG_USERNAME, username),
            (config.TAG_PASSWORD, password)
        ])
        self.send_packet(packet)

    def send_create_room(self, username, jwt_token, room_code):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_CREATE_ROOM,[
            (config.TAG_JWT_TOKEN, jwt_token),
            (config.TAG_USERNAME, username),
            (config.TAG_ROOM_ID, room_code),
        ])
        self.send_packet(packet)

    def send_join_room(self, username, jwt_token, room_code):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_JOIN_ROOM, [
            (config.TAG_JWT_TOKEN, jwt_token),
            (config.TAG_USERNAME, username),
            (config.TAG_ROOM_ID, room_code),
        ])
        self.send_packet(packet)

    def send_start_game_request(self, username, jwt_token, room_code):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_START_GAME, [
            (config.TAG_JWT_TOKEN, jwt_token),
            (config.TAG_USERNAME, username),
            (config.TAG_ROOM_ID, room_code),
        ])
        self.send_packet(packet)

    def send_move_request(self, username, jwt_token, direction, room_code):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_MOVE, [
            (config.TAG_JWT_TOKEN, jwt_token),
            (config.TAG_USERNAME, username),
            (config.TAG_ROOM_ID, room_code),
            (config.TAG_DIRECTION, direction)
        ])
        self.send_packet(packet)

    def send_leave_room_request(self, username, jwt_token):
        packet = self.tlv_parser.encode_tlv_packet(config.REQUEST_LEAVE_ROOM, [
            (config.TAG_JWT_TOKEN, jwt_token),
            (config.TAG_USERNAME, username)
        ])
        self.send_packet(packet)

