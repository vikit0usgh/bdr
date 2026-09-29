# Python API Client - Tkinter

Cliente HTTP inspirado em Postman/Bruno, construído com Tkinter.

## Funcionalidades

- Múltiplas abas
- GET, POST, PUT, PATCH e DELETE
- URL, Headers e Body
- Response com status e tempo
- Pretty print de JSON
- Collections
- Salvar/Abrir Collection
- Variáveis de Collection
- Variáveis extraídas da Response
- Substituição de `{{variavel}}` em URL, Headers e Body
- JSON Path simples para extração, como:
  - `$.token`
  - `$.user.id`
  - `$.data.access_token`

## Exemplo

A request de login pode retornar:

```json
{
    "token": "abc123",
    "user": {
        "id": 123
    }
}
```

Na aba de extração, configure:

```text
Nome       JSON Path
token      $.token
user_id    $.user.id
```

Depois, em outra request:

```text
Authorization: Bearer {{token}}
```

ou:

```text
https://api.exemplo.com/users/{{user_id}}
```

Ao enviar, as variáveis serão resolvidas automaticamente.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Teste rápido

Abra:

```text
examples/example_collection.json
```

A Collection contém um fluxo:

```text
1. Login
   ↓
   extrai token da response
   ↓
2. Get User
   ↓
   usa {{token}}
```

> O exemplo usa `httpbin.org`. Dependendo da disponibilidade do serviço, a resposta pode variar. O importante para testar a funcionalidade é observar a aba "Extract" e o uso de `{{token}}`.

## Estrutura

```text
api_client/
├── main.py
├── requirements.txt
├── README.md
├── examples/
│   └── example_collection.json
├── models/
│   ├── __init__.py
│   ├── request.py
│   ├── collection.py
│   └── environment.py
├── services/
│   ├── __init__.py
│   ├── http_client.py
│   ├── collection_service.py
│   └── variable_service.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── request_tab.py
│   ├── collection_panel.py
│   └── environment_panel.py
└── utils/
    ├── __init__.py
    └── json_utils.py
```


## Importação de cURL

O campo de URL também aceita um comando cURL completo.

Exemplo:

```bash
curl 'https://api.exemplo.com/users/123' \
  -X POST \
  -H 'Authorization: Bearer abc123' \
  -H 'Content-Type: application/json' \
  --data-raw '{"name":"Victor","active":true}'
```

Você pode:

1. Colar o comando no campo de URL.
2. Clicar em **Importar cURL**.

O sistema preencherá:

```text
Method: POST

URL:
https://api.exemplo.com/users/123

Headers:
Authorization: Bearer abc123
Content-Type: application/json

Body:
{
    "name": "Victor",
    "active": true
}
```

Também é possível simplesmente clicar em **Enviar** com o cURL colado: o sistema detecta o comando, importa os campos e não tenta enviar o texto do cURL como URL.

### cURL + variáveis

A importação preserva variáveis da Collection.

Exemplo:

```bash
curl '{{base_url}}/users/{{user_id}}' \
  -H 'Authorization: Bearer {{token}}'
```

As variáveis continuam disponíveis para o `VariableService` resolver antes do envio.


## Atalhos

- `Ctrl+A`: seleciona todo o conteúdo do campo atual.
- `Ctrl+V`: cola normalmente.
- `Ctrl+V` no campo de URL: se o conteúdo colado for um cURL, a importação acontece automaticamente.
- `Enter` no campo de URL: importa o cURL se o conteúdo começar com `curl`.
- `Command+A` / `Command+V`: equivalentes para macOS.

## cURL adicional

O parser também reconhece:

```bash
# Form
curl "https://httpbin.org/anything" -X POST \
  -F "name=Victor" \
  -F "active=true"

# Cookie + query
curl "https://httpbin.org/anything?page=2&limit=10" \
  -b "session=abc123"

# URL encode
curl "https://httpbin.org/anything" \
  --data-urlencode "query=Victor Silva" \
  --data-urlencode "page=1"
```

`-F/--form` é preservado para edição. O envio multipart com arquivos será uma etapa específica do `HttpClient`.


## Tempo de execução em tempo real

Ao clicar em **Enviar**, a interface passa a mostrar o tempo decorrido:

```text
Status: Enviando...
Time: 0.00 s
```

Enquanto a API estiver respondendo:

```text
0.05 s
0.10 s
0.15 s
...
1.00 s
1.05 s
...
```

A interface continua responsiva durante a requisição porque o HTTP é executado em uma thread separada.

Quando a resposta chega, o cronômetro para e mostra o tempo final medido pela requisição.

O botão **Enviar** fica desabilitado durante a execução para evitar o disparo acidental de várias requisições simultâneas na mesma aba.

## Importação de cURL

A importação de cURL não exibe mais uma janela de alerta. O comando é convertido silenciosamente para os campos da request.
