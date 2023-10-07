from typing import Union
import pygame
from pygame.locals import *
from vector import Vector2  #! Why is this not used?
from constants import *
from entity import Entity
from sprites import PacmanSprites

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nodes import Node
    from ghosts import Ghost


class Pacman(Entity):
    """
    Pacman class

    Pacman is the main character of the game. He is controlled by the player
    and must eat all the pellets in the maze while avoiding the ghosts.

    Attributes
    ----------
    name : string
        The name of the entity
    color : tuple
        The color of the entity
    direction : int
        The direction the entity is moving
    alive : bool
        Whether or not the entity is alive
    sprites : PacmanSprites
        The sprites for the entity

    Methods
    -------
    reset()
        Resets the entity
    die()
        Kills the entity
    update(dt)
        Updates the entity
    getValidKey()
        Gets the key pressed by the player
    eatPellets(pelletList)
        Checks if the entity has eaten a pellet
    collideGhost(ghost)
        Checks if the entity has collided with a ghost
    collideCheck(other)
        Checks if the entity has collided with another entity
    """

    def __init__(self, node: Node) -> None:
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)  # Pacman starts between nodes 1 and 2
        self.alive = True
        self.sprites = PacmanSprites(self)

    def reset(self) -> None:
        """
        Resets the Pac-Man to its initial state, facing left and alive.
        It also resets its sprites.
        """
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self) -> None:
        """
        Sets the Pac-Man's state to dead and stops its movement.
        """
        self.alive = False
        self.direction = STOP

    def update(self, dt: float) -> None:
        """
        Updates the Pac-Man's state based on the time delta (dt).

        It handles the movement, checks for overshooting targets, and handles
        portal transitions (like when Pac-Man goes off one side of the screen
        and appears on the other). It also checks for direction reversal.

        Parameters
        ----------
        dt : float
            The time delta
        """
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def getValidKey(self) -> str:
        """
        Checks for keyboard inputs and returns the direction corresponding to
        the key pressed.

        If no movement key is pressed, it returns STOP.

        Returns
        -------
        str
            The direction corresponding to the key pressed
        """
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eatPellets(self, pelletList: list) -> Union[None, object]:
        """
        Checks for collisions between Pac-Man and any pellet in the provided list.

        If a collision is detected, it returns the pellet that was "eaten".

        Parameters
        ----------
        pelletList : list
            A list of pellets to check for collisions with

        Returns
        -------
        object
            The pellet that was "eaten" if a collision is detected, None otherwise
        """
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost: "Ghost") -> bool:
        """
        Checks if Pac-Man has collided with a ghost.

        Returns True if a collision is detected, False otherwise.

        Parameters
        ----------
        ghost : Ghost
            The ghost to check for collisions with

        Returns
        -------
        bool
            True if a collision is detected, False otherwise
        """
        return self.collideCheck(ghost)

    def collideCheck(self, other: "object") -> bool:
        """
        A general collision detection method that checks if Pac-Man has collided
        with another entity (like a ghost or pellet).

        It calculates the distance between the two entities and checks if
        it's less than or equal to the sum of their collision radii.

        Returns True if a collision is detected, False otherwise.

        Parameters
        ----------
        other : object
            The entity to check for collisions with

        Returns
        -------
        bool
            True if a collision is detected, False otherwise
        """
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius) ** 2
        if dSquared <= rSquared:
            return True
        return False
