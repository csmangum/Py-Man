from random import random
from typing import Union
import pygame
from pygame.locals import *
from vector import Vector2  #! Why is this not used?
from constants import *
from entity import Entity
from sprites import PacManSprites

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.nodes import Node
    from game.ghosts import Ghost


class PacMan(Entity):
    """
    PacMan class

    PacMan is the main character of the game. He is controlled by the player
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
    sprites : PacManSprites
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

    def __init__(self, node: "Node") -> None:
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)  # PacMan starts between nodes 1 and 2
        self.alive = True
        self.sprites = PacManSprites(self)

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


class PacManFSM(PacMan):
    def __init__(self):
        self.state = "Search"
        self.environment = None

    def update(self, dt):
        """
        While in the seek pellets state, Ms Pac-Man moves randomly up until it 
        detects a pellet and then follows a pathfinding algorithm to eat as many  
        pellets as possible and as soon as possible. 
        
        If a power pill is eaten, then Ms PacMan moves to the chase ghosts state 
        in which it can use any tree-search algorithm  to chase the blue ghosts. 
        
        When the ghosts start flashing, Ms Pac-Man moves to the evade ghosts 
        state in which it uses tree search to evade ghosts so that none is 
        visible within a distance; when that happens Ms Pac-Man moves back to 
        the seek pellets state. 
        """
        
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        
        if self.state == "Search":
            locations = self.validDirections()
            random_location = random.choice(locations)
            if self.power_pellet_nearby():
                self.state = "Chase"
            elif self.non_vulnerable_ghost_nearby():
                self.state = "Evade"

        elif self.state == "Chase":
            if self.ate_power_pellet() and self.vulnerable_ghost_nearby():
                self.state = "Attack"
            elif self.non_vulnerable_ghost_nearby():
                self.state = "Evade"

        elif self.state == "Attack":
            if not self.vulnerable_ghost_nearby() or self.ate_vulnerable_ghost():
                self.state = "Search"

        elif self.state == "Evade":
            if not self.non_vulnerable_ghost_nearby():
                self.state = "Search"
            elif self.power_pellet_nearby():
                self.state = "Chase"
                
        self.action()

    def power_pellet_nearby(self):
        """
        Checks the direct up, down, left, and right cells for power pellets.
        
        Parameters
        ----------
        environment : dict
            The game environment
            
        Returns
        -------
        bool
            True if a power pellet is found, False otherwise
        """
        

    def power_pellet_nearby(self, pacman_position, game_board, threshold_distance=3):
        """
        Check if a power pellet is nearby Pac-Man.
    
        Parameters
        ----------
        pacman_position : tuple

        """
        pacman_x, pacman_y = pacman_position
    
        # Iterate over the game board
        for y in range(len(game_board)):
            for x in range(len(game_board[y])):
                # Check if the current cell contains a power pellet
                if game_board[y][x] == "POWER_PELLET":
                    # Calculate the Manhattan distance between Pac-Man and the power pellet
                    distance = abs(pacman_x - x) + abs(pacman_y - y)
                    if distance <= threshold_distance:
                        return True
    
        return False


    def non_vulnerable_ghost_nearby(self, environment):
        return False

    def vulnerable_ghost_nearby(self, environment):
        return False

    def ate_power_pellet(self, environment):
        return False

    def ate_vulnerable_ghost(self, environment):
        return False

    def action(self):
        if self.state == "Search":
            locations = self.validDirections()
            
        elif self.state == "Chase":
            return self.move_towards_power_pellet()
        elif self.state == "Attack":
            return self.move_towards_vulnerable_ghost()
        elif self.state == "Evade":
            return self.move_away_from_ghost()

    def move_towards_nearest_pellet(self, environment):
        # Search algo for nearest pellet in 4 directions (up, down, left, right)
        # stops when it hits a wall or a pellet, returns distance, shortest distance is chosen
        # get the N spaces in a provided direction
        return None

    def move_towards_power_pellet(self):
        return None

    def move_towards_vulnerable_ghost(self):
        return None

    def move_away_from_ghost(self):
        return None


class StateMachine:
    def __init__(self):
        self.state = 'Seek pellets'

    def update(self, conditions):
        
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.getValidKey()
        
        if self.state == 'Seek pellets':
            # Ms Pac-Man moves randomly until it detects a pellet 
            # and then uses a pathfinding algorithm to eat the pellets.
            # For simplicity, we will just print a statement here.
            
            if conditions['pellet_detected']:
                print("Pellet detected! Following pathfinding algorithm...")
            
            if conditions['ghost_in_sight']:
                self.state = 'Evade Ghosts'
            elif conditions['power_pill_eaten']:
                self.state = 'Chase Ghosts'
                
        elif self.state == 'Chase Ghosts':
            # Ms Pac-Man uses a tree-search algorithm to chase the blue ghosts.
            print("Using tree-search algorithm to chase blue ghosts...")
            if conditions['ghosts_flashing']:
                self.state = 'Evade Ghosts'
            elif not conditions['visible_ghost']:
                self.state = 'Seek pellets'

        elif self.state == 'Evade Ghosts':
            # Ms Pac-Man uses tree search to evade ghosts 
            # so that none is visible within a distance.
            print("Using tree search to evade ghosts...")
            if not conditions['ghost_in_sight']:
                self.state = 'Seek pellets'
                
        return self.state

# Example usage:

sm = StateMachine()

# Conditions are represented as a dictionary
conditions = {
    'ghost_in_sight': False,
    'power_pill_eaten': False,
    'ghosts_flashing': False,
    'visible_ghost': False,
    'pellet_detected': False
}

print(sm.update(conditions))  # Output: Seek pellets behavior and then the state

conditions['ghost_in_sight'] = True
print(sm.update(conditions))  # Output: Evade ghosts behavior and then the state

conditions['ghost_in_sight'] = False
conditions['pellet_detected'] = True
print(sm.update(conditions))  # Output: Seek pellets behavior (with pathfinding) and then the state

conditions['power_pill_eaten'] = True
print(sm.update(conditions))  # Output: Chase ghosts behavior and then the state
