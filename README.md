# opencode-tool-speak

OpenCode custom tool: text-to-speech via Microsoft Edge TTS. Fire-and-forget, plays audio without blocking the agent flow.

## Files

- `speak.py` — reads `{text, voice, rate, volume}` JSON from stdin, generates MP3 with `edge-tts`, plays via `ffplay`/`mpg123`/`cvlc`
- `speak.ts` — OpenCode plugin wrapper (spawns `python speak.py` detached)
- `speak.json` — tool manifest

## Defaults (English, masculine)

- `voice`: `en-US-AndrewNeural`
- `rate`: `+20%`
- `volume`: `+0%`

> Personal note: the author's own setup overrides the default to
> `pt-BR-AntonioNeural` (Brazilian Portuguese, masculine). The `xml:lang` fix
> derives the language from whatever voice you pass, so any locale works.

## Why the patch matters (accents fix)

Upstream `edge-tts` `mkssml()` hardcodes `xml:lang='en-US'` even for `pt-BR` voices, so `coração, avião, maçã, você, lâmpada` came out wrong (extra syllables mid-word). This repo's `speak.py` monkey-patches `mkssml` to derive `xml:lang` from the voice locale via regex `([a-z]{2,3}-[A-Z]{2})`, and forces UTF-8 on stdin/stdout (Windows PowerShell 5.1 defaults to cp1252/cp437 and mangles `ã,ç,é`).

Note: `edge-tts` `TTSConfig` expands `pt-BR-AntonioNeural` to the long form `Microsoft Server Speech Text to Speech Voice (pt-BR, AntonioNeural)` — the regex handles both forms.

## Requirements

- Python 3.12+, `pip install edge-tts`
- One audio player: `ffplay` (ffmpeg), `mpg123`, or `cvlc`

## Usage

```json
{ "text": "Olá, tudo bem?", "voice": "pt-BR-AntonioNeural" }
```

```sh
echo '{"text":"Teste de acentos: coração, avião, maçã, você, lâmpada."}' | python speak.py
```

Other PT-BR voices: `pt-BR-FranciscaNeural`; Portugal: `pt-PT-DuarteNeural`, `pt-PT-RaquelNeural`.

## First interaction

When both tools are loaded, the agent on the very first interaction speaks aloud (via speak) that it can talk and listen, explains how to ask to be heard: `ouça por X segundos` / `listen for X seconds`, and asks if the user wants always-speak-and-listen as the default for every interaction (this instruction lives in the tool descriptions, so it ships with the tools).

Suggested announcement (English, match voice locale to text language — never read English with a `pt-BR` voice):

> Hi! I can now speak to you out loud and listen through your microphone. To have me listen, just say: listen for ten seconds, or any number of seconds. Do you want me to always speak and listen by default in all our chats?

Portuguese variant (with `pt-BR-AntonioNeural`):

> Olá! Agora eu posso falar com você e também ouvir pelo microfone. Para me pedir para ouvir, é só dizer: ouça por dez segundos, ou qualquer número de segundos que quiser. Quer que eu sempre fale e escute como padrão em todas as nossas conversas?

## License

MIT — free for anyone to use, see `LICENSE`.
