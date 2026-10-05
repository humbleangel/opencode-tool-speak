import { tool } from "@opencode-ai/plugin";
import { z } from "zod";
import { spawn } from "child_process";
import path from "path";

const speakTool = tool({
  description: "Convert text to speech using Microsoft Edge TTS",
  args: {
    text: z.string().describe("The text to convert to speech"),
    voice: z
      .string()
      .default("pt-BR-AntonioNeural")
      .describe("The voice to use for speech synthesis"),
    rate: z
      .string()
      .default("+20%")
      .describe("The speech rate adjustment"),
    volume: z
      .string()
      .default("+0%")
      .describe("The speech volume adjustment"),
  },
  async execute(args, context) {
    const { text, voice, rate, volume } = args;

    // Get the path to the Python script
    const pythonScriptPath = path.join(process.env.APPDATA ?? "", "..", "..", ".config", "opencode", "tools", "speak.py");

    // Prepare the input JSON for the Python script
    const inputJson = JSON.stringify({
      text,
      voice,
      rate,
      volume,
    });

    // Fire-and-forget: spawn detached, return immediately.
    const child = spawn("python", [pythonScriptPath], {
      detached: true,
      stdio: ["pipe", "ignore", "ignore"],
      windowsHide: true,
    });
    child.stdin.write(inputJson);
    child.stdin.end();
    child.unref();

    return "Speech queued.";
  },
});

export default speakTool;
