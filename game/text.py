from abc import ABC
import pygame
from vector import Vector2
from constants import *


class Text(ABC):
    """
    This class provides a convenient way to display text elements within a game.

    It handles the rendering of the text, updating its state based on time,
    and managing its visibility and lifespan.

    Attributes
    ----------
    id : int
        The id of the text.
    text : str
        The text content.
    color : tuple
        The color of the text.
    size : int
        The size of the text.
    visible : bool
        The visibility of the text.
    position : Vector2
        The position of the text.
    timer : int
        The timer for the text.
    lifespan : int
        The lifespan of the text.
    label : pygame.Surface
        The rendered version of the text.
    destroy : bool
        The flag that indicates whether the text should be destroyed.
    font : pygame.font.Font
        The font used to render the text.

    Methods
    -------
    setupFont(fontpath: str) -> None
        Initializes the font for rendering the text using a specified font
        path and size.
    createLabel() -> None
        Renders the text content into a label using the specified font and color.
    setText(newtext: str) -> None
        Updates the text content and recreates the label.
    update(dt: float) -> None
        If the text object has a lifespan, this method updates a timer based on
        the time delta (dt).
    render(screen: pygame.Surface) -> None
        Renders the text label onto the provided screen (or surface) if the
        text object is visible.
    """

    def __init__(
        self,
        text: str,
        color: tuple,
        x: int,
        y: int,
        size: int,
        time: int = None,
        id: int = None,
        visible: bool = True,
    ) -> None:
        """
        Initializes the text object with various attributes like the text content,
        color, position (x, y), size, and optional attributes like time (lifespan),
        id, and visibility.

        The lifespan attribute indicates how long the text should be displayed
        before it's destroyed.

        The destroy attribute is a flag that indicates whether the text object
        should be destroyed (removed from the game).

        Sets up the font for rendering the text using the setupFont method.

        Creates a label (a rendered version of the text) using the
        createLabel method.

        Parameters
        ----------
        text : str
            The text content.
        color : tuple
            The color of the text.
        x : int
            The x position of the text.
        y : int
            The y position of the text.
        size : int
            The size of the text.
        time : int, optional
            The lifespan of the text. The default is None.
        id : int, optional
            The id of the text. The default is None.
        visible : bool, optional
            The visibility of the text. The default is True.
        """
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setupFont("game/assets/PressStart2P-Regular.ttf")
        self.createLabel()

    def setupFont(self, fontpath: str) -> None:
        """
        Initializes the font for rendering the text using a specified font
        path and size.

        Parameters
        ----------
        fontpath : str
            The path to the font file.
        """
        self.font = pygame.font.Font(fontpath, self.size)

    def createLabel(self) -> None:
        """
        Renders the text content into a label using the specified font and color.
        """
        self.label = self.font.render(self.text, 1, self.color)

    def setText(self, newtext: str) -> None:
        """
        Updates the text content and recreates the label.

        Parameters
        ----------
        newtext : str
            The new text content.
        """
        self.text = str(newtext)
        self.createLabel()

    def update(self, dt: float) -> None:
        """
        If the text object has a lifespan, this method updates a timer based on
        the time delta (dt).
        When the timer exceeds the lifespan, the text object is marked f
        or destruction.

        Parameters
        ----------
        dt : float
            The time delta.
        """
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen: pygame.Surface) -> None:
        """
        Renders the text label onto the provided screen (or surface) if the
        text object is visible.

        Parameters
        ----------
        screen : pygame.Surface
            The surface to render the text label onto.
        """
        if self.visible:
            x, y = self.position.asTuple()
            screen.blit(self.label, (x, y))


class TextGroup(ABC):
    """ """

    def __init__(self) -> None:
        """
        Initializes the next available ID for text elements.

        Initializes an empty dictionary alltext to store all the text elements.

        Sets up predefined text elements using the setupText method.

        Shows the "READY!" text by default.
        """
        self.nextid = 10
        self.alltext = {}
        self.setupText()
        self.showText(READYTXT)

    def addText(
        self,
        text: str,
        color: tuple,
        x: int,
        y: int,
        size: int,
        time: int = None,
        id: str = None,
    ) -> int:
        """
        Adds a new Text object to the alltext dictionary with a unique ID
        and returns the ID.

        Parameters
        ----------
        text : str
            The text content.
        color : tuple
            The color of the text.
        x : int
            The x position of the text.
        y : int
            The y position of the text.
        size : int
            The size of the text.
        time : int, optional
            The lifespan of the text. The default is None.
        id : int, optional
            The id of the text. The default is None.

        Returns
        -------
        int
            The id of the text.
        """
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time=time, id=id)
        return self.nextid

    def removeText(self, id):
        self.alltext.pop(id)

    def setupText(self):
        size = TILEHEIGHT
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.alltext[LEVELTXT] = Text(
            str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, size
        )
        self.alltext[READYTXT] = Text(
            "READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False
        )
        self.alltext[PAUSETXT] = Text(
            "PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False
        )
        self.alltext[GAMEOVERTXT] = Text(
            "GAMEOVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False
        )
        self.addText("SCORE", WHITE, 0, 0, size)
        self.addText("LEVEL", WHITE, 23 * TILEWIDTH, 0, size)

    def update(self, dt):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)

    def showText(self, id):
        self.hideText()
        self.alltext[id].visible = True

    def hideText(self):
        self.alltext[READYTXT].visible = False
        self.alltext[PAUSETXT].visible = False
        self.alltext[GAMEOVERTXT].visible = False

    def updateScore(self, score):
        self.updateText(SCORETXT, str(score).zfill(8))

    def updateLevel(self, level):
        self.updateText(LEVELTXT, str(level + 1).zfill(3))

    def updateText(self, id, value):
        if id in self.alltext.keys():
            self.alltext[id].setText(value)

    def render(self, screen):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)
