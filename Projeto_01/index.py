import requests

url = "http://localhost:11434/api/generate"

dados = {
    "model": "mistral",
    "prompt": "Explique o que é Python em 3 linhas.",
    "stream": False
}

resposta = requests.post(url, json=dados)

print(resposta.json()["response"])