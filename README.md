# page-parser
Use esse pacote para extrair informações de um texot (HTML/JSON).  

Não existe regra sobre o que usar para extrair as informações, então use a ferramenta que preferir (parsel/cssselect/beautifulsoup).  

# install
`pdm add page-parser`  

# usage

### page_parser.Parser.parse(text, url)
Deve se passar o texto que pode ser um HTML, JSON ou qualquer outra coisa desde que você assuma a responsabilidade de conseguir extrair dentro da configuração do seu marketplace. O URL também deve ser passado para conseguirmos montar links da página.  

```python
from pathlib import Path

from page_models import SKU
from pydantic import AnyHttpUrl

from page_parser.parser import Parser

parser = Parser()
html = Path("page.html").read_text()
url = "https://www.google.com/shopping/product/r/BR/16567145044483249038"
items = parser.parse(text=html, url=url)

for item in items:
    if isinstance(item, AnyHttpUrl):
        print(f"url: {item}")
    elif isinstance(item, SKU):
        print(f"sku: {SKU}")
```

Nem sempre um texto é o suficiente para extrair o que deseja da página, mas como usamos um *Generator* sempre é possível enviar mais texto com `send()`.  

```python
from pathlib import Path

from page_models import SKU
from pydantic import AnyHttpUrl

from page_parser.parser import Parser

parser = Parser()
html = Path("page.html").read_text()
html2 = Path("page2.html").read_text()
url = "https://www.google.com/shopping/product/r/BR/16567145044483249038"
url2 = "https://www.google.com/shopping/product/r/BR/16567145044483249038/specs?prds=rj:1,rsk:PC_11142543734639733720"
items = parser.parse(text=html, url=url)

for item in items:
    if isinstance(item, AnyHttpUrl):
        print(f"url: {item}")
    elif isinstance(item, SKU):
        print(f"sku: {SKU}")
    
    item = items.send(html2, url2)
    
    if isinstance(item, AnyHttpUrl):
        print(f"url: {item}")
    elif isinstance(item, SKU):
        print(f"sku: {SKU}")
```

# references
[Yield expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions)  
[Generator-iterator methods](https://docs.python.org/3/reference/expressions.html#generator-iterator-methods)  
