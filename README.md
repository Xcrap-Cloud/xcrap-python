# Xcrap for Python

Xcrap é um framework originalmente feito para Node.js, mas, digamos que eu também sou um desenvolvedor Python e, estava um pouco entediado; por isso, resolvi fazer uma versão para Python.

Ainda está em fase experimental, mas já conta com funcionalidades poderosas portadas da versão original em TypeScript, garantindo paridade entre os ecossistemas.

## 🚀 Como funciona

A ideia é ser declarativo e fácil. Veja um exemplo de como você já pode usar o `xcrap` para extrair dados estruturados:

```python
from xcrap.extractor import HtmlExtractionModel, HtmlBaseField, HtmlNestedField, css
from xcrap.clients import HttpxClient
import asyncio

# 1. Defina seus modelos de forma declarativa
class AuthorModel(HtmlExtractionModel):
    name = HtmlBaseField(query=css("small.author::text"))
    link = HtmlBaseField(query=css("a::attr(href)"))

class QuoteModel(HtmlExtractionModel):
    text = HtmlBaseField(query=css("span.text::text"))
    # Modelos aninhados sem esforço!
    author = HtmlNestedField(model=AuthorModel) 
    tags = HtmlBaseField(query=css("div.tags a.tag::text"), multiple=True)

class QuotesPageModel(HtmlExtractionModel):
    quotes = HtmlNestedField(query=css("div.quote"), model=QuoteModel, multiple=True)

async def main():
    client = HttpxClient()
    
    # 2. Busque a página
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

## ✨ Funcionalidades Principais

### 🔒 Descriptografia Automática
Suporte integrado para descriptografar respostas HTTP (AES-CBC/ECB).

```python
from xcrap.core import decrypt_client
from xcrap.utils.decryption import DecryptConfig, DecryptKeyConfig

config = DecryptConfig(
    algorithm="aes-256-cbc",
    key=DecryptKeyConfig(value="sua-chave-aqui"),
    iv=DecryptKeyConfig(value="seu-iv-aqui")
)

@decrypt_client(config)
class MySecureClient(HttpxClient):
    pass

# Todas as respostas deste cliente agora virão descriptografadas!
```

### 🏭 Sistema de Factories
Crie modelos e clientes a partir de configurações JSON/Dicionários, ideal para sistemas dinâmicos.

```python
from xcrap.factory import create_parsing_model
from xcrap.extractor import HtmlExtractionModel

config = {
    "type": "html",
    "model": {
        "title": {"query": {"type": "css", "value": "h1::text"}}
    }
}

model = create_parsing_model(config, allowed_models={"html": HtmlExtractionModel})
data = model.extract("<h1>Hello!</h1>")
```

### 🛠️ Extratores Customizados
Você pode passar funções customizadas para processar campos individualmente:

```python
class MyModel(HtmlExtractionModel):
    # 'extractor' permite transformar o dado logo após a captura
    price = HtmlBaseField(
        query=css(".price::text"), 
        extractor=lambda text: float(text.replace("$", ""))
    )
```

### 📊 Extração de JSON (JMESPath)
Também suportamos extração de JSON usando JMESPath:

```python
from xcrap.extractor import JsonExtractionModel, JsonBaseField, jmes_path, JsonParser

class ProjectModel(JsonExtractionModel):
    name = JsonBaseField(query=jmes_path("title"))
    tags = JsonBaseField(query=jmes_path("tags"), multiple=True)

content = '{"title": "Xcrap", "tags": ["python", "scraping"]}'
parser = JsonParser(content)
data = parser.extract_model(ProjectModel) # {'name': 'Xcrap', 'tags': ['python', 'scraping']}
```

## 🛠️ Desenvolvimento

Para rodar os testes e verificar a cobertura:

```bash
poetry run pytest --cov=xcrap --cov-report=term-missing
```

Atualmente o projeto conta com **100% de cobertura de código**, garantindo a confiabilidade de todas as funcionalidades.

---
Feito com ❤️ por Marcuth <contact@marcuth.dev>
