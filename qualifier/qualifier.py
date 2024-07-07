import re
import warnings
from enum import StrEnum, auto
from typing import ClassVar

MAX_QUOTE_LENGTH = 50


class VariantMode(StrEnum):
    """Enum to represent the different modes a quote can be transformed into."""

    NORMAL = auto()
    UWU = auto()
    PIGLATIN = auto()

    @classmethod
    def get(cls, value: str | None) -> "VariantMode":
        """Return the VariantMode enum value for the given `value`. If not found, return NORMAL."""
        return getattr(VariantMode, value.upper(), VariantMode.NORMAL) if value else VariantMode.NORMAL


class DuplicateError(Exception):
    """Error raised when there is an attempt to add a duplicate entry to a database."""


class Quote:
    """Class to represent a quote. The quote can be transformed into different variants."""

    def __init__(self, quote: str, mode: VariantMode) -> None:
        """Initialize the quote with the given `quote` and `mode`."""
        if len(quote) > MAX_QUOTE_LENGTH:
            msg = "Quote is too long"
            raise ValueError(msg)
        self.quote = quote
        self.mode = mode
        self.transformed_quote = self._create_variant()

    def __str__(self) -> str:
        """Return the quote in the appropriate variant."""
        return self.transformed_quote

    def _create_variant(self) -> str:
        """Transform the quote to the appropriate variant indicated by `self.mode` and returns the result."""
        match self.mode:
            case VariantMode.UWU:
                return self.uwuify(self.quote)
            case VariantMode.PIGLATIN:
                return self.piglatinify(self.quote)
            case _:
                return self.quote

    def uwuify(self, text: str) -> str:
        """Transform the text to uwu variant."""
        old_text = text

        # Replace all L or R with W
        text = re.sub(r"[LR]", "W", text)
        text = re.sub(r"[lr]", "w", text)

        # Stuttering
        text = re.sub(r"\b([uU])", r"\1-\1", text)

        if text == old_text:
            msg = "Quote was not modified"
            raise ValueError(msg)

        # Check for length
        if len(text) > MAX_QUOTE_LENGTH:
            text = old_text
            text = re.sub(r"[LR]", "W", text)
            text = re.sub(r"[lr]", "w", text)
            warnings.warn("Quote too long, only partially transformed", stacklevel=2)

        return text

    def piglatinify(self, text: str) -> str:
        """Transform the text to piglatin variant."""
        words = text.split()

        for i, word in enumerate(words):
            match = re.match(r"[^aeiouAEIOU]+", word)

            if match:
                # Get the match indices
                start, end = match.span()
                pig_word = word[end:] + word[start:end] + "ay"
            else:
                pig_word = word + "way"

            words[i] = pig_word

        # Sentence case
        words[0] = words[0][0].upper() + words[0][1:].lower()
        text = " ".join(words)

        if len(text) > MAX_QUOTE_LENGTH:
            msg = "Quote was not modified"
            raise ValueError(msg)

        return text


def run_command(command: str) -> None:
    """Will be given a command from a user. The command will be parsed and executed appropriately.

    Current supported commands:
        - `quote` - creates and adds a new quote
        - `quote uwu` - uwu-ifys the new quote and then adds it
        - `quote piglatin` - piglatin-ifys the new quote and then adds it
        - `quote list` - print a formatted string that lists the current
           quotes to be displayed in discord flavored markdown
    """
    if match := re.fullmatch(r'quote (uwu|piglatin)? ?("|“)(.*?)("|”)', command):
        mode = VariantMode.get(match.group(1))
        quote = Quote(match.group(3), mode)
        try:
            Database.add_quote(quote)
        except DuplicateError:
            print("Quote has already been added previously")
    elif match := re.fullmatch(r"quote list", command):
        quotes = Database.get_quotes()
        print(f"- {'\n- '.join(quotes)}")
    else:
        msg = "Invalid command"
        raise ValueError(msg)


class Database:
    """Class to represent a database of quotes."""

    quotes: ClassVar[list[Quote]] = []

    @classmethod
    def get_quotes(cls) -> list[str]:
        """Return current quotes in a list."""
        return [str(quote) for quote in cls.quotes]

    @classmethod
    def add_quote(cls, quote: Quote) -> None:
        """Add a quote. Will raise a `DuplicateError` if an error occurs."""
        if str(quote) in [str(quote) for quote in cls.quotes]:
            raise DuplicateError
        cls.quotes.append(quote)
