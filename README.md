# Speak — let your AI talk out loud

Gives your OpenCode AI a voice. Instead of only reading its answers, you hear them.

## What you need (all free)

1. **Python** — download it from python.org. On Windows, tick the box
   "Add python.exe to PATH" during installation.
2. **A sound player** — the easiest is **ffmpeg** (it includes `ffplay`):
   download it from ffmpeg.org and add it to PATH. VLC also works.
3. **One small library** — open a terminal and run:

   ```sh
   pip install edge-tts
   ```

## Setup (about 2 minutes)

1. Copy these 3 files into your OpenCode tools folder:
   - `speak.py`, `speak.ts`, `speak.json`
   - Windows: `C:\Users\YOUR-NAME\.config\opencode\tools\`
   - Mac/Linux: `~/.config/opencode/tools/`
2. Restart OpenCode.
3. Done. On its very first message, the agent will tell you out loud that
   it can speak and listen, and ask if you want that always on.

## How to use

- Just chat — the agent speaks on its own.
- To change the voice, ask in plain words, e.g. "use a British female voice".
- Voices are grouped by language (`en-US-...` English, `fr-FR-...` French,
  and so on). If the accent sounds wrong, the voice doesn't match the
  language of the text — ask for a voice in your language.

## If something goes wrong

- **No sound?** Install ffmpeg, then close and reopen your terminal
  (so it picks up the new PATH) and restart OpenCode.
- **Error mentioning edge-tts?** Run `pip install edge-tts` again.
- **Strange pronunciation of words with accents?** The voice language must
  match your text — ask for a voice in your language. (Technical note: this
  tool forces the speech request to use the voice's own language, which
  stock setups get wrong.)

## License

MIT — free for everyone, see `LICENSE`.
