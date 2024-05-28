import jwt
import pygame
import pygame_gui

from game.Player import Player
from networking import config, tlv_definitions
from networking.client.client import Client
from networking.tlv_parser import TLVParser
from threading import Lock


class Game:
    def __init__(self):
        self.lock = Lock()
        self.game_info = None
        self.room_info = None
        self.jwt_token = None
        self.client = Client()
        self.game_running = True
        self.screen = None
        self.ui_manager = None
        self.clock = pygame.time.Clock()
        self.state = "MAIN_MENU"
        self.username = ''

    def main_menu(self):
        self.ui_manager = pygame_gui.UIManager((800, 579))
        background = pygame.image.load("assets/background.jpg")

        connect_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 120), (150, 75)),
                                                      text='Connect', manager=self.ui_manager,
                                                      anchors={'center': 'center'})

        address_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, -60), (300, 60)),
                                                                 placeholder_text='Enter server ip',
                                                                 manager=self.ui_manager, anchors={'center': 'center'})

        port_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 30), (300, 60)),
                                                              placeholder_text='Enter server port',
                                                              manager=self.ui_manager, anchors={'center': 'center'})
        port_text_entry.set_allowed_characters('numbers')

        while self.state == "MAIN_MENU":
            self.process_packets()
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                    self.state = "EXIT"
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == connect_button:
                        try:
                            self.handle_server_connection(address_text_entry.text, int(port_text_entry.text))
                        except ValueError:
                            alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                                       html_message="Invalid IP:port format",
                                                                       window_title="Error!",
                                                                       manager=self.ui_manager)
                self.ui_manager.process_events(event)
            self.ui_manager.update(time_delta)

            self.screen.blit(background, (0, 0))
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

    def register(self):
        self.ui_manager = pygame_gui.UIManager((800, 579))
        background = pygame.image.load("assets/background.jpg")

        register_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 120), (250, 75)),
                                                       text='Register', manager=self.ui_manager,
                                                       anchors={'center': 'center'})

        login_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 200), (250, 30)),
                                                    text='Already a member? Log In', manager=self.ui_manager,
                                                    anchors={'center': 'center'})

        username_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, -60), (300, 60)),
                                                                  placeholder_text='Enter your username',
                                                                  manager=self.ui_manager, anchors={'center': 'center'})

        password_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 30), (300, 60)),
                                                                  placeholder_text='Enter your password',
                                                                  manager=self.ui_manager, anchors={'center': 'center'})
        password_text_entry.set_text_hidden()

        while self.state == "REGISTER":
            self.process_packets()
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                    self.state = "EXIT"
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == register_button:
                        try:
                            self.client.send_register_request(username_text_entry.text, password_text_entry.text)
                        except ValueError:
                            alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((100, 275), (100, 50)),
                                                                       html_message="Unable to register, please try again",
                                                                       window_title="Error!",
                                                                       manager=self.ui_manager)
                    elif event.ui_element == login_button:
                        self.state = "LOGIN"
                        continue

                self.ui_manager.process_events(event)
            self.ui_manager.update(time_delta)

            self.screen.blit(background, (0, 0))
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

    def login(self):
        self.ui_manager = pygame_gui.UIManager((800, 579))
        background = pygame.image.load("assets/background.jpg")

        login_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 120), (250, 75)),
                                                    text='Login', manager=self.ui_manager,
                                                    anchors={'center': 'center'})

        register_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 200), (250, 30)),
                                                       text='Are you new? Register now!', manager=self.ui_manager,
                                                       anchors={'center': 'center'})

        username_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, -60), (300, 60)),
                                                                  placeholder_text='Enter your username',
                                                                  manager=self.ui_manager, anchors={'center': 'center'})

        password_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 30), (300, 60)),
                                                                  placeholder_text='Enter your password',
                                                                  manager=self.ui_manager, anchors={'center': 'center'})
        password_text_entry.set_text_hidden()

        while self.state == "LOGIN":
            self.process_packets()
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                    self.state = "EXIT"
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == login_button:
                        try:
                            self.client.send_login_request(username_text_entry.text, password_text_entry.text)
                        except ValueError:
                            alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                                       html_message="Unable to log in, please try again",
                                                                       window_title="Error!",
                                                                       manager=self.ui_manager)
                    elif event.ui_element == register_button:
                        self.state = "REGISTER"

                self.ui_manager.process_events(event)
            self.ui_manager.update(time_delta)

            self.screen.blit(background, (0, 0))
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

    def lobby(self):
        self.ui_manager = pygame_gui.UIManager((800, 579))
        self.clock = pygame.time.Clock()
        background = pygame.image.load("assets/background.jpg")

        player_list = pygame_gui.elements.ui_selection_list.UISelectionList(
            relative_rect=pygame.Rect((0, 0), (300, 400)),
            item_list=self.room_info["players"],
            manager=self.ui_manager,
            anchors={'center': 'center'})

        room_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((0, -250), (300, 150)),
                                                          parent_element=player_list,
                                                          text=f"Room code: {self.room_info['id']}",
                                                          manager=self.ui_manager,
                                                          anchors={'center': 'center'})

        start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-100, 250), (150, 55)),
                                                    text='Start', manager=self.ui_manager,
                                                    anchors={'center': 'center'})
        start_button.disable()

        leave_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 250), (150, 55)),
                                                    text='Leave', manager=self.ui_manager,
                                                    anchors={'center': 'center'})

        current_players_label = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect((0, 120), (100, 50)),
                                                                     text=f"{self.room_info['current_players']}/{self.room_info['max_players']}",
                                                                     manager=self.ui_manager,
                                                                     anchors={'center': 'center'})

        while self.state == "LOBBY":
            self.process_packets()
            time_delta = self.clock.tick(60) / 1000.0

            player_list.set_item_list(self.room_info["players"])
            current_players_label.set_text(f"{self.room_info['current_players']}/{self.room_info['max_players']}")

            if self.room_info["current_players"] >= self.room_info["min_players"] and self.room_info[
                "owner"] == self.username:
                start_button.enable()
            else:
                start_button.disable()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                    self.state = "EXIT"
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        try:
                            self.client.send_start_game_request(self.username, self.jwt_token, self.room_info["id"])
                        except ValueError:
                            alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                                       html_message="Unable to start the game, please try again",
                                                                       window_title="Error!",
                                                                       manager=self.ui_manager)
                    if event.ui_element == leave_button:
                        try:
                            self.client.send_leave_room_request(self.username, self.jwt_token)
                        except ValueError:
                            alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                                       html_message="Unable to start the game, please try again",
                                                                       window_title="Error!",
                                                                       manager=self.ui_manager)
                self.ui_manager.process_events(event)
            self.ui_manager.update(time_delta)

            self.screen.blit(background, (0, 0))
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

    def handle_server_connection(self, server_ip, server_port):
        return self.client.connect(server_ip, server_port, "server.crt")

    def room_selection(self):
        self.ui_manager = pygame_gui.UIManager((800, 579))
        background = pygame.image.load("assets/background.jpg")

        room_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, -60), (300, 60)),
                                                              placeholder_text='Room code',
                                                              manager=self.ui_manager, anchors={'center': 'center'})

        create_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-80, 40), (130, 50)),
                                                     text='Create room', manager=self.ui_manager,
                                                     anchors={'center': 'center'})

        join_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((80, 40), (130, 50)),
                                                   text='Join room', manager=self.ui_manager,
                                                   anchors={'center': 'center'})

        while self.state == "ROOM_SELECTION":
            self.process_packets()
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                    self.state = "EXIT"
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == create_button:
                        self.room_id = room_text_entry.text
                        self.client.send_create_room(self.username, self.jwt_token, room_text_entry.text)
                    elif event.ui_element == join_button:
                        self.room_id = room_text_entry.text
                        self.client.send_join_room(self.username, self.jwt_token, room_text_entry.text)

                self.ui_manager.process_events(event)
            self.ui_manager.update(time_delta)

            self.screen.blit(background, (0, 0))
            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()

    def game_loop(self):
        self.clock = pygame.time.Clock()
        while self.state == "GAME":
            self.process_packets()
            time_delta = self.clock.tick(60) / 1000.0
            self.render()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    print(event.type)
                    if event.type == pygame.QUIT:
                        self.game_running = False
                        self.state = "EXIT"
                    elif event.type == pygame.KEYDOWN:
                        direction = None
                        if event.key == pygame.K_UP:
                            direction = "UP"
                        elif event.key == pygame.K_DOWN:
                            direction = "DOWN"
                        elif event.key == pygame.K_LEFT:
                            direction = "LEFT"
                        elif event.key == pygame.K_RIGHT:
                            direction = "RIGHT"

                        if direction:
                            self.client.send_move_request(self.username, self.jwt_token, direction, self.room_id)
            pygame.display.update()
            self.clock.tick(60)

    def process_packets(self):
        while not self.client.event_queue.empty():
            try:
                packet = self.client.event_queue.get()
                self.handle_packet(packet)
            except:
                return

    def handle_packet(self, data):
        offset = 0

        definitions = tlv_definitions.TLVDefinitions(tag_mappings=tlv_definitions.mappings)
        tlv_parser = TLVParser(definitions)

        packet_id = int.from_bytes(data[offset:offset + definitions.tag_size], byteorder='big')
        offset += definitions.tag_size

        print("pid", hex(packet_id))

        try:
            fields = tlv_parser.parse_tlv(data, offset)
        except ValueError as e:
            print(e)

        print("fields", fields)

        if packet_id == config.RESPONSE_LOGIN_RESULT:
            if fields[0]:
                with self.lock:
                    self.jwt_token = fields[1]
                    self.username = jwt.decode(self.jwt_token, options={"verify_signature": False})["username"]
                    self.state = "ROOM_SELECTION"
            else:
                alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                           html_message="Unable to log in, please try again",
                                                           window_title="Error!",
                                                           manager=self.ui_manager)
        elif packet_id == config.RESPONSE_REGISTER_RESULT:
            if fields[0]:
                with self.lock:
                    self.state = "LOGIN"
            else:
                alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                           html_message="Unable to register, please try again",
                                                           window_title="Error!",
                                                           manager=self.ui_manager)
        elif packet_id == config.RESPONSE_JOIN_ROOM_RESULT:
            if fields[0]:
                with self.lock:
                    self.room_info = fields[1]
                    self.state = "LOBBY"
            else:
                alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                           html_message="Unable to join room, please try again",
                                                           window_title="Error!",
                                                           manager=self.ui_manager)
        elif packet_id == config.RESPONSE_LEAVE_ROOM_RESULT:
            if fields[0]:
                with self.lock:
                    self.state = "ROOM_SELECTION"
            else:
                alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                           html_message="Unable to leave room, please try again",
                                                           window_title="Error!",
                                                           manager=self.ui_manager)
        elif packet_id == config.RESPONSE_LIST_ROOMS_RESULT:
            with self.lock:
                self.room_list = fields[0]
        elif packet_id == config.RESPONSE_START_GAME_RESULT:
            if fields[0]:
                with self.lock:
                    self.state = "GAME"
            else:
                alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                           html_message="Unable to start game, please try again",
                                                           window_title="Error!",
                                                           manager=self.ui_manager)
        elif packet_id == config.TAG_ROOM:
            with self.lock:
                self.room_info = fields[0]
        elif packet_id == config.SIGNAL_START_GAME:
            with self.lock:
                self.state = "GAME"
                self.game_info = fields[0]
        elif packet_id == config.ACCEPTED:
            self.state = "REGISTER"
        elif packet_id == config.RESPONSE_CREATE_ROOM_RESULT:
            if fields[0]:
                with self.lock:
                    self.room_info = fields[1]
                    self.state = "LOBBY"

            else:
                alert = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((400, 289), (100, 50)),
                                                           html_message="Unable to create room, please try again",
                                                           window_title="Error!",
                                                           manager=self.ui_manager)
        elif packet_id == config.SIGNAL_PLAYER_JOIN:
            if fields[0]:
                with self.lock:
                    self.room_info = fields[1]
        elif packet_id == config.RESPONSE_START_GAME_RESULT:
            if fields[0]:
                self.state = "GAME"
        elif packet_id == config.SIGNAL_START_GAME:
            with self.lock:
                self.state = "GAME"
                self.game_info = fields[0]
        elif packet_id == config.SIGNAL_UPDATE_POSITIONS:
            with self.lock:
                self.game_info["player_positions"] = fields[0]
        elif packet_id == config.RESPONSE_MOVE_RESULT:
            if fields[0] is False:
                print("server refused the move")
        elif packet_id == config.SIGNAL_SCORE_UPDATE:
            with self.lock:
                self.winner = fields[0]
                print(f"Round feature work in progress, the winner of the round is {self.winner}")
                self.state = "WORK_IN_PROGRESS"
        else:
            pass

    def draw_maze(self, surface, m, color_map, cell_size):
        maze_map = m

        for y in range(len(m[0])):
            for x in range(len(m)):
                pygame.draw.rect(surface, color_map[maze_map[x][y]],
                                 pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

    def draw_centered_maze(self, screen, maze_surface):
        cx, cy = screen.get_rect().center
        maze_x = maze_surface.get_rect(center=(cx, cy)).x
        maze_y = maze_surface.get_rect(center=(cx, cy)).y

        screen.blit(maze_surface, maze_surface.get_rect(center=(cx, cy)))

    def render(self):
        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 579
        PADDING = 50
        MAZE_WIDTH = len(self.game_info["map"][0])
        MAZE_HEIGHT = len(self.game_info["map"])
        CELL_SIZE = min(((SCREEN_WIDTH - (2 * PADDING)) // MAZE_WIDTH),
                        ((SCREEN_HEIGHT - (2 * PADDING)) // MAZE_HEIGHT))
        maze = self.game_info["map"]
        self.screen.fill((0, 0, 0))

        maze_surface = pygame.Surface((CELL_SIZE * len(maze), CELL_SIZE * len(maze[0])))

        flattened_matrix = [element for row in maze for element in row]
        matrix_set = set(flattened_matrix)
        color_map = dict(zip(matrix_set, self.game_info["map_colours"]))

        self.draw_maze(maze_surface, maze, color_map, CELL_SIZE)
        self.draw_centered_maze(self.screen, maze_surface)

        cx, cy = self.screen.get_rect().center
        maze_x = maze_surface.get_rect(center=(cx, cy)).x
        maze_y = maze_surface.get_rect(center=(cx, cy)).y

        all_sprites = pygame.sprite.Group()
        for i in range(self.room_info["current_players"]):
            position = self.game_info["player_positions"][i]
            colour = self.game_info["player_colours"][i]
            player = Player(cell_size=CELL_SIZE,
                            absolute=(position[0] * CELL_SIZE + maze_x, position[1] * CELL_SIZE + maze_y),
                            relative=position,
                            maze=maze,
                            colour=colour
                            )
            all_sprites.add(player)

        self.screen.blit(maze_surface, maze_surface.get_rect(center=self.screen.get_rect().center))
        all_sprites.draw(self.screen)

        pygame.display.flip()

    def work_in_progress(self):
        self.ui_manager = pygame_gui.UIManager((800, 579))
        self.clock = pygame.time.Clock()
        self.screen.fill((0, 0, 0))
        winner_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((0, 0), (300, 100)),
                                                    html_text=f'Round feature work in progress, the winner of the '
                                                              f'round is {self.winner}',
                                                    manager=self.ui_manager, anchors={'center': 'center'})
        winner_text.enable()
        winner_text.background_colour = (255, 255, 255)
        self.ui_manager.draw_ui(self.screen)
        pygame.display.update()

    def run(self):
        pygame.init()
        pygame.display.set_caption("Terrapin")

        icon = pygame.image.load("assets/icon.ico")
        pygame.display.set_icon(icon)

        self.screen = pygame.display.set_mode((800, 579))

        background = pygame.Surface((800, 579))
        background.fill(pygame.Color('#000000'))

        self.ui_manager = pygame_gui.UIManager((800, 579))

        while self.game_running:
            if self.state == "MAIN_MENU":
                self.main_menu()
            elif self.state == "ROOM_SELECTION":
                self.room_selection()
            elif self.state == "GAME":
                self.game_loop()
            elif self.state == "REGISTER":
                self.register()
            elif self.state == "LOGIN":
                self.login()
            elif self.state == "LOBBY":
                self.lobby()
            elif self.state == "WORK_IN_PROGRESS":
                self.work_in_progress()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
