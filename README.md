# Xcrap for Python

Xcrap é um framework originalmente feito para Node.js, mas, digamos que eu também sou um desenvolvedor Python e, estava um pouco entediado; por isso, resolvi fazer uma versão para Python.

Ainda está em fase experimental, e muito incompleto, só vou garantir o nome no PyPI, o resto, vou fazendo aos poucos. Talvez nos tornemos uma alternativa ao Scrapy, seria ambicioso demais da minha parte? Não sei, mas, vamos tentar, sou meio doido... (me contratem, Zyte :v)

## Como funciona (O que já temos)

A ideia é ser declarativo e fácil. Veja um exemplo de como você já pode usar o `xcrap` para extrair dados estruturados:

```python
from xcrap.extractor import HtmlExtractionModel, HtmlBaseField, HtmlNestedField, css
from xcrap.clients import HttpxClient
import asyncio

# 1. Defina seus modelos de forma declarativa
class AuthorModel(HtmlExtractionModel):
    name = HtmlBaseField(
        query = css("small.author::text")
    )
    link = HtmlBaseField(
        query = css("a::attr(href)")
    )

class QuoteModel(HtmlExtractionModel):
    text = HtmlBaseField(
        query = css("span.text::text")
    )
    # Modelos aninhados sem esforço!
    author = HtmlNestedField(
        model = AuthorModel
    ) 
    tags = HtmlBaseField(
        query = css("div.tags a.tag::text"),
        multiple = True
    )

class QuotesPageModel(HtmlExtractionModel):
    quotes = HtmlNestedField(
        query = css("div.quote"),
        model = QuoteModel,
        multiple = True
    )

async def main():
    client = HttpxClient()
    
    # 2. Busque a página (com suporte a retries, proxy, etc.)
    response = await client.fetch(url="http://quotes.toscrape.com")

    # 3. Transforme em um parser e extraia os dados
    parser = response.as_html_parser()
    data = parser.extract_model(QuotesPageModel)

    for quote in data["quotes"][:3]:
        print(f"Quote: {quote['text']}")
        print(f"Author: {quote['author']['name']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Saída:**

```
Fetching http://quotes.toscrape.com ...

Extracted Data:

Quote 1:
  Text: “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”
  Author: {'name': 'Albert Einstein', 'link': '/author/Albert-Einstein'}
  Tags: change, deep-thoughts, thinking, world

Quote 2:
  Text: “It is our choices, Harry, that show what we truly are, far more than our abilities.”
  Author: {'name': 'J.K. Rowling', 'link': '/author/J-K-Rowling'}
  Tags: abilities, choices

Quote 3:
  Text: “There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.”
  Author: {'name': 'Albert Einstein', 'link': '/author/Albert-Einstein'}
  Tags: inspirational, life, live, miracle, miracles

Full test passed successfully!
```

Eu não sou iniciante em web scraping, mas não posso dizer que sou um especialista também, não enfrentei muitos casos; então, peço que, se você souber de algo que eu não sei e puder me ajudar, que me ajude!

O objetivo do Xcrap é ser modular, fácil de plugar com outros clientes Http (e usar até mesmo navegadores via Selenium ou seja qual lá biblioteca existir par isso), tratar JSON, HTML, Markdown (podendo lidar bem com um documento que tenha inclusive os 3 formatos sem problemas) de forma declarativa.

Quero fazer um transformador de dados, mas, até o momento, não consegui fazer essa façanha nem no Node.js, que eu já tenho um ecossitema maior do Xcrap.

Também sou um tanto quanto leigo em testes, então, se puder me ajudar com isso, eu agradeço!

Enfim, estamos aceitando contribuições, precismos documentar tudo isso, e muito mais! :D
