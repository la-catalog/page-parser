from page_parser.abstractions import Marketplace
from page_parser.marketplace_search.rihappy import Rihappy as SearchRihappy

search_options: dict[str, type[Marketplace]] = {
    "rihappy": SearchRihappy,
}
