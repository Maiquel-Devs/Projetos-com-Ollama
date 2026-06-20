import requests
import json

url = "http://localhost:11434/api/generate"

dados = {
    "model": "mistral",
    "prompt": "Explique o que é Python em 3 linhas.",
    "stream": True
}

resposta = requests.post(url, json=dados, stream=True)

for linha in resposta.iter_lines():
    if linha:
        chunk = json.loads(linha)
        print(chunk["response"], end="", flush=True)

print()