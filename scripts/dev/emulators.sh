#!/usr/bin/env bash
# Starts the local Firebase emulators (Auth, Firestore, Functions) with data kept in .emulator-data/.
# The Firestore emulator needs Java 11+; Homebrew's keg-only openjdk is picked up automatically.
set -euo pipefail
if ! java -version >/dev/null 2>&1; then
  for jdk in /opt/homebrew/opt/openjdk@21 /opt/homebrew/opt/openjdk /usr/local/opt/openjdk@21 /usr/local/opt/openjdk; do
    if [ -x "$jdk/bin/java" ]; then export PATH="$jdk/bin:$PATH"; break; fi
  done
fi
java -version >/dev/null 2>&1 || { echo "Java 11+ is required for the Firestore emulator (macOS: brew install openjdk@21)"; exit 1; }
npm --prefix functions run build >/dev/null
exec firebase emulators:start --only "${EMULATORS:-auth,firestore,functions}" --import=.emulator-data --export-on-exit
