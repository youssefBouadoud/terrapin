import struct
import copy
import numpy as np

from networking.server.round import generate_map
from networking.tlv_parser import TLVParser
from networking import config


class TLVDefinitions:
    def __init__(self, tag_size=2, length_size=2, tag_mappings=None):
        if tag_mappings is None:
            tag_mappings = dict()
        self.tag_size = tag_size
        self.length_size = length_size
        self.tag_mappings = copy.deepcopy(tag_mappings)

    def get(self, key, default=None):
        return self.tag_mappings.get(key, default)


def unpack_pid(data):
    return int.from_bytes(data, byteorder='big')


def pack_pid(value):
    return struct.pack("!I", value)


def unpack_username(data):
    return data.decode()


def pack_username(value):
    return value.encode()


def unpack_password(data):
    return data.decode()


def pack_password(value):
    return value.encode()


def unpack_jwt_token(data):
    return data.decode()


def pack_jwt_token(value):
    return value.encode()


def unpack_room_id(data):
    return data.decode()


def pack_room_id(value):
    return value.encode()


def unpack_current_players(data):
    return struct.unpack("!I", data)[0]


def pack_current_players(value):
    return struct.pack("!I", value)


def unpack_max_players(data):
    return struct.unpack("!I", data)[0]


def pack_max_players(value):
    return struct.pack("!I", value)


def unpack_success(data):
    return bool(struct.unpack("!B", data)[0])


def pack_success(value):
    return struct.pack("!B", int(value))


def unpack_room(data):
    parser = TLVParser(tag_definitions)
    offset = 0
    room = {}
    while offset < len(data):
        tag, value, offset = parser.read_tlv(data, offset, get_tag=True)
        if tag == config.TAG_ROOM_ID:
            room["id"] = value
        elif tag == config.TAG_CURRENT_PLAYERS:
            room["current_players"] = value
        elif tag == config.TAG_MAX_PLAYERS:
            room["max_players"] = value
        elif tag == config.TAG_PLAYERS:
            room["players"] = value
        elif tag == config.TAG_STATE:
            room["state"] = value
        elif tag == config.TAG_ROUND:
            room["round"] = value
        elif tag == config.TAG_NUM_ROUNDS:
            room["num_rounds"] = value
        elif tag == config.TAG_MIN_PLAYERS:
            room["min_players"] = value
        elif tag == config.TAG_OWNER:
            room["owner"] = value
        else:
            pass
    return room


def pack_room(value):
    parser = TLVParser(tag_definitions)
    packed_room = bytearray()

    encoded_room_id = parser.encode_tlv(config.TAG_ROOM_ID, value["id"])
    encoded_current_players = parser.encode_tlv(config.TAG_CURRENT_PLAYERS, value["current_players"])
    encoded_max_players = parser.encode_tlv(config.TAG_MAX_PLAYERS, value["max_players"])
    encoded_state = parser.encode_tlv(config.TAG_STATE, value["state"])
    encoded_players = parser.encode_tlv(config.TAG_PLAYERS, value["players"])
    encoded_round = parser.encode_tlv(config.TAG_ROUND, value["round"])
    encoded_num_rounds = parser.encode_tlv(config.TAG_NUM_ROUNDS, value["num_rounds"])
    encoded_min_players = parser.encode_tlv(config.TAG_MIN_PLAYERS, value["min_players"])
    encoded_owner = parser.encode_tlv(config.TAG_OWNER, value["owner"])

    packed_room.extend(encoded_room_id)
    packed_room.extend(encoded_current_players)
    packed_room.extend(encoded_max_players)
    packed_room.extend(encoded_state)
    packed_room.extend(encoded_players)
    packed_room.extend(encoded_round)
    packed_room.extend(encoded_num_rounds)
    packed_room.extend(encoded_min_players)
    packed_room.extend(encoded_owner)

    return packed_room


def unpack_rooms(data):
    parser = TLVParser(tag_definitions)
    rooms = []
    offset = 0
    while offset < len(data):
        room, offset = parser.read_tlv(data, offset)
        rooms.append(room)
    return rooms


def pack_rooms(value):
    parser = TLVParser(tag_definitions)
    encoded_rooms = bytearray()
    for room in value:
        room_data = parser.encode_tlv(config.TAG_ROOM, room)
        encoded_rooms.extend(room_data)
    return bytes(encoded_rooms)


def unpack_state(data):
    return struct.unpack("!I", data)[0]


def pack_state(value):
    return struct.pack("!I", value)


def unpack_players(data):
    parser = TLVParser(tag_definitions)
    players = []
    offset = 0
    while offset < len(data):
        username, offset = parser.read_tlv(data, offset)
        players.append(username)
    return players


def pack_players(value):
    parser = TLVParser(tag_definitions)
    encoded_players = bytearray()
    for player in value:
        player_data = parser.encode_tlv(config.TAG_USERNAME, player)
        encoded_players.extend(player_data)
    return bytes(encoded_players)


def unpack_round(data):
    return struct.unpack("!I", data)[0]


def pack_round(value):
    return struct.pack("!I", value)


def unpack_num_rounds(data):
    return struct.unpack("!I", data)[0]


def pack_num_rounds(value):
    return struct.pack("!I", value)


def unpack_map(data):
    parser = TLVParser(tag_definitions)
    maze = []
    offset = 0
    while offset < len(data):
        row, offset = parser.read_tlv(data, offset)
        maze.append(row)
    return maze


def pack_map(value):
    parser = TLVParser(tag_definitions)
    encoded_map = bytearray()
    for row in value:
        row_data = parser.encode_tlv(config.TAG_ROW, row)
        encoded_map.extend(row_data)
    return bytes(encoded_map)


def unpack_row(data):
    ternary_number = int.from_bytes(data, byteorder='big')
    ternary_string = np.base_repr(ternary_number, base=3)

    row = [int(ch) for ch in ternary_string]
    return row


def pack_row(value):
    ternary_string = ''.join([str(x) for x in value])
    ternary_number = int(ternary_string, 3)

    num_bytes = (ternary_number.bit_length() + 7) // 8

    packed_row = ternary_number.to_bytes(num_bytes, byteorder='big')
    return packed_row


def unpack_colours(data):
    parser = TLVParser(tag_definitions)
    colours = []
    offset = 0
    while offset < len(data):
        colour, offset = parser.read_tlv(data, offset)
        colours.append(colour)
    return colours


def pack_colours(value):
    parser = TLVParser(tag_definitions)
    encoded_colours = bytearray()
    for colour in value:
        colour_data = parser.encode_tlv(config.TAG_COLOUR, colour)
        encoded_colours.extend(colour_data)
    return bytes(encoded_colours)


def unpack_colour(data):
    data = struct.unpack("!I", data)[0]
    r = (data >> 16) & 0xFF
    g = (data >> 8) & 0xFF
    b = data & 0xFF
    return (r, g, b)


def pack_colour(value):
    r, g, b = value
    packed_colour = (r << 16) | (g << 8) | b
    return struct.pack("!I", packed_colour)


def unpack_positions(data):
    parser = TLVParser(tag_definitions)
    positions = []
    offset = 0
    while offset < len(data):
        position, offset = parser.read_tlv(data, offset)
        positions.append(position)
    return positions


def pack_positions(value):
    parser = TLVParser(tag_definitions)
    encoded_positions = bytearray()
    for colour in value:
        position_data = parser.encode_tlv(config.TAG_POSITION, colour)
        encoded_positions.extend(position_data)
    return bytes(encoded_positions)


def unpack_position(data):
    x, y = struct.unpack("!HH", data)
    return (x, y)


def pack_position(value):
    x, y = value
    packed_position = struct.pack("!HH", x, y)
    return packed_position


def unpack_game_info(data):
    parser = TLVParser(tag_definitions)
    offset = 0
    game_info = {}
    while offset < len(data):
        tag, value, offset = parser.read_tlv(data, offset, get_tag=True)
        if tag == config.TAG_MAP:
            game_info["map"] = value
        elif tag == config.TAG_PLAYER_COLOURS:
            game_info["player_colours"] = value
        elif tag == config.TAG_MAP_COLOURS:
            game_info["map_colours"] = value
        elif tag == config.TAG_POSITIONS:
            game_info["player_positions"] = value
        else:
            pass
    return game_info


def pack_game_info(value):
    parser = TLVParser(tag_definitions)
    packed_info = bytearray()

    encoded_map = parser.encode_tlv(config.TAG_MAP, value["map"])
    encoded_player_colours = parser.encode_tlv(config.TAG_PLAYER_COLOURS, value["player_colours"])
    encoded_map_colours = parser.encode_tlv(config.TAG_MAP_COLOURS, value["map_colours"])
    encoded_player_positions = parser.encode_tlv(config.TAG_POSITIONS, value["player_positions"])

    packed_info.extend(encoded_map)
    packed_info.extend(encoded_player_colours)
    packed_info.extend(encoded_map_colours)
    packed_info.extend(encoded_player_positions)

    return packed_info


def unpack_min_players(data):
    return struct.unpack("!I", data)[0]


def pack_min_players(value):
    return struct.pack("!I", value)


def unpack_owner(data):
    return data.decode()


def pack_owner(value):
    return value.encode()


def unpack_direction(data):
    return data.decode()


def pack_direction(value):
    return value.encode()


def pack_colour(value):
    r, g, b = value
    packed_colour = (r << 16) | (g << 8) | b
    return struct.pack("!I", packed_colour)


def unpack_error_message(data):
    return data.decode()


def pack_error_message(value):
    return value.encode()


mappings = {
    config.ACCEPTED: {"unpack_func": unpack_pid, "pack_func": pack_pid},
    config.TAG_USERNAME: {"unpack_func": unpack_username, "pack_func": pack_username},
    config.TAG_PASSWORD: {"unpack_func": unpack_password, "pack_func": pack_password},
    config.TAG_JWT_TOKEN: {"unpack_func": unpack_jwt_token, "pack_func": pack_jwt_token},
    config.TAG_ROOM_ID: {"unpack_func": unpack_room_id, "pack_func": pack_room_id},
    config.TAG_CURRENT_PLAYERS: {"unpack_func": unpack_current_players, "pack_func": pack_current_players},
    config.TAG_MAX_PLAYERS: {"unpack_func": unpack_max_players, "pack_func": pack_max_players},
    config.TAG_MIN_PLAYERS: {"unpack_func": unpack_min_players, "pack_func": pack_min_players},
    config.TAG_OWNER: {"unpack_func": unpack_owner, "pack_func": pack_owner},
    config.TAG_STATE: {"unpack_func": unpack_state, "pack_func": pack_state},
    config.TAG_SUCCESS: {"unpack_func": unpack_success, "pack_func": pack_success},
    config.TAG_ROOM: {"unpack_func": unpack_room, "pack_func": pack_room},
    config.TAG_ROOMS: {"unpack_func": unpack_rooms, "pack_func": pack_rooms},
    config.TAG_ROUND: {"unpack_func": unpack_round, "pack_func": pack_round},
    config.TAG_NUM_ROUNDS: {"unpack_func": unpack_num_rounds, "pack_func": pack_num_rounds},
    config.TAG_PLAYERS: {"unpack_func": unpack_players, "pack_func": pack_players},
    config.TAG_MAP: {"unpack_func": unpack_map, "pack_func": pack_map},
    config.TAG_ROW: {"unpack_func": unpack_row, "pack_func": pack_row},
    config.TAG_COLOURS: {"unpack_func": unpack_colours, "pack_func": pack_colours},
    config.TAG_COLOUR: {"unpack_func": unpack_colour, "pack_func": pack_colour},
    config.TAG_POSITIONS: {"unpack_func": unpack_positions, "pack_func": pack_positions},
    config.TAG_POSITION: {"unpack_func": unpack_position, "pack_func": pack_position},
    config.TAG_GAME_INFO: {"unpack_func": unpack_game_info, "pack_func": pack_game_info},
    config.TAG_PLAYER_COLOURS: {"unpack_func": unpack_colours, "pack_func": pack_colours},
    config.TAG_MAP_COLOURS: {"unpack_func": unpack_colours, "pack_func": pack_colours},
    config.TAG_DIRECTION: {"unpack_func": unpack_direction, "pack_func": pack_direction},

    config.TAG_ERROR_MESSAGE: {"unpack_func": unpack_error_message, "pack_func": pack_error_message},
}

# Usage example (assuming read_tlv function is defined elsewhere)
tag_definitions = TLVDefinitions(tag_mappings=mappings)

# Initialize the parser
parser = TLVParser(tag_definitions)

'''
# Sample rooms data
rooms = [
    {
        "id": "room1",
        "current_players": 2,
        "max_players": 4,
        "state": 0x5001,
        "players": ["lupo", "lupastro", "lupastracchio"],
        "round": 6,
        "num_rounds": 10,
    },
    {
        "id": "room2",
        "current_players": 1,
        "max_players": 6,
        "state": 0x5001,
        "players": ["lupo", "lupastro", "lupastracchio"],
        "round": 6,
        "num_rounds": 10,
    }
]

# Packing rooms
packed_rooms = pack_rooms(rooms)
print(packed_rooms.hex().upper())

# Unpacking rooms
unpacked_rooms = unpack_rooms(packed_rooms)

# Printing unpacked rooms
for room in unpacked_rooms:
    print(room)



# Construct example TLV data
data = bytearray()
data.extend(struct.pack("!H", config.TAG_USERNAME))  # Tag for Username
data.extend(struct.pack("!H", len("alice")))
data.extend("alice".encode())

data.extend(struct.pack("!H", config.TAG_PASSWORD))  # Tag for Password
data.extend(struct.pack("!H", len("password123")))
data.extend("password123".encode())

data.extend(struct.pack("!H", config.TAG_JWT_TOKEN))  # Tag for JWT Token
data.extend(struct.pack("!H", len("jwt_token_example")))
data.extend("jwt_token_example".encode())

data.extend(struct.pack("!H", config.TAG_ROOM_ID))  # Tag for Room ID
data.extend(struct.pack("!H", len("room_01")))
data.extend("room_01".encode())

data.extend(struct.pack("!H", config.TAG_CURRENT_PLAYERS))  # Tag for Current Players
data.extend(struct.pack("!H", 4))
data.extend(struct.pack("!I", 5))

data.extend(struct.pack("!H", config.TAG_MAX_PLAYERS))  # Tag for Max Players
data.extend(struct.pack("!H", 4))
data.extend(struct.pack("!I", 10))

data.extend(struct.pack("!H", config.TAG_SUCCESS))  # Tag for Success
data.extend(struct.pack("!H", 1))
data.extend(struct.pack("!B", 1))

data.extend(struct.pack("!H", config.TAG_ERROR_MESSAGE))  # Tag for Error Message
data.extend(struct.pack("!H", len("No error")))
data.extend("No error".encode())

# Nested Rooms
room_data = bytearray()

# Room 1
room_data.extend(struct.pack("!H", config.TAG_ROOM))  # Tag for Room

# Construct room 1 data
room1_data = bytearray()
room1_data.extend(struct.pack("!H", config.TAG_ROOM_ID))  # Tag for Room ID
room1_data.extend(struct.pack("!H", len("room_01")))
room1_data.extend("room_01".encode())

room1_data.extend(struct.pack("!H", config.TAG_CURRENT_PLAYERS))  # Tag for Current Players
room1_data.extend(struct.pack("!H", 4))
room1_data.extend(struct.pack("!I", 5))

room1_data.extend(struct.pack("!H", config.TAG_MAX_PLAYERS))  # Tag for Max Players
room1_data.extend(struct.pack("!H", 4))
room1_data.extend(struct.pack("!I", 10))

# Append room 1 data to room_data
room_data.extend(struct.pack("!H", len(room1_data)))  # Length of room 1 data
room_data.extend(room1_data)

# Room 2
room_data.extend(struct.pack("!H", config.TAG_ROOM))  # Tag for Room

# Construct room 2 data
room2_data = bytearray()
room2_data.extend(struct.pack("!H", config.TAG_ROOM_ID))  # Tag for Room ID
room2_data.extend(struct.pack("!H", len("room_02")))
room2_data.extend("room_02".encode())

room2_data.extend(struct.pack("!H", config.TAG_CURRENT_PLAYERS))  # Tag for Current Players
room2_data.extend(struct.pack("!H", 4))
room2_data.extend(struct.pack("!I", 6))

room2_data.extend(struct.pack("!H", config.TAG_MAX_PLAYERS))  # Tag for Max Players
room2_data.extend(struct.pack("!H", 4))
room2_data.extend(struct.pack("!I", 13))

# Append room 2 data to room_data
room_data.extend(struct.pack("!H", len(room2_data)))  # Length of room 2 data
room_data.extend(room2_data)

data.extend(struct.pack("!H", config.TAG_ROOMS))  # Tag for Rooms
data.extend(struct.pack("!H", len(room_data)))
data.extend(room_data)

# Parse the TLV data
parsed_data = parser.parse_tlv(data, 0)
print(parsed_data)


game_info = {
    "map": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1], [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1], [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1], [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1], [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1], [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1], [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1], [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1], [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1], [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1], [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1], [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1], [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1], [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1], [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]],
    "player_colours": [(123, 123, 1), (123, 123, 2), (123, 123, 3), (123, 123, 4)],
    "map_colours": [(0, 0, 0), (1, 2, 2), (3, 4, 4)],
    "player_positions": [(1, 1), (1, 3), (3, 1), (3, 3)]
}

packed_info = parser.encode_tlv(config.TAG_GAME_INFO, game_info)
print(packed_info)
unpacked_info, _ = parser.read_tlv(packed_info, 0)
print(unpacked_info)
'''