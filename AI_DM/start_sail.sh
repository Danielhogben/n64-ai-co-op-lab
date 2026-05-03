#!/bin/bash
cd ~/HylianModding/tools/sail
deno run --allow-net --allow-read examples/twitch_custom_sail.ts --port 43384 --debug
