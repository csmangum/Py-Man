import pygame
from pygame.locals import *
from constants import *
from pacman import PacMan
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from maze import MazeData


class GameController:
    """
    Main game controller class.  This class is responsible for
    initializing the game, loading the data, and updating the game
    state.  It also handles the main game loop and rendering.

    Attributes
    ----------
    screen : pygame.Surface
        The main game screen
    background : pygame.Surface
        The background image
    clock : pygame.time.Clock
        The game clock
    fruit : Fruit
        The fruit object
    pause : Pause
        The pause object
    level : int
        The current game level
    lives : int
        The number of lives remaining
    score : int
        The current score
    textgroup : TextGroup
        The text group object
    lifesprites : LifeSprites
        The life sprites object
    flashBG : bool
        Whether or not the background is flashing
    flashTime : float
        The time between background flashes
    flashTimer : float
        The current time since last background flash
    fruitCaptured : list
        A list of fruit images captured
    fruitNode : Node
        The node where the fruit is located
    mazedata : MazeData
        The maze data object

    Methods
    -------
    set_background()
        Sets the background image
    start_game()
        Starts the game
    update()
        Updates the game state
    check_events()
        Checks for user input
    check_pellet_events()
        Checks for pellet events
    check_ghost_events()
        Checks for ghost events
    check_fruit_events()
        Checks for fruit events
    show_entities()
        Shows the entities
    hide_entities()
        Hides the entities
    next_level()
        Starts the next level
    restart_game()
        Restarts the game
    reset_level()
        Resets the current level
    update_score()
        Updates the score
    render()
        Renders the game
    """

    def __init__(self, render_game: bool = True) -> None:
        self.render_game = render_game
        if render_game:
            pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()

    def set_background(self) -> None:
        """
        Sets up the game's background, including a normal background
        and a flashing one.
        """
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.construct_background(
            self.background_norm, self.level % 5
        )
        self.background_flash = self.mazesprites.construct_background(
            self.background_flash, 5
        )
        self.flashBG = False
        self.background = self.background_norm

    def start_game(self) -> None:
        """
        Loads the maze for the current level, sets up the maze sprites, nodes,
        Pacman, pellets, and ghosts. It also configures the starting positions
        and behaviors of the ghosts.

        Order of operations:
        1. Load the maze
        2. Set up the maze sprites
        3. Set up the nodes
        4. Set up Pacman
        5. Set up the pellets
        6. Set up the ghosts
        7. Set up the ghost starting positions
        8. Set up the ghost behaviors
        9. Set up the ghost home nodes
        10. Set up the ghost home access
        11. Set up the ghost access
        """
        self.mazedata.load_maze(self.level)
        self.mazesprites = MazeSprites(
            "game/assets/" + self.mazedata.obj.name + ".txt",
            "game/assets/" + self.mazedata.obj.name + "_rotation.txt",
        )
        self.set_background()
        self.nodes = NodeGroup("game/assets/" + self.mazedata.obj.name + ".txt")
        self.mazedata.obj.set_portal_pairs(self.nodes)
        self.mazedata.obj.connect_home_nodes(self.nodes)
        self.pacman = PacMan(
            self.nodes.get_node_from_tiles(*self.mazedata.obj.pacmanStart)
        )
        self.pellets = PelletGroup("game/assets/" + self.mazedata.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.get_start_temp_node(), self.pacman)

        self.ghosts.pinky.set_start_node(
            self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(2, 3))
        )
        self.ghosts.inky.set_start_node(
            self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(0, 3))
        )
        self.ghosts.clyde.set_start_node(
            self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(4, 3))
        )
        self.ghosts.set_spawn_node(
            self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(2, 3))
        )
        self.ghosts.blinky.set_start_node(
            self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(2, 0))
        )

        self.nodes.deny_home_access(self.pacman)
        self.nodes.deny_home_access_list(self.ghosts)
        self.ghosts.inky.startNode.deny_access(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.deny_access(LEFT, self.ghosts.clyde)
        self.mazedata.obj.deny_ghosts_access(self.ghosts, self.nodes)

    def update(self) -> None:
        """
        Updates the game state by updating all game entities
        (like Pacman, ghosts, pellets, etc.) and checking for various game
        events (like collisions).

        Also, handles the game's rendering.

        1. Game clock is updated.
        2. Update the text group, pellets, ghosts,and fruit. If the game is not
            paused, then the ghosts and fruit are updated.
        3. If Pacman is alive and the game is not paused, Pacman is updated.
            Otherwise, Pacman is updated regardless of whether the game is paused or not.
        4. If the background is flashing, the background is updated.
        5. Pause is updated.
        6. Game checks for events and renders the game.
        """
        dt = self.clock.tick(30) / 1000.0
        self.dt = dt
        self.textgroup.update(dt)
        self.pellets.update(dt)

        # Update ghosts, fruit, and check for pellet events
        if not self.pause.paused:
            self.ghosts.update(self)
            if self.fruit is not None:
                self.fruit.update(self)
            self.check_pellet_events()
            self.check_ghost_events()
            self.check_fruit_events()

        # Play when pacman is alive and not paused
        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(self)
        else:
            self.pacman.update(self)

        # Flash background
        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        # Update pause
        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()

        # Finish update and render
        self.check_events()
        if self.render_game:
            self.render()

    def check_events(self) -> None:
        """
        Checks for user input events, like quitting the game or pausing.

        If the user presses the space bar, the game is paused.
        If the user presses the escape key, the game is exited.
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.set_pause(player_paused=True)
                        if not self.pause.paused:
                            self.textgroup.hide_text()
                            self.show_entities()
                        else:
                            self.textgroup.show_text(PAUSETXT)
                            # self.hide_entities()

    def check_pellet_events(self) -> None:
        """
        Checks if Pacman has eaten any pellets and handles the consequences.

        If Pacman eats a pellet, the pellet is removed from the pellet list, the
            score is updated, and the ghost freight????(sp) mode is started if Pacman
            eats a power pellet.
        If Pacman eats all the pellets, the background flashes and the game is
            paused for 3 seconds before starting the next level.
        """
        pellet = self.pacman.eat_pellets(self.pellets.pellet_List)
        if pellet:
            self.pellets.numEaten += 1
            self.update_score(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allow_access(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allow_access(LEFT, self.ghosts.clyde)
            self.pellets.pellet_List.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.start_freight()
            if self.pellets.is_empty():
                self.flashBG = True
                self.hide_entities()
                self.pause.set_pause(pause_time=3, func=self.next_level)

    def check_ghost_events(self) -> None:
        """
        Checks for collisions between Pacman and the ghosts and handles the outcomes.

        If Pacman collides with a ghost in freight mode, the ghost and Pacman
            are hidden, the score is updated, and the ghost is sent back to its
            spawn node.
        If Pacman collides with a ghost in any other mode, Pacman dies and the
            game is paused for 3 seconds before restarting the level.
        """
        for ghost in self.ghosts:
            if self.pacman.collide_ghost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.update_score(ghost.points)
                    self.textgroup.add_text(
                        str(ghost.points),
                        WHITE,
                        ghost.position.x,
                        ghost.position.y,
                        8,
                        time=1,
                    )
                    self.ghosts.update_points()
                    self.pause.set_pause(pause_time=1, func=self.show_entities)
                    ghost.start_spawn()
                    self.nodes.allow_home_access(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.remove_image()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.show_text(GAMEOVERTXT)
                            self.pause.set_pause(pause_time=3, func=self.restart_game)
                        else:
                            self.pause.set_pause(pause_time=3, func=self.reset_level)

    def check_fruit_events(self) -> None:
        """
        Checks for events related to the fruit, like if Pacman has eaten it.

        If Pacman eats the fruit, the score is updated and the fruit is removed.
        If the fruit is destroyed, the fruit is removed.
        """
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.get_node_from_tiles(9, 20), self.level)
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.update_score(self.fruit.points)
                self.textgroup.add_text(
                    str(self.fruit.points),
                    WHITE,
                    self.fruit.position.x,
                    self.fruit.position.y,
                    8,
                    time=1,
                )
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def show_entities(self) -> None:
        """
        Shows the entities, like Pacman and the ghosts.
        """
        self.pacman.visible = True
        self.ghosts.show()

    def hide_entities(self) -> None:
        """
        Hides the entities, like Pacman and the ghosts.
        """
        self.pacman.visible = False
        self.ghosts.hide()

    def next_level(self) -> None:
        """
        Progresses the game to the next level.
        """
        self.show_entities()
        self.level += 1
        self.pause.paused = True
        self.start_game()
        self.textgroup.update_level(self.level)

    def restart_game(self) -> None:
        """
        Restarts the game from the beginning.
        """
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.start_game()
        self.score = 0
        self.textgroup.update_score(self.score)
        self.textgroup.update_level(self.level)
        self.textgroup.show_text(READYTXT)
        self.lifesprites.reset_lives(self.lives)
        self.fruitCaptured = []

    def reset_level(self) -> None:
        """
        Resets the current level.
        """
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.show_text(READYTXT)

    def update_score(self, points: int) -> None:
        """
        Updates the player's score.

        Parameters
        ----------
        points : int
            The amount of points to add to the score
        """
        self.score += points
        self.textgroup.update_score(self.score)

    def render(self) -> None:
        """
        Renders all game entities and UI elements onto the screen.

        1. The background is rendered.
        2. The nodes are rendered.
        3. The pellets are rendered.
        4. The fruit is rendered.
        5. Pacman is rendered.
        6. The ghosts are rendered.
        7. The text group is rendered.
        8. The lives sprites are rendered.
        9. The fruit captured sprites are rendered.
        """
        self.screen.blit(self.background, (0, 0))
        # self.nodes.render(self.screen) #! Why is this commented out?
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        # Lifesprites
        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        # Fruit captured
        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i + 1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.start_game()
    while True:
        game.update()
