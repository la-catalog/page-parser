from collections.abc import Generator

from page_models import SKU
from pydantic import AnyHttpUrl
from structlog.stdlib import BoundLogger


class Marketplace:
    """
    Base class for the marketplaces classes.
    """

    def __init__(self, marketplace: str, logger: BoundLogger) -> None:
        self._marketplace = marketplace
        self._logger = logger

    def parse(
        self, text: str, url: AnyHttpUrl
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, AnyHttpUrl], None]:
        """
        Parse the text (HTML/JSON) to obtain informations from it.

        In case parsing one text isn't enough to obtain the complete information,
        it's possible to yield an URL and wait for this generators receive the `send()`.
        """

        return
