#!/usr/bin/env python3
"""Transcribe an audio or video file locally with Whisper, emitting timestamped JSON.

Runs fully on the local machine — no audio/video data leaves it.

Usage:
    python3 transcribe.py <media-file> [--model base] [--out /tmp/call_transcript.json] [--language en]

Output JSON shape:
    {
      "source": "<input path>",
      "model": "base",
      "duration": 3120.5,
      "text": "<full transcript>",
      "segments": [
        {"start": 0.0, "end": 4.2, "text": "Thanks everyone for joining..."},
        ...
      ]
    }

Prerequisites:
    pip3 install openai-whisper --break-system-packages
    ffmpeg on PATH (whisper uses it to decode both audio and video containers)
"""

import argparse
import json
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Whisper transcription with timestamps")
    parser.add_argument("media", help="Path to audio/video file (mp3, m4a, wav, mp4, mov, webm, ...)")
    parser.add_argument("--model", default="base",
                        help="Whisper model size: tiny|base|small|medium|large (default: base)")
    parser.add_argument("--out", default="/tmp/call_transcript.json", help="Output JSON path")
    parser.add_argument("--language", default=None,
                        help="Force a language code (e.g. en). Default: auto-detect")
    args = parser.parse_args()

    if not os.path.isfile(args.media):
        print(f"error: file not found: {args.media}", file=sys.stderr)
        return 1

    try:
        import whisper  # type: ignore
    except ImportError:
        print("error: openai-whisper is not installed.\n"
              "       pip3 install openai-whisper --break-system-packages", file=sys.stderr)
        return 1

    print(f"loading whisper model '{args.model}'...", file=sys.stderr)
    model = whisper.load_model(args.model)

    print(f"transcribing {args.media} (this can take a while for long recordings)...",
          file=sys.stderr)
    kwargs = {"verbose": False}
    if args.language:
        kwargs["language"] = args.language
    result = model.transcribe(args.media, **kwargs)

    segments = [
        {"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()}
        for s in result.get("segments", [])
    ]
    payload = {
        "source": os.path.abspath(args.media),
        "model": args.model,
        "duration": segments[-1]["end"] if segments else 0.0,
        "text": result.get("text", "").strip(),
        "segments": segments,
    }

    with open(args.out, "w") as f:
        json.dump(payload, f, indent=1)

    print(f"wrote {len(segments)} segments to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
