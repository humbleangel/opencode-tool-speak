#!/usr/bin/env python3
"""
Text-to-Speech tool using Microsoft Edge TTS.

This script reads JSON input from stdin, converts text to speech using edge-tts,
plays the audio using system audio players, and outputs JSON status to stdout.

Input format (JSON):
    {
        "text": "Hello world",           # Required - text to speak
        "voice": "en-US-AriaNeural",    # Optional - voice to use
        "rate": "+0%",                   # Optional - speech rate
        "volume": "+0%"                  # Optional - speech volume
    }

Output format (JSON):
    {
        "success": true/false,
        "message": "Status message"
    }
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Optional

import edge_tts
import edge_tts.communicate as _comm


def _mkssml_fixed(tc, escaped_text):
    """Fix: edge-tts hardcodes xml:lang en-US -> use the voice's locale instead."""
    import re

    if isinstance(escaped_text, bytes):
        escaped_text = escaped_text.decode("utf-8")
    # tc.voice can be short (en-US-AndrewNeural) or long
    # (Microsoft Server Speech ... (en-US, AndrewNeural))
    m = re.search(r"([a-z]{2,3}-[A-Z]{2})", tc.voice)
    locale = m.group(1) if m else "en-US"
    return (
        f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{locale}'>"
        f"<voice name='{tc.voice}'>"
        f"<prosody pitch='{tc.pitch}' rate='{tc.rate}' volume='{tc.volume}'>"
        f"{escaped_text}"
        "</prosody>"
        "</voice>"
        "</speak>"
    )


_comm.mkssml = _mkssml_fixed


# Default values
DEFAULT_VOICE = "en-US-AndrewNeural"
DEFAULT_RATE = "+20%"
DEFAULT_VOLUME = "+0%"

# Audio players to try, in order of preference
AUDIO_PLAYERS = ["ffplay", "mpg123", "cvlc"]


async def generate_speech(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    volume: str = DEFAULT_VOLUME,
    output_file: Optional[str] = None,
) -> str:
    """
    Generate speech audio file from text using edge-tts.

    Args:
        text: The text to convert to speech
        voice: The voice to use (default: en-US-AriaNeural)
        rate: The speech rate (default: +0%)
        volume: The speech volume (default: +0%)
        output_file: Optional output file path (created if not provided)

    Returns:
        Path to the generated audio file

    Raises:
        Exception: If speech generation fails
    """
    # Create output file if not specified
    if output_file is None:
        fd, output_file = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

    # Create communicate object with specified parameters
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)

    # Save audio to file
    await communicate.save(output_file)

    return output_file


def find_available_player() -> Optional[str]:
    """
    Find the first available audio player from the preference list.

    Returns:
        Path to the available player executable, or None if no player found
    """
    for player in AUDIO_PLAYERS:
        if shutil.which(player):
            return player
    return None


def _run_hidden(cmd: list) -> bool:
    """Run cmd without a visible console window (Windows: no black popup)."""
    try:
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        }
        if os.name == "nt":
            # ponytail: CREATE_NO_WINDOW hides console, upgrade to per-player flags if one misbehaves
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = si
        return subprocess.run(cmd, **kwargs).returncode == 0
    except Exception:
        return False


def play_audio(file_path: str, player: str) -> bool:
    """
    Play an audio file using the specified player.

    Args:
        file_path: Path to the audio file
        player: The audio player executable name

    Returns:
        True if playback succeeded, False otherwise
    """
    try:
        if player == "mpg123":
            return _run_hidden(["mpg123", "-q", file_path])
        elif player == "ffplay":
            # ffplay with no window and auto-exit
            return _run_hidden(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path]
            )
        elif player == "cvlc":
            # cvlc (console vlc) with no GUI
            return _run_hidden(["cvlc", "--play-and-exit", "--quiet", file_path])
        elif player == "paplay":
            # paplay for PulseAudio
            return _run_hidden(["paplay", file_path])
        elif player == "aplay":
            # aplay for ALSA
            return _run_hidden(["aplay", "-q", file_path])
        else:
            return False
    except Exception:
        return False


def cleanup_file(file_path: str) -> None:
    """
    Safely remove a temporary file.

    Args:
        file_path: Path to the file to remove
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass  # Ignore cleanup errors


def main() -> int:
    """
    Main entry point for the TTS tool.

    Returns:
        0 on success, 1 on failure
    """
    audio_file: Optional[str] = None

    try:
        # ponytail: stdin in cp1252 mangles non-ASCII (accents/diacritics) -> force UTF-8
        try:
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8")
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        # Read JSON input from stdin
        try:
            input_data = sys.stdin.buffer.read().decode("utf-8").strip()
        except Exception:
            input_data = sys.stdin.read().strip()

        if not input_data:
            output = {
                "success": False,
                "message": "No input provided. Expected JSON with 'text' field.",
            }
            print(json.dumps(output))
            return 1

        # Parse JSON input
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            output = {"success": False, "message": f"Invalid JSON input: {str(e)}"}
            print(json.dumps(output))
            return 1

        # Extract parameters with defaults
        text = data.get("text", "").strip()

        if not text:
            output = {
                "success": False,
                "message": "No text provided. The 'text' field is required.",
            }
            print(json.dumps(output))
            return 1

        voice = data.get("voice", DEFAULT_VOICE)
        rate = data.get("rate", DEFAULT_RATE)
        volume = data.get("volume", DEFAULT_VOLUME)

        # Generate speech audio
        try:
            audio_file = asyncio.run(generate_speech(text, voice, rate, volume))
        except Exception as e:
            output = {
                "success": False,
                "message": f"Failed to generate speech: {str(e)}",
            }
            print(json.dumps(output))
            return 1

        # Find available audio player
        player = find_available_player()

        if player is None:
            output = {
                "success": False,
                "message": "No audio player found. Install one of: mpg123, ffmpeg, vlc, pulseaudio-utils, or alsa-utils.",
            }
            print(json.dumps(output))
            return 1

        # Play the audio
        if not play_audio(audio_file, player):
            output = {
                "success": False,
                "message": f"Failed to play audio using {player}.",
            }
            print(json.dumps(output))
            return 1

        # Success
        output = {
            "success": True,
            "message": f"Speech played successfully using {player}.",
        }
        print(json.dumps(output))
        return 0

    except KeyboardInterrupt:
        output = {"success": False, "message": "Interrupted by user."}
        print(json.dumps(output))
        return 1

    except Exception as e:
        output = {"success": False, "message": f"Unexpected error: {str(e)}"}
        print(json.dumps(output))
        return 1

    finally:
        # Cleanup temporary audio file
        if audio_file:
            cleanup_file(audio_file)


if __name__ == "__main__":
    sys.exit(main())
