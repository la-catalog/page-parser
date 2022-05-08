from structlog.stdlib import BoundLogger

from page_parser.abstractions import Marketplace
from page_parser.exceptions import UnknowMarketplaceError
from page_parser.marketplaces.rihappy import Rihappy

options: dict[Marketplace] = {
    "rihappy": Rihappy,
}


def get_marketplace_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    try:
        log = logger.bind(marketplace=marketplace)
        return options[marketplace](log)
    except KeyError as e:
        raise UnknowMarketplaceError(
            f"Marketplace '{marketplace}' is not defined in page_parser package"
        ) from e
