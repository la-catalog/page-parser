from page_parser.abstractions import Marketplace
from page_parser.marketplace_sku.amazon import Amazon
from page_parser.marketplace_sku.amazon_pt import AmazonPT
from page_parser.marketplace_sku.mercado_livre_api import MercadoLivreAPI
from page_parser.marketplace_sku.rihappy import Rihappy

sku_options: dict[str, type[Marketplace]] = {
    "rihappy": Rihappy,
    "amazon": Amazon,
    "amazon_pt": AmazonPT,
    "mercado_livre_api": MercadoLivreAPI,
}
