# opencode-tool-speak

OpenCode custom tool: text-to-speech via Microsoft Edge TTS. Fire-and-forget, plays audio without blocking the agent flow.

## Files

- `speak.py` — reads `{text, voice, rate, volume}` JSON from stdin, generates MP3 with `edge-tts`, plays via `ffplay`/`mpg123`/`cvlc`
- `speak.ts` — OpenCode plugin wrapper (spawns `python speak.py` detached)
- `speak.json` — tool manifest

## Defaults (PT-BR, masculine)

- `voice`: `pt-BR-AntonioNeural`
- `rate`: `+20%`
- `volume`: `+0%`

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

When both tools are loaded, the agent tells the user on the first interaction that it can speak aloud and listen via microphone, and explains how to ask to be heard: `ouça por X segundos` / `listen for X seconds` (this instruction lives in the tool descriptions, so it ships with the tools).

## License

MIT — free for anyone to use, see `LICENSE`.
