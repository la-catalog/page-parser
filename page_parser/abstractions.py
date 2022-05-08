from collections.abc import Generator

from page_sku import SKU


class Marketplace:
    """
    Base class for the marketplaces classes.
    """

    def __init__(self, logger) -> None:
        self._logger = logger

    def parse(self, text: str, url: str) -> Generator[list[SKU], tuple[str, str], None]:
        """
        Parse the text to obtain all information from it.
        When parsing more than one text is needed,
        you can use coroutine `send()` to pass more texts.
        """

        _ = yield None
