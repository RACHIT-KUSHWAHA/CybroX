#!/bin/bash

# Check if SESSION_STRING is present (critical for userbot)
if [ -z "$STRINGSESSION" ] && [ -z "$SESSION_STRING" ]; then
    echo "Error: STRINGSESSION or SESSION_STRING environment variable is not set."
    echo "Please configure your session string to start the userbot."
    # We don't exit here immediately to allow the container to stay alive if needed for debugging,
    # but the bot won't work. However, for "Crash Loop" prevention, maybe we should just sleep?
    # But usually failing fast is better unless we have a specific "keep alive" mechanism requested for config.
    # The prompt said "prevent crash loops", but usually that implies the app shouldn't crash just because of missing config if we can help it,
    # OR it means we should give a clear error.
    # Let's echo and exit 1, usually platforms restart.
    exit 1
fi

echo "Starting Legendbot Userbot (Lite Plan)..."
python3 -m userbot
