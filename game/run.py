import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazedata import MazeData


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
    setBackground()
        Sets the background image
    startGame()
        Starts the game
    update()
        Updates the game state
    checkEvents()
        Checks for user input
    checkPelletEvents()
        Checks for pellet events
    checkGhostEvents()
        Checks for ghost events
    checkFruitEvents()
        Checks for fruit events
    showEntities()
        Shows the entities
    hideEntities()
        Hides the entities
    nextLevel()
        Starts the next level
    restartGame()
        Restarts the game
    resetLevel()
        Resets the current level
    updateScore()
        Updates the score
    render()
        Renders the game
    """

    def __init__(self) -> None:
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

    def setBackground(self) -> None:
        """
        Sets up the game's background, including a normal background
        and a flashing one.
        """
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(
            self.background_norm, self.level % 5
        )
        self.background_flash = self.mazesprites.constructBackground(
            self.background_flash, 5
        )
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self) -> None:
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
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(
            self.mazedata.obj.name + ".txt", self.mazedata.obj.name + "_rotation.txt"
        )
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name + ".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart)
        )
        self.pellets = PelletGroup(self.mazedata.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.inky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3))
        )
        self.ghosts.clyde.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3))
        )
        self.ghosts.setSpawnNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.blinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0))
        )

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

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
        self.textgroup.update(dt)
        self.pellets.update(dt)

        # Update ghosts, fruit, and check for pellet events
        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        # Play when pacman is alive and not paused
        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

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
        self.checkEvents()
        self.render()

    def checkEvents(self) -> None:
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
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            # self.hideEntities()

    def checkPelletEvents(self) -> None:
        """
        Checks if Pacman has eaten any pellets and handles the consequences.

        If Pacman eats a pellet, the pellet is removed from the pellet list, the
            score is updated, and the ghost freight????(sp) mode is started if Pacman
            eats a power pellet.
        If Pacman eats all the pellets, the background flashes and the game is
            paused for 3 seconds before starting the next level.
        """
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self) -> None:
        """
        Checks for collisions between Pacman and the ghosts and handles the outcomes.

        If Pacman collides with a ghost in freight mode, the ghost and Pacman
            are hidden, the score is updated, and the ghost is sent back to its
            spawn node.
        If Pacman collides with a ghost in any other mode, Pacman dies and the
            game is paused for 3 seconds before restarting the level.
        """
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textgroup.addText(
                        str(ghost.points),
                        WHITE,
                        ghost.position.x,
                        ghost.position.y,
                        8,
                        time=1,
                    )
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)

    def checkFruitEvents(self) -> None:
        """
        Checks for events related to the fruit, like if Pacman has eaten it.

        If Pacman eats the fruit, the score is updated and the fruit is removed.
        If the fruit is destroyed, the fruit is removed.
        """
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(
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

    def showEntities(self) -> None:
        """
        Shows the entities, like Pacman and the ghosts.
        """
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self) -> None:
        """
        Hides the entities, like Pacman and the ghosts.
        """
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self) -> None:
        """
        Progresses the game to the next level.
        """
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self) -> None:
        """
        Restarts the game from the beginning.
        """
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self) -> None:
        """
        Resets the current level.
        """
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points) -> None:
        """
        Updates the player's score.

        Parameters
        ----------
        points : int
            The amount of points to add to the score
        """
        self.score += points
        self.textgroup.updateScore(self.score)

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
    game.startGame()
    while True:
        game.update()
