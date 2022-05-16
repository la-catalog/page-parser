from structlog.stdlib import BoundLogger

from page_parser.abstractions import Marketplace
from page_parser.exceptions import UnknowMarketplaceError
from page_parser.marketplaces.amazon import Amazon
from page_parser.marketplaces.amazon_pt import AmazonPT
from page_parser.marketplaces.rihappy import Rihappy

options: dict[str, type[Marketplace]] = {
    "rihappy": Rihappy,
    "amazon": Amazon,
    "amazon_pt": AmazonPT,
}


def get_marketplace_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    try:
        new_logger = logger.bind(marketplace=marketplace)
        marketplace_class = options[marketplace]
        return marketplace_class(marketplace=marketplace, logger=new_logger)
    except KeyError as e:
        raise UnknowMarketplaceError(
            f"Marketplace '{marketplace}' is not defined in page_parser package"
        ) from e
