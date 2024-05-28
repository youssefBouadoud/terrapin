import threading
import numpy as np
from networking.server.round import generate_palette, generate_map

STATE_WAITING = 0x5001
STATE_FULL = 0x5002
STATE_STARTING = 0x5003
STATE_PLAYING = 0x5004
STATE_PLAYING_FULL = 0x5005
STATE_PAUSED = 0x5006
STATE_ENDED = 0x5007
STATE_CLOSED = 0x5008


class Room:
    NUM_ROUNDS = 5

    def __init__(self, id, max_players, owner):
        self.id = id
        self.max_players = max_players
        self.current_players = 0
        self.players = {}
        self.maze = None
        self.state = STATE_WAITING
        self.lock = threading.Lock()
        self.owner = owner
        self.round_number = 0

    def add_player(self, player):
        with self.lock:
            if self.state in (STATE_WAITING, STATE_PLAYING):
                self.players[player.username] = player
                player.current_room = self.id
                self.current_players += 1

                if self.current_players == self.max_players:
                    self.state = STATE_FULL if self.state == STATE_WAITING else STATE_PLAYING_FULL
                return True
        return False

    def remove_player(self, player):
        with self.lock:
            if self.players.get(player.username) is not None:
                del self.players[player.username]
                self.current_players -= 1
                player.current_room = None

                if self.current_players == 0:
                    self.state = STATE_CLOSED
                elif self.state == STATE_FULL:
                    self.state = STATE_WAITING
                elif self.state == STATE_PLAYING_FULL:
                    self.state = STATE_PLAYING

                return True
        return False

    def get_room_info(self):
        return {
            "id": self.id,
            "current_players": self.current_players,
            "max_players": self.max_players,
            "state": self.state,
            "players": [username for username in self.players],
            "round": self.round_number,
            "num_rounds": self.NUM_ROUNDS,
            "owner": self.owner,
            "min_players": 2,
        }

    def start_new_round(self):
        self.round_number += 1

    def start_game(self):
        generated_map = generate_map()
        self.maze = generated_map.tolist()
        game_info = {
            "map": self.maze,
            "player_colours": generate_palette(self.max_players),
            "map_colours": generate_palette(len(set(generated_map.flat))),
            "player_positions": [(1, 1),
                                 (1, len(self.maze[0]) - 2),
                                 (len(self.maze) - 2, 1),
                                 (len(self.maze) - 2, len(self.maze[0]) - 2),
                                 ],
        }

        for player, pos in zip(self.players.values(), game_info["player_positions"]):
            player.x, player.y = pos[0], pos[1]

        return game_info

    def broadcast(self, data):
        for player in self.players.values():
            player.send(data)


    def move_player(self, username, direction):
        player = self.players.get(username)
        if player is None:
            return False

        current_pos = (player.x, player.y)
        new_pos = self.calculate_new_position(current_pos, direction)
        if self.is_valid_position(new_pos):
            player.x, player.y = new_pos
            print("current pos of", username, (player.x, player.y), "new pos", new_pos, "valid")
            return True
        print("current pos of", username, (player.x, player.y), "new pos", new_pos, "not valid")

        return False

    def calculate_new_position(self, current_pos, direction):
        x, y = current_pos
        if direction == "UP":
            return (x, y - 1)
        elif direction == "DOWN":
            return (x, y + 1)
        elif direction == "LEFT":
            return (x - 1, y)
        elif direction == "RIGHT":
            return (x + 1, y)
        return current_pos

    def is_valid_position(self, pos):
        x, y = pos
        return self.maze[x][y] == 0 or self.maze[x][y] == 2 # Assuming 0 is walkable, 1 is wall

    def get_positions_info(self):
        positions = [(player.x, player.y) for player in self.players.values()]
        return positions

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.lock = threading.Lock()

    def create_room(self, room_id, player, max_players):
        with self.lock:
            if self.rooms.get(room_id) is None:
                self.rooms[room_id] = Room(room_id, max_players, player.username)
                self.rooms[room_id].add_player(player)
                return True
        return False

    def join_room(self, room_id, player):
        with self.lock:
            if player.current_room is not None:
                return False

            if room := self.rooms.get(room_id):
                return room.add_player(player)
        return False

    def leave_room(self, player):
        with self.lock:
            if room := self.rooms.get(player.current_room) is not None:
                if room.remove_player(player):
                    if room.state == STATE_CLOSED:
                        del self.rooms[room.id]
                    return True
        return False

    def list_rooms(self):
        with self.lock:
            rooms = [room.get_room_info() for room in self.rooms.values()]
        return rooms

    def get_room(self, room_id):
        return self.rooms.get(room_id)

    def set_room_state(self, room_id, state):
        room = self.rooms.get(room_id)
        if room is not None:
            if state in (
                    STATE_WAITING, STATE_FULL, STATE_STARTING, STATE_PLAYING, STATE_PLAYING_FULL, STATE_PAUSED,
                    STATE_ENDED,
                    STATE_CLOSED):
                room.state = state
                return True
        return False
