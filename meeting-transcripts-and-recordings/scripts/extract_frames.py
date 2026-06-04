#!/usr/bin/env python3
"""Extract still frames from a video — at specific timestamps, or automatically at
scene changes. Used to capture "key moments" of a process walkthrough so the frames
can be embedded as Image widgets on the matching workflow tasks.

Runs fully locally via ffmpeg.

Usage:
    # Frames at specific timestamps (seconds, from the transcript)
    python3 extract_frames.py demo.mp4 --timestamps 312,478.5,1024 --out /tmp/frames

    # Auto-detect visually distinct moments (scene-change threshold 0..1, lower = more frames)
    python3 extract_frames.py demo.mp4 --scene-detect 0.30 --out /tmp/frames

    # Both modes can cap the frame width (default 1280px) to keep uploads small
    python3 extract_frames.py demo.mp4 --timestamps 60 --width 1280 --out /tmp/frames

Output:
    <out>/frame_<seconds>s.jpg per frame, plus <out>/manifest.json:
        [{"file": ".../frame_0312s.jpg", "timestamp": 312.0}, ...]

Prerequisites:
    ffmpeg on PATH (brew install ffmpeg / apt-get install ffmpeg)

Tip: shoot the frame 2-3 seconds AFTER the verbal anchor ("as you can see here...") —
the screen has usually settled by then.
"""

import argparse
import json
import os
import re
import subprocess
import sys


def run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def extract_at_timestamps(video: str, timestamps: list, out_dir: str, width: int) -> list:
    frames = []
    for ts in timestamps:
        name = f"frame_{int(round(ts)):05d}s.jpg"
        path = os.path.join(out_dir, name)
        # -ss before -i = fast seek; quality 2 = high; scale preserves aspect ratio
        proc = run([
            "ffmpeg", "-y", "-ss", str(ts), "-i", video,
            "-frames:v", "1", "-q:v", "2",
            "-vf", f"scale='min({width},iw)':-2",
            path,
        ])
        if proc.returncode == 0 and os.path.isfile(path) and os.path.getsize(path) > 0:
            frames.append({"file": os.path.abspath(path), "timestamp": float(ts)})
            print(f"  ✓ {name}", file=sys.stderr)
        else:
            print(f"  ✗ failed at {ts}s (past end of video?)", file=sys.stderr)
    return frames


def extract_scene_changes(video: str, threshold: float, out_dir: str, width: int,
                          max_frames: int) -> list:
    # Pass 1: find scene-change timestamps with ffmpeg's scene filter
    proc = run([
        "ffmpeg", "-i", video,
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-",
    ])
    times = [float(m) for m in re.findall(r"pts_time:(\d+\.?\d*)", proc.stderr)]
    if not times:
        print(f"no scene changes found at threshold {threshold} — try a lower value "
              f"(e.g. {max(0.05, threshold - 0.1):.2f})", file=sys.stderr)
        return []
    if len(times) > max_frames:
        # Keep an even spread rather than a burst at the start
        step = len(times) / max_frames
        times = [times[int(i * step)] for i in range(max_frames)]
        print(f"capped to {max_frames} frames (even spread)", file=sys.stderr)
    print(f"extracting {len(times)} scene-change frames...", file=sys.stderr)
    return extract_at_timestamps(video, times, out_dir, width)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract key-moment frames from a video")
    parser.add_argument("video", help="Path to video file (mp4, mov, webm, ...)")
    parser.add_argument("--timestamps", default=None,
                        help="Comma-separated seconds, e.g. 312,478.5,1024")
    parser.add_argument("--scene-detect", type=float, default=None, metavar="THRESHOLD",
                        help="Auto-detect scene changes; threshold 0..1 (0.30 is a good start)")
    parser.add_argument("--out", default="/tmp/frames", help="Output directory")
    parser.add_argument("--width", type=int, default=1280, help="Max frame width px (default 1280)")
    parser.add_argument("--max-frames", type=int, default=40,
                        help="Cap for scene-detect mode (default 40)")
    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(f"error: file not found: {args.video}", file=sys.stderr)
        return 1
    if run(["ffmpeg", "-version"]).returncode != 0:
        print("error: ffmpeg not found on PATH (brew install ffmpeg)", file=sys.stderr)
        return 1
    if not args.timestamps and args.scene_detect is None:
        print("error: provide --timestamps or --scene-detect", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    frames = []
    if args.timestamps:
        ts = [float(t) for t in args.timestamps.split(",") if t.strip()]
        frames += extract_at_timestamps(args.video, ts, args.out, args.width)
    if args.scene_detect is not None:
        frames += extract_scene_changes(args.video, args.scene_detect, args.out,
                                        args.width, args.max_frames)

    frames.sort(key=lambda f: f["timestamp"])
    manifest = os.path.join(args.out, "manifest.json")
    with open(manifest, "w") as f:
        json.dump(frames, f, indent=1)
    print(f"{len(frames)} frames → {args.out} (manifest: {manifest})", file=sys.stderr)
    print("REMINDER: review every frame before embedding — discard webcam-only shots and "
          "anything showing sensitive data.", file=sys.stderr)
    return 0 if frames else 1


if __name__ == "__main__":
    sys.exit(main())
