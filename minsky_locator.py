"""Minsky's Turing locator solution implemented with the state pattern.

We have six states (L1, L2, R1, R2, R3, R4) and six symbols (X, Y, A, B,
0, 1)."""


class Locator:
    """A parser for finding target--location pairs that match in an
    input string for a possible copy of its contents by a Turing copier.

    The init arg for this locator is a string required to be in the
    format "Y<target>X<location 1><content 1>X<location 2><content 2>X
    ...Y", where the lengths of the target and location bits must match.
    Y denotes the start and end delimeters, while X separates target--
    location and location--location pairs.

    Example: "Y101X101111" is a valid input; while "Y", "YY", "Y11X1",
    "Y11X11", "YX11", and "YX11Y" aren't. And the result of calling the
    start() method on this locator for the previous valid input returns
    ("Y101XBAB111", "Copy").
    """

    def __init__(self, parse_string: str) -> None:
        try:
            parse_string = self._validate_string(parse_string)
        except AssertionError as exc:
            print("Invalid input:", str(exc))
            raise
        self.parse_string = parse_string
        self.pointer = parse_string.index("X")

    def _validate_string(self, parse_string) -> list[str]:
        assert parse_string[0] == parse_string[-1] == "Y", "Improper delimiters"
        units = parse_string.split("X")
        target = units[0].strip("Y")
        assert (len(units) > 1) and target, "No target--location pair"
        assert 0 < len(target) < len(units[1]), "Target--location lengths don't match."

        return list(parse_string)

    def process(self) -> Tuple[str, str]:
        """
        Process the parse string and return a tuple of the processed
        string and the last write.
        """

        write = None
        while write not in {"Halt", "Copy"}:
            write = self.curr_state.process(self)
        return ("".join(self.parse_string), write)

    def start(self) -> list[str]:
        """
        Start off the parser in the right state and return the
        result of processing.
        """
        self.curr_state = L1
        return self.process()


class State:
    """Base class representing both left and right states."""

    def shift(self, context: Locator) -> None:
        """Move the locator's pointer left or right depending on the
        current state."""
        # Intentional coupling of state logic due to only two states.
        if self.__class__.__name__.startswith("L"):
            shift = context.pointer - 1
            context.pointer = (shift >= 0 and shift) or 0
        elif self.__class__.__name__.startswith("R"):
            shift = context.pointer + 1
            str_length = len(context.parse_string)
            context.pointer = (shift < str_length and shift) or (str_length - 1)

    def read(self, context: Locator) -> str:
        """Shift the pointer, then read the current input."""
        config = self.__class__.read_write_next()
        read = None
        while not read in config:
            self.shift(context)
            read = context.parse_string[context.pointer]
        return read

    def process(self, context: Locator) -> str:
        """
        Respond to the result of reading the current pointer's input.
        """
        read = self.read(context)
        config = self.__class__.read_write_next()
        write, next_ = config[read]
        if write is not None and write not in {"Copy", "Halt"}:
            context.parse_string[context.pointer] = write
        if next_ is None:
            context.curr_state = self
        else:
            context.curr_state = next_
        return write


class Left1(State):
    """Left state. Start branch. Num|delim read, alpha|None write."""

    # We use a dictionary to represent state transition rules for this
    # state. Convention:{Read: (write, next).} (The quintuples of the
    # locator can be summarized by a dictionary mapping each state to
    # its read_write_next dictionary.)
    #
    # We use a lambda here to to avoid exceptions from unquoted
    # future class references.

    read_write_next = lambda: {"0": ("A", None), "1": ("B", None), "Y": (None, R1)}


class Left2(State):
    """Left Y read, None write."""

    read_write_next = lambda: {"Y": (None, R1)}


class Right1(State):
    """Right state. Copy branch. Alpha|delimiter read, Num|Copy write."""

    read_write_next = lambda: {"A": ("0", R2), "B": ("1", R3), "X": ("Copy", "Copy")}


class Right2(State):
    """Right state. Num read, alpha write."""

    read_write_next = lambda: {"0": ("A", L2), "1": ("B", R4)}


class Right3(State):
    """Right state. Num read, alpha write."""

    read_write_next = lambda: {"0": ("A", R4), "1": ("B", L2)}


class Right4(State):
    """Right state. Halt branch. Delimiter read, None|Halt write."""

    read_write_next = lambda: {"X": (None, L1), "Y": ("Halt", "Halt")}


L1 = Left1()
L2 = Left2()
R1 = Right1()
R2 = Right2()
R3 = Right3()
R4 = Right4()
