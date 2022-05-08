from collections.abc import Generator

from page_sku import SKU
from structlog.stdlib import BoundLogger, get_logger

from page_parser.options import get_marketplace_parser


class Parser:
    """
    TODO
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

    def parse(
        self, text: str, url: str, marketplace: str
    ) -> Generator[list[SKU], tuple[str, str], None]:
        """TODO"""

        parser = get_marketplace_parser(marketplace=marketplace, logger=self._logger)
        return parser.parse(text=text, url=url)
