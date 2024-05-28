import copy
import socket
import ssl
import struct
import threading
import traceback

from networking import config, tlv_definitions
from auth import AuthenticationService
from log import Logger
from networking.server import room
from networking.server.player import Player
from networking.server.room import RoomManager
from networking.tlv_parser import TLVParser


class Server:
    def __init__(self, host=config.SERVER_IP, port=config.SERVER_PORT, certfile="server.crt", keyfile="server.key"):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_listening = False
        self.clients = {}

        self.auth_service = AuthenticationService()
        self.logger = Logger("logs.txt")
        self.room_manager = RoomManager()
        self.definitions = tlv_definitions.TLVDefinitions(tag_mappings=tlv_definitions.mappings)
        self.tlv_parser = TLVParser(self.definitions)
        self.lock = threading.Lock()

        # Mapping packet IDs to their handler functions
        self.handlers = {
            config.REQUEST_LOGIN: self.handle_login,
            config.REQUEST_REGISTER: self.handle_register,
            config.REQUEST_JOIN_ROOM: self.handle_join_room,
            config.REQUEST_LEAVE_ROOM: self.handle_leave_room,
            config.REQUEST_LIST_ROOMS: self.handle_list_rooms,
            config.REQUEST_CREATE_ROOM: self.handle_create_room,
            config.REQUEST_START_GAME: self.handle_start_game,
            config.REQUEST_MOVE: self.handle_move,
        }

    def start(self):
        self.logger.log_event("Starting server...")
        self.bind_and_listen()
        self.is_listening = True
        threading.Thread(target=self.accept_connections).start()

    def bind_and_listen(self):
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(config.MAX_CLIENTS)
            self.logger.log_event(f"Server started on {self.host}:{self.port}")
        except socket.error as e:
            self.logger.log_error(f"Error binding/listening: {e}")

    def accept_connections(self):
        while self.is_listening:
            try:
                sock, addr = self.sock.accept()

                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
                context.check_hostname = False

                wrapped_socket = context.wrap_socket(sock, server_side=True)

                payload = [
                    (config.TAG_SUCCESS, True),
                ]
                data = self.tlv_parser.encode_tlv_packet(config.ACCEPTED, payload)
                wrapped_socket.sendall(data)
                threading.Thread(target=self.handle_client, args=(wrapped_socket,)).start()
                self.logger.log_event(f"Connection from {addr}")
            except socket.error as e:
                self.logger.log_error(f"Error accepting connection: {e}")

    def handle_client(self, client_socket):
        try:
            while True:
                raw_packet_length = self.recv_all(client_socket, 2)
                if not raw_packet_length:
                    break

                packet_length = struct.unpack("!H", raw_packet_length)[0]
                data = self.recv_all(client_socket, packet_length - 2)
                if not data:
                    break

                response = self.process_request(data, client_socket)

                # Send the response back to the client
                client_socket.sendall(response)
        except Exception as e:
            self.logger.log_error(f"Error handling client: {e}, {''.join(traceback.format_tb(e.__traceback__))}")
        finally:
            client_socket.close()

    def recv_all(self, client_socket, num_bytes):
        data = bytearray()
        while len(data) < num_bytes:
            packet = client_socket.recv(num_bytes - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def process_request(self, data, client_socket):
        offset = 0

        # Extract packet ID
        packet_id = int.from_bytes(data[offset:offset+self.tlv_parser.tag_definitions.tag_size], byteorder='big')
        offset += self.tlv_parser.tag_definitions.tag_size

        if packet_id not in (config.REQUEST_REGISTER, config.REQUEST_LOGIN):
            # Extract JWT token length
            jwt_token, offset = self.tlv_parser.read_tlv(data, offset)

            if not self.auth_service.verify_jwt(jwt_token):
                return self.tlv_parser.encode_tlv_packet(config.RESPONSE_AUTH_ERROR,
                                                         [(config.TAG_ERROR_MESSAGE, "Invalid or expired token")])

        # Parse TLV fields
        fields = self.tlv_parser.parse_tlv(data, offset)

        # Route request based on packet ID
        handler = self.handlers.get(packet_id)
        if handler:
            if packet_id == config.REQUEST_LOGIN:
                return handler(client_socket=client_socket, *fields)
            return handler(*fields)
        else:
            return self.tlv_parser.encode_tlv_packet(config.RESPONSE_ERROR, [(config.TAG_ERROR_MESSAGE, "Unknown "
                                                                                                        "packet "
                                                                                                        "ID")])

    def handle_login(self, username, password, client_socket):
        with self.lock:
            success, jwt_token = self.auth_service.authenticate_user(username, password)
            payload = [
                (config.TAG_SUCCESS, success),
                (config.TAG_JWT_TOKEN, jwt_token),
            ]

            if success:
                self.clients[username] = Player(username, client_socket)
        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_LOGIN_RESULT, payload)

    def handle_register(self, username, password):
        with self.lock:
            success = self.auth_service.register_user(username, password)
            payload = [
                (config.TAG_SUCCESS, success),
            ]
        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_REGISTER_RESULT, payload)

    def handle_join_room(self, username, room_id):
        with self.lock:
            success = self.room_manager.join_room(room_id, self.clients[username])
            payload = [
                (config.TAG_SUCCESS, success),
            ]

            if success:
                room = self.room_manager.get_room(room_id)
                room_info = room.get_room_info()
                payload.append(
                    (config.TAG_ROOM, room_info)
                )
                room.broadcast(self.tlv_parser.encode_tlv_packet(config.SIGNAL_PLAYER_JOIN, payload))
        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_JOIN_ROOM_RESULT, payload)

    def handle_leave_room(self, username):
        with self.lock:
            room_id = username.current_room
            success = self.room_manager.leave_room(username)
            payload = [
                (config.TAG_SUCCESS, success),
            ]
            if success:
                room = self.room_manager.get_room(room_id)
                room.broadcast(self.tlv_parser.encode_tlv_packet(config.SIGNAL_PLAYER_JOIN, room.get_info))
        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_LEAVE_ROOM_RESULT, payload)

    def handle_list_rooms(self, username):
        with self.lock:
            rooms = self.room_manager.list_rooms()
            encoded_rooms = []
            for room in rooms:
                room_payload = [
                    (config.TAG_ROOM, (
                        (config.TAG_ROOM_ID, room["id"]),
                        (config.TAG_CURRENT_PLAYERS, room["current_players"]),
                        (config.TAG_MAX_PLAYERS, room["max_players"]),
                    ))
                ]
                encoded_rooms.append(room_payload)

            payload = [
                (config.TAG_ROOMS, encoded_rooms),
            ]

        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_LIST_ROOMS_RESULT, payload)

    def handle_start_game(self, username, room_id):
        success = False
        with self.lock:
            r = self.room_manager.get_room(room_id)
            if r and r.owner == username:
                game_info = r.start_game()
                if game_info is None:
                    return self.tlv_parser.encode_tlv_packet(config.RESPONSE_START_GAME_RESULT, [(config.TAG_SUCCESS, False)])

                r.broadcast(self.tlv_parser.encode_tlv_packet(config.SIGNAL_START_GAME, [
                    (config.TAG_GAME_INFO, game_info),
                ]
                ))

                self.room_manager.set_room_state(room_id, room.STATE_PLAYING)
                success = True

                payload = [
                    (config.TAG_SUCCESS, success),
                ]

        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_START_GAME_RESULT, payload)

    def handle_create_room(self, username, room_id):
        with self.lock:
            success = self.room_manager.create_room(room_id, self.clients[username], 4)

        payload = [
            (config.TAG_SUCCESS, success),
        ]

        if success:
            room = self.room_manager.get_room(room_id)
            payload.append(
                (config.TAG_ROOM, room.get_room_info())
            )

        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_CREATE_ROOM_RESULT, payload)

    def handle_move(self, username, room_id, direction):
        success = False
        with self.lock:
            r = self.room_manager.get_room(room_id)
            if r and r.state == room.STATE_PLAYING:
                if r.players.get(username):
                    success = r.move_player(username, direction)
                    if success:
                        r.broadcast(
                            self.tlv_parser.encode_tlv_packet(config.SIGNAL_UPDATE_POSITIONS,
                                                              [(config.TAG_POSITIONS, r.get_positions_info()),]))
                        px, py = r.players[username].x, r.players[username].y
                        if r.maze[px][py] == 2:
                            r.broadcast(
                                self.tlv_parser.encode_tlv_packet(config.SIGNAL_SCORE_UPDATE,
                                                                  [(config.TAG_USERNAME, username)])
                            )

        self.logger.log_event(f"{username} requested a {direction} move, success:{success}")
        payload = [
            (config.TAG_SUCCESS, success),
        ]

        return self.tlv_parser.encode_tlv_packet(config.RESPONSE_MOVE_RESULT, payload)

    def stop(self):
        self.is_listening = False
        self.sock.close()
        self.logger.log_event("Server stopped")


if __name__ == "__main__":
    server = Server()
    server.start()
