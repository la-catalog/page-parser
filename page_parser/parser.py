from collections.abc import Generator

from page_models import SKU
from pydantic import AnyHttpUrl
from structlog.stdlib import BoundLogger, get_logger

from page_parser.options.options import get_sku_parser


class Parser:
    """
    Parser is responsible for extracting informations from text (HTML/JSON).
    """

    def __init__(self, logger: BoundLogger = get_logger()) -> None:
        self._logger = logger

    def _log_error(
        self, text: str, url: str, marketplace: str, exception: Exception
    ) -> None:
        self._logger.exception(
            event="Parser error",
            url=url,
            marketplace=marketplace,
        )

    def parse_sku(
        self, text: str, url: str, marketplace: str
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, str], None]:
        """Call the parse function from the respective marketplace"""

        parser = get_sku_parser(marketplace=marketplace, logger=self._logger)

        return parser.parse(text=text, url=url)
