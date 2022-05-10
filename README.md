# page-parser
Use esse pacote para extrair informações de um tet (HTML/JSON).  

Não existe regra sobre o que usar para extrair as informações, então use a ferramenta que preferir (parsel/cssselect/beautifulsoup).  

# install
`pip install git+https://github.com/thiagola92/page-parser.git`  

# usage

### page_parser.Parser.parse(text, url)
Deve se passar o texto que pode ser um HTML, JSON ou qualquer outra coisa desde que você assuma a responsabilidade de conseguir extrair dentro da configuração do seu marketplace. O URL também deve ser passado para conseguirmos montar links da página.  

```python
from pathlib import Path

from page_sku import SKU
from pydantic import AnyHttpUrl

from page_parser.parser import Parser

parser = Parser()
html = Path("page.html").read_text()
url = "https://www.google.com/shopping/product/r/BR/16567145044483249038"
items = parser.parse(text=html, url=url)

for item in  items:
    if isinstance(item, AnyHttpUrl):
        print(f"url: {item}")
    elif isinstance(item, SKU):
        print(f"sku: {SKU}")
```