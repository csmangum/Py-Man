from random import random
from typing import Union
import pygame
from pygame.locals import *
from vector import Vector2  #! Why is this not used?
from constants import *
from entity import Entity
from sprites import PacManSprites

from typing import TYPE_CHECKING

from game.pacman import PacMan

if TYPE_CHECKING:
    from game.nodes import Node
    from game.ghosts import Ghost


class PacManFSM(PacMan):
    def __init__(self):
        self.state = "Search"
        self.environment = None

    def update(self, game):
        """
        While in the seek pellets state, Ms Pac-Man moves randomly up until it
        detects a pellet and then follows a pathfinding algorithm to eat as many
        pellets as possible and as soon as possible.

        If a power pill is eaten, then Ms PacMan moves to the chase ghosts state
        in which it can use any tree-search algorithm to chase the blue ghosts.

        When the ghosts start flashing, Ms Pac-Man moves to the evade ghosts
        state in which it uses tree search to evade ghosts so that none is
        visible within a distance; when that happens Ms Pac-Man moves back to
        the seek pellets state.

        States
        -------
        """
        #! Add "Eat" state???
        #! Attack vs Chase
        dt = game.dt
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        self.update_state()
        self.action()

    def update_state(self) -> None:
        """
        Update the PacMan's state based on the current game environment.

        The PacMan's state is updated based on the following rules:
        1. If the PacMan is in the search state and a power pellet is nearby,
            then the PacMan moves to the chase state.
        2. If the PacMan is in the search state and a non-vulnerable ghost is
            nearby, then the PacMan moves to the evade state.
        3. If the PacMan is in the chase state and a power pellet is eaten and
            a vulnerable ghost is nearby, then the PacMan moves to the attack
            state.
        4. If the PacMan is in the chase state and a non-vulnerable ghost is
            nearby, then the PacMan moves to the evade state.
        5. If the PacMan is in the attack state and no vulnerable ghosts are
            nearby or a vulnerable ghost is eaten, then the PacMan moves to
            the search state.
        6. If the PacMan is in the evade state and no non-vulnerable ghosts are
            nearby, then the PacMan moves to the search state.
        7. If the PacMan is in the evade state and a power pellet is nearby, then
            the PacMan moves to the chase state.
        """

        if self.state == "Search":
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

    def search(self):
        """
        Get the next direction to move in the search state.

        If no pellets are nearby, then move randomly.
        If a pellet is nearby, then move towards it.
        """
        #! Just set the direction in this method
        next_direction = None

        if self.power_pellet_nearby():
            next_direction = self.move_towards_power_pellet()
        elif self.pellet_nearby():
            next_direction = self.move_towards_nearest_pellet()
        else:
            valid_directions = self.valid_directions()
            next_direction = random.choice(valid_directions)

        return next_direction

    def action(self):
        #! change method name to update_direction???
        if self.state == "Search":
            next_direction = self.search()
        elif self.state == "Chase":
            pass
        elif self.state == "Attack":
            pass
        elif self.state == "Evade":
            pass

    def pellet_nearby(self):
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
        pacman_x, pacman_y = self.position

    def power_pellet_nearby(self, pacman_position, game_board, threshold_distance=3):
        """
        Check if a power pellet is nearby Pac-Man.

        It is considered nearby if it is within a Manhattan distance of
        threshold_distance.

        Manhattan distance is the distance between two points measured along
        the path and not the straight line distance.

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
