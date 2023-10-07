class Pause:
    """
    This class provides a structured way to handle pausing in a game.

    It allows for easy pausing and unpausing, setting a specific pause duration,
    and executing a callback function after the pause duration is over.

    Attributes
    ----------
    paused : bool
        Whether the game is paused or not
    timer : float
        Elapsed time since the game was paused
    pauseTime : float
        Duration for which the game should be paused
    func : function
        Callback function to be executed after the pause duration is over

    Methods
    -------
    update(dt)
        Increments the timer by the time delta (dt). If the timer exceeds or
        equals the pause duration, it resets the timer, unpauses the game, and
        returns the callback function (func). This allows the game to execute a
        specific action after the pause duration is over. If the pause duration
        is not reached or not set, it returns None.
    setPause(playerPaused, pauseTime, func)
        Sets the pause state with the provided arguments.
    flip()
        Toggles the pause state (paused attribute).
    """

    def __init__(self, paused: bool = False) -> None:
        """
        Initializes the pause state (paused attribute) based on the provided
        argument (default is False).

        Initializes a timer (timer attribute) to track the elapsed time since
        the game was paused.

        Initializes pauseTime to store the duration for which the game should
        be paused.

        Initializes func to store a callback function that can be executed after
        the pause duration is over.

        Parameters
        ----------
        paused : bool, optional
            Whether the game is paused or not, by default False
        """
        self.paused = paused
        self.timer = 0
        self.pauseTime = None
        self.func = None

    def update(self, dt: float) -> None:
        """
        If a pause duration (pauseTime) is set, this method increments the timer
        by the time delta (dt).

        If the timer exceeds or equals the pause duration, it resets the timer,
        unpauses the game, and returns the callback function (func). This allows
        the game to execute a specific action after the pause duration is over.

        If the pause duration is not reached or not set, it returns None.

        Parameters
        ----------
        dt : float
            Time delta
        """
        if self.pauseTime is not None:
            self.timer += dt
            if self.timer >= self.pauseTime:
                self.timer = 0
                self.paused = False
                self.pauseTime = None
                return self.func
        return None

    def setPause(self, playerPaused: bool = False, pauseTime=None, func=None) -> None:
        """
        Sets the pause state with the provided arguments.

        Parameters
        ----------
        playerPaused : bool, optional
            Whether the game was paused by the player, by default False
        pauseTime : float, optional
            Duration for which the game should be paused, by default None
        func : function, optional
            Callback function to be executed after the pause duration is over,
            by default None
        """
        self.timer = 0
        self.func = func
        self.pauseTime = pauseTime
        self.flip()

    def flip(self) -> None:
        """
        Toggles the pause state (paused attribute).
        """
        self.paused = not self.paused
