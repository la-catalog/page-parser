from structlog.stdlib import BoundLogger

from page_parser.abstractions import Marketplace
from page_parser.marketplace_sku.amazon import Amazon


class AmazonPT(Amazon):
    def __init__(self, marketplace: str, logger: BoundLogger) -> None:
        super().__init__(marketplace, logger)

        self._locale = "pt_PT"

        # TODO: create a package to build urls to marketplaces
        self._base_url = "https://www.amazon.es/-/pt/dp/{0}"
