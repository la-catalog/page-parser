from collections.abc import Generator

from page_models import SKU, URL
from structlog.stdlib import BoundLogger


class Marketplace:
    """
    Base class for the marketplaces classes.
    """

    def __init__(self, marketplace: str, logger: BoundLogger) -> None:
        self._marketplace = marketplace
        self._logger = logger

    def parse(
        self,
        text: str,
        url: URL,
    ) -> Generator[SKU | URL, tuple[str, URL], None]:
        """
        Parse the text (HTML/JSON) to obtain informations from it.

        text - Content from the page
        url - URL from the content

        In case parsing one text isn't enough to obtain the complete information,
        it's possible to yield an URL so the caller can use `send()` to pass
        more content (with the respective URL).
        """

        return
