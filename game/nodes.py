from abc import ABC, abstractmethod
import pygame
from vector import Vector2
from constants import *
import numpy as np

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from game.nodes import Node
    from game.entity import Entity


class Node(ABC):
    """
    Provides a structured way to represent and manage nodes in a maze or grid.

    It allows for easy connection between nodes, control over which game entities
    can move between nodes, and a way to visually represent the nodes and their connections

    Attributes
    ----------
    position : Vector2
        The position of the node in the maze
    neighbors : dict
        A dictionary of the neighboring nodes, with the direction as the key
    access : dict
        A dictionary of the game entities that can move in each direction

    Methods
    -------
    denyAccess(direction, entity)
        Removes the entity from the list of entities that can move in the given direction
    allowAccess(direction, entity)
        Adds the entity to the list of entities that can move in the given direction
    render(screen)
        Draws the node and its connections on the screen
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Initializes the node with a position using the Vector2 class.

        Initializes a dictionary neighbors to store neighboring nodes in each direction.

        Initializes a dictionary access to determine which game entities
        (PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT) can move in each direction
        from this node.

        Parameters
        ----------
        x : int
            The x coordinate of the node in the maze
        y : int
            The y coordinate of the node in the maze
        """
        self.position = Vector2(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}
        self.access = {
            UP: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            DOWN: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            LEFT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
        }

    def denyAccess(self, direction: int, entity: 'Entity') -> None:
        """
        Denies access for a specific entity in a given direction.

        This means the entity will not be able to move in that direction from this node.

        Parameters
        ----------
        direction : int
            The direction to deny access in.
            Directions are defined in constants.py
        entity : 'Entity'
            The entity to deny access to
        """
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction: int, entity: 'Entity') -> None:
        """
        Allows access for a specific entity in a given direction,
        enabling the entity to move in that direction from this node.

        Parameters
        ----------
        direction : int
            The direction to allow access in
        entity : 'Entity'
            The entity to allow access to
        """
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)

    def render(self, screen: pygame.Surface) -> None:
        """
        Renders the node and its connections to its neighbors on the provided
        screen (or surface).

        It draws lines to each of its neighbors and represents the node itself
        as a circle.

        Parameters
        ----------
        screen : pygame.Surface
            The screen or surface to draw the node on
        """
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)


class NodeGroup(ABC):
    """
    Provides a structured way to represent and manage groups of nodes in a
    maze or grid.

    It allows for easy connection between nodes, control over which game entities
    can move between nodes, and a way to visually represent the nodes and their
    connections

    Attributes
    ----------
    level : str
        The name of the maze file
    nodesLUT : dict
        A dictionary of all nodes in the maze, with their x and y coordinates
        as the key
    nodeSymbols : List[str]
        A list of symbols that represent nodes in the maze file
    pathSymbols : List[str]
        A list of symbols that represent paths in the maze file
    homekey : tuple
        The x and y coordinates of the home node

    Methods
    -------
    readMazeFile(textfile)
        Reads the maze layout from a file and returns it as a NumPy array
    createNodeTable(data, xoffset, yoffset)
        Constructs nodes based on the maze data
    constructKey(x, y)
        Constructs a unique key for each node based on its x and y coordinates
    connectHorizontally(data, xoffset, yoffset)
        Connect nodes horizontally based on the maze data
    connectVertically(data, xoffset, yoffset)
        Connect nodes vertically based on the maze data
    getStartTempNode()
        Get the starting node for the temporary pathfinding algorithm
    setPortalPair(pair1, pair2)
        Sets two nodes as portal pairs, allowing entities to teleport between them
    createHomeNodes(xoffset, yoffset)
        Constructs nodes for the "home" area (where ghosts start)
    connectHomeNodes(homekey, otherkey, direction)
        Connects the home nodes to the main maze
    getNodeFromPixels(xpixel, ypixel)
        Retrieve a node based on pixel coordinates
    getNodeFromTiles(col, row)
        Retrieves a node based on tile (row, col) coordinates
    denyAccess(col, row, direction, entity)
        Denies access for a specific entity in a given direction from a given tile
    allowAccess(col, row, direction, entity)
        Allows access for a specific entity in a given direction from a given tile
    denyAccessList(col, row, direction, entities)
        Denies access for a list of entities in a given direction from a given tile
    allowAccessList(col, row, direction, entities)
        Allows access for a list of entities in a given direction from a given tile
    denyHomeAccess(entity)
        Denies access for a specific entity to the home node
    allowHomeAccess(entity)
        Allows access for a specific entity to the home node
    denyHomeAccessList(entities)
        Denies access for a list of entities to the home node
    allowHomeAccessList(entities)
        Allows access for a list of entities to the home node
    render(screen)
        Renders all nodes and their connections on the provided screen (or surface)
    """

    def __init__(self, level: str) -> None:
        """
        Initializes the NodeGroup with a reference to a level (likely a maze file).

        Initializes a dictionary nodesLUT (Look-Up Table) to store all nodes.

        Reads the maze file and constructs the nodes and their connections.

        Parameters
        ----------
        level : str
            The name of the maze file
        """
        self.level = level
        self.nodesLUT = {}
        self.nodeSymbols = ["+", "P", "n"]
        self.pathSymbols = [".", "-", "|", "p"]
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)
        self.homekey = None

    def readMazeFile(self, textfile: str) -> np.ndarray:
        """
        Reads the maze layout from a file and returns it as a NumPy array.

        Parameters
        ----------
        textfile : str
            The name of the maze file

        Returns
        -------
        np.ndarray
            A NumPy array containing the maze layout
        """
        return np.loadtxt(textfile, dtype="<U1")

    def createNodeTable(
        self, data: np.ndarray, xoffset: int = 0, yoffset: int = 0
    ) -> None:
        """
        Constructs nodes based on the maze data.

        Parameters
        ----------
        data : np.ndarray
            A NumPy array containing the maze layout
        xoffset : int
            The x coordinate offset for the maze
        yoffset : int
            The y coordinate offset for the maze
        """
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col + xoffset, row + yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)

    def constructKey(self, x: int, y: int) -> tuple:
        """
        Constructs a unique key for each node based on its x and y coordinates.

        Parameters
        ----------
        x : int
            The x coordinate of the node
        y : int
            The y coordinate of the node

        Returns
        -------
        tuple
            A tuple containing the x and y coordinates of the node
        """
        return x * TILEWIDTH, y * TILEHEIGHT

    def connectHorizontally(
        self, data: np.ndarray, xoffset: int = 0, yoffset: int = 0
    ) -> None:
        """
        Connect nodes horizontally based on the maze data.

        Parameters
        ----------
        data : np.ndarray
            A NumPy array containing the maze layout
        xoffset : int
            The x coordinate offset for the maze
        yoffset : int
            The y coordinate offset for the maze
        """
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col + xoffset, row + yoffset)
                    else:
                        otherkey = self.constructKey(col + xoffset, row + yoffset)
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connectVertically(
        self, data: np.ndarray, xoffset: int = 0, yoffset: int = 0
    ) -> None:
        """
        Connect nodes vertically based on the maze data.

        Parameters
        ----------
        data : np.ndarray
            A NumPy array containing the maze layout
        xoffset : int
            The x coordinate offset for the maze
        yoffset : int
            The y coordinate offset for the maze
        """
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col + xoffset, row + yoffset)
                    else:
                        otherkey = self.constructKey(col + xoffset, row + yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    def getStartTempNode(self) -> Node:
        """
        Get the starting node for the temporary pathfinding algorithm.
        """
        nodes = list(self.nodesLUT.values())
        return nodes[0]

    def setPortalPair(self, pair1: tuple, pair2: tuple) -> None:
        """
        Sets two nodes as portal pairs, allowing entities to teleport between them.

        Parameters
        ----------
        pair1 : tuple
            The x and y coordinates of the first node
        pair2 : tuple
            The x and y coordinates of the second node
        """
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def createHomeNodes(self, xoffset: int, yoffset: int) -> tuple:
        """
        Constructs nodes for the "home" area (where ghosts start).

        Parameters
        ----------
        xoffset : int
            The x coordinate offset for the maze
        yoffset : int
            The y coordinate offset for the maze

        Returns
        -------
        tuple
            The x and y coordinates of the home node
        """
        homedata = np.array(
            [
                ["X", "X", "+", "X", "X"],
                ["X", "X", ".", "X", "X"],
                ["+", "X", ".", "X", "+"],
                ["+", ".", "+", ".", "+"],
                ["+", "X", "X", "X", "+"],
            ]
        )

        self.createNodeTable(homedata, xoffset, yoffset)
        self.connectHorizontally(homedata, xoffset, yoffset)
        self.connectVertically(homedata, xoffset, yoffset)
        self.homekey = self.constructKey(xoffset + 2, yoffset)
        return self.homekey

    def connectHomeNodes(self, homekey: tuple, otherkey: tuple, direction: int) -> None:
        """
        Connects the home nodes to the main maze.

        Parameters
        ----------
        homekey : tuple
            The x and y coordinates of the home node
        otherkey : tuple
            The x and y coordinates of the other node
        direction : int
            The direction to connect the nodes in
        """
        key = self.constructKey(*otherkey)
        self.nodesLUT[homekey].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction * -1] = self.nodesLUT[homekey]

    def getNodeFromPixels(self, xpixel: int, ypixel: int) -> Node:
        """
        Retrieve a node based on pixel coordinates

        Parameters
        ----------
        xpixel : int
            The x coordinate of the pixel
        ypixel : int
            The y coordinate of the pixel

        Returns
        -------
        Node
            The node at the given pixel coordinates
        """
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col: int, row: int) -> Node:
        """
        Retrieves a node based on tile (row, col) coordinates.

        Parameters
        ----------
        col : int
            The column of the tile
        row : int
            The row of the tile

        Returns
        -------
        Node
            The node at the given tile coordinates
        """
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None

    def denyAccess(self, col: int, row: int, direction: int, entity: 'Entity') -> None:
        """
        Denies access for a specific entity in a given direction from a given tile.

        Parameters
        ----------
        col : int
            The column of the tile
        row : int
            The row of the tile
        direction : int
            The direction to deny access in
        entity : 'Entity'
            The entity to deny access to
        """
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.denyAccess(direction, entity)

    def allowAccess(self, col: int, row: int, direction: int, entity: 'Entity') -> None:
        """
        Allows access for a specific entity in a given direction from a given tile.

        Used to allow ghosts to enter the home area.

        Parameters
        ----------
        col : int
            The column of the tile
        row : int
            The row of the tile
        direction : int
            The direction to allow access in
        entity : 'Entity'
            The entity to allow access to
        """
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.allowAccess(direction, entity)

    def denyAccessList(
        self, col: int, row: int, direction: int, entities: List['Entity']
    ) -> None:
        """
        Denies access for a list of entities in a given direction from a given tile.

        Parameters
        ----------
        col : int
            The column of the tile
        row : int
            The row of the tile
        direction : int
            The direction to deny access in
        entities : List[Entity]
            The list of entities to deny access to
        """
        for entity in entities:
            self.denyAccess(col, row, direction, entity)

    def allowAccessList(
        self, col: int, row: int, direction: int, entities: List['Entity']
    ) -> None:
        """
        Allows access for a list of entities in a given direction from a given tile.

        Parameters
        ----------
        col : int
            The column of the tile
        row : int
            The row of the tile
        direction : int
            The direction to allow access in
        entities : List[Entity]
            The list of entities to allow access to
        """
        for entity in entities:
            self.allowAccess(col, row, direction, entity)

    def denyHomeAccess(self, entity: 'Entity') -> None:
        """
        Denies access for a specific entity to the home node.

        Parameters
        ----------
        entity : 'Entity'
            The entity to deny access to
        """
        self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity: 'Entity') -> None:
        """
        Allows access for a specific entity to the home node.

        Parameters
        ----------
        entity : 'Entity'
            The entity to allow access to
        """
        self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities: List['Entity']) -> None:
        """
        Denies access for a list of entities to the home node.

        Parameters
        ----------
        entities : List[Entity]
            The list of entities to deny access to
        """
        for entity in entities:
            self.denyHomeAccess(entity)

    def allowHomeAccessList(self, entities: List['Entity']) -> None:
        """
        Allows access for a list of entities to the home node.

        Parameters
        ----------
        entities : List[Entity]
            The list of entities to allow access to
        """
        for entity in entities:
            self.allowHomeAccess(entity)

    def render(self, screen: pygame.Surface) -> None:
        """
        Renders all nodes and their connections on the provided screen (or surface).

        Parameters
        ----------
        screen : pygame.Surface
            The screen or surface to draw the nodes on
        """
        for node in self.nodesLUT.values():
            node.render(screen)
