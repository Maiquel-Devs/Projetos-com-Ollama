import requests
import json
import speech_recognition as sr
import pyttsx3
import sys

# ── Funções principais ───────────────────────────────────────────────────────

def falar(texto):
    """Converte texto em voz — reinicia o engine a cada chamada para evitar travamento no Windows."""
    print(f"\n🤖 Assistant: {texto}\n")
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")
    for voice in voices:
        if "en" in voice.languages or "english" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    engine.say(texto)
    engine.runAndWait()
    engine.stop()


def ouvir():
    """Capta o microfone e retorna o texto transcrito."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️  Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            return None

    try:
        texto = recognizer.recognize_google(audio, language="en-US")
        print(f"🗣️  You said: {texto}")
        return texto
    except sr.UnknownValueError:
        print("❌ Could not understand. Try again.")
        return None
    except sr.RequestError:
        print("❌ Speech recognition service unavailable.")
        return None


def perguntar_mistral(historico):
    """Envia o histórico de conversa ao Mistral e retorna a resposta."""
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": "mistral",
        "messages": historico,
        "stream": True
    }

    try:
        resposta = requests.post(url, json=payload, stream=True, timeout=60)
        resposta_completa = ""

        print("🤖 Assistant: ", end="", flush=True)
        for linha in resposta.iter_lines():
            if linha:
                chunk = json.loads(linha)
                parte = chunk.get("message", {}).get("content", "")
                print(parte, end="", flush=True)
                resposta_completa += parte
                if chunk.get("done"):
                    break

        print()
        return resposta_completa

    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to Ollama. Make sure it is running.")
        sys.exit(1)


# ── Loop principal ───────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  🇺🇸  English Practice — Powered by Mistral (Local)")
    print("=" * 55)
    print("Speak in English and practice your conversation!")
    print("Say 'quit' or 'exit' to stop.\n")

    system_prompt = (
        "You are a friendly English conversation teacher. "
        "Your job is to help the user practice spoken English. "
        "Always respond in English. "
        "Keep responses short and natural (2-4 sentences). "
        "If the user makes a grammar mistake, gently correct it at the end of your reply. "
        "Encourage the user and keep the conversation going by asking a follow-up question."
    )

    historico = [
        {"role": "system", "content": system_prompt}
    ]

    boas_vindas = "Hello! I'm your English practice assistant. What would you like to talk about today?"
    falar(boas_vindas)
    historico.append({"role": "assistant", "content": boas_vindas})

    while True:
        texto_usuario = ouvir()

        if texto_usuario is None:
            continue

        if any(palavra in texto_usuario.lower() for palavra in ["quit", "exit", "bye", "goodbye"]):
            despedida = "Goodbye! Great practice today. Keep it up!"
            falar(despedida)
            break

        historico.append({"role": "user", "content": texto_usuario})

        resposta = perguntar_mistral(historico)

        if resposta:
            historico.append({"role": "assistant", "content": resposta})
            falar(resposta)


if __name__ == "__main__":
    main()