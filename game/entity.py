from abc import ABC
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.nodes import Node


class Entity(ABC):
    """
    Abstract base class for all entities in the game.

    Attributes
    ----------
    name : str
        The name of the entity.
    directions : dict
        A dictionary of directions, mapping direction constants to Vector2 objects.
    direction : int
        The current direction of the entity.
    speed : float
        The speed of the entity.
    radius : int
        The radius of the entity.
    collideRadius : int
        The collision radius of the entity.
    color : tuple
        The color of the entity.
    visible : bool
        Whether or not the entity is visible.
    disablePortal : bool
        Whether or not the entity can use portals.
    goal : Vector2
        The goal position of the entity.
    directionMethod : function
        The method used to determine the entity's direction.
    node : Node
        The current node of the entity.
    startNode : Node
        The starting node of the entity.
    target : Node
        The target node of the entity.
    position : Vector2
        The position of the entity.
    image : pygame.Surface
        The image of the entity.

    Methods
    -------
    setPosition()
        Sets the entity's position based on its current node's position.
    update(dt)
        Updates the entity's position based on its current direction and speed,
        taking into account the elapsed time (dt).
    validDirection(direction)
        Checks if the entity can move in the given direction.
    getNewTarget(direction)
        Gets the new target node for the entity, based on the given direction.
    overshotTarget()
        Checks if the entity has overshot its target node.
    reverseDirection()
        Reverses the entity's direction.
    oppositeDirection(direction)
        Checks if the given direction is the opposite of the entity's current
        direction.
    validDirections()
        Gets a list of valid directions for the entity.
    randomDirection(directions)
        Gets a random direction from the given list of directions.
    goalDirection(directions)
        Gets the direction that is closest to the entity's goal.
    setStartNode(node)
        Sets the entity's starting node.
    setBetweenNodes(direction)
        Sets the entity's position between its current node and the node in the
        given direction.
    reset()
        Resets the entity.
    setSpeed(speed)
        Sets the entity's speed.
    render(screen)
        Renders the entity.
    """

    def __init__(self, node: "Node") -> None:
        """
        Initializes various attributes for the entity, including its name,
        directions, speed, radius, color, visibility, and other properties.

        Sets the initial direction to "STOP."

        Takes a node as a parameter, representing the starting node of the entity.

        Parameters
        ----------
        node : Node
            The starting node of the entity.
        """
        self.name = None
        self.directions = {
            UP: Vector2(0, -1),
            DOWN: Vector2(0, 1),
            LEFT: Vector2(-1, 0),
            RIGHT: Vector2(1, 0),
            STOP: Vector2(),
        }
        self.direction = STOP
        self.setSpeed(100)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.randomDirection
        self.setStartNode(node)
        self.image = None

    def setPosition(self) -> None:
        """
        Sets the entity's position based on its current node's position.
        """
        self.position = self.node.position.copy()

    def update(self, dt: float) -> None:
        """
        Updates the entity's position based on its current direction and speed,
        taking into account the elapsed time (dt).

        Checks if the entity has overshot its target node, and if so, updates
        the node and direction.

        Parameters
        ----------
        dt : float
            The elapsed time since the last update.
        """
        self.position += self.directions[self.direction] * self.speed * dt

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def validDirection(self, direction: int) -> bool:
        """
        Checks if the entity can move in the given direction.

        Parameters
        ----------
        direction : int
            The direction to check.

        Returns
        -------
        bool
            True if the entity can move in the given direction, False otherwise.
        """
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def getNewTarget(self, direction: int) -> "Node":
        """
        Gets the new target node for the entity, based on the given direction.

        Parameters
        ----------
        direction : int
            The direction to check.

        Returns
        -------
        Node
            The new target node for the entity.
        """
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self) -> bool:
        """
        Checks if the entity has overshot its target node.

        Returns
        -------
        bool
            True if the entity has overshot its target node, False otherwise.
        """
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self) -> None:
        """
        Reverses the entity's direction.
        """
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction: int) -> bool:
        """
        Checks if the given direction is the opposite of the entity's current
        direction.

        Parameters
        ----------
        direction : int
            The direction to check.

        Returns
        -------
        bool
            True if the given direction is the opposite of the entity's current
            direction, False otherwise.
        """
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def validDirections(self) -> list:
        """
        Gets a list of valid directions for the entity.

        Returns
        -------
        list
            A list of valid directions for the entity.
        """
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions: list) -> int:
        """
        Gets a random direction from the given list of directions.

        Parameters
        ----------
        directions : list
            The list of directions to choose from.

        Returns
        -------
        int
            A random direction from the given list of directions.
        """
        return directions[randint(0, len(directions) - 1)]

    def goalDirection(self, directions: list) -> int:
        """
        Gets the direction that is closest to the entity's goal.

        Parameters
        ----------
        directions : list
            The list of directions to choose from.

        Returns
        -------
        int
            The direction that is closest to the entity's goal.
        """
        distances = []
        for direction in directions:
            vec = (
                self.node.position + self.directions[direction] * TILEWIDTH - self.goal
            )
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

    def setStartNode(self, node: "Node") -> None:
        """
        Sets the entity's starting node.

        Parameters
        ----------
        node : Node
            The starting node of the entity.
        """
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def setBetweenNodes(self, direction: int) -> None:
        """
        Sets the entity's position between its current node and the node in the
        given direction.

        Parameters
        ----------
        direction : int
            The direction to check.
        """
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def reset(self) -> None:
        """
        Resets the entity's state to its initial state, including its starting
        node, direction, speed, and visibility.
        """
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100
        self.visible = True

    def setSpeed(self, speed: float) -> None:
        """
        Sets the entity's speed based on a given value.

        Parameters
        ----------
        speed : float
            The speed of the entity.
        """
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen: pygame.Surface) -> None:
        """
        Renders the entity on the game screen.

        It either displays an image at the entity's position or draws a circle
        with a specified color and radius.

        Parameters
        ----------
        screen : pygame.Surface
            The game screen.
        """
        if self.visible:
            if self.image is not None:
                adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)
