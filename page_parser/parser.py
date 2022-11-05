from collections.abc import Generator

from page_models import SKU, URL
from structlog.stdlib import BoundLogger, get_logger

from page_parser.options.options import get_marketplace_parser
from page_parser.options.search_options import search_options
from page_parser.options.sku_options import sku_options


class Parser:
    """
    Parser is responsible for extracting informations from text (HTML/JSON).
    """

    def __init__(self, logger: BoundLogger = get_logger()) -> None:
        self._logger = logger

    def _log_error(
        self, text: str, url: URL, marketplace: str, exception: Exception
    ) -> None:
        self._logger.exception(
            event="Parser error",
            url=str(url),
            marketplace=marketplace,
        )

    def parse_sku(
        self, text: str, url: URL, marketplace: str
    ) -> Generator[SKU | URL, tuple[str, URL], None]:
        """Call the parse function from the respective marketplace"""

        parser = get_marketplace_parser(
            marketplace=marketplace, options=sku_options, logger=self._logger
        )

        return parser.parse(text=text, url=url)

    def parse_search(
        self, text: str, url: URL, marketplace: str
    ) -> Generator[SKU | URL, tuple[str, URL], None]:
        """Call the parse function from the respective marketplace"""

        parser = get_marketplace_parser(
            marketplace=marketplace, options=search_options, logger=self._logger
        )

        return parser.parse(text=text, url=url)
