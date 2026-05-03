#!/bin/bash
# Start the Sail TCP bridge for Project Nexus
cd /home/donn/HylianModding/AI_DM
deno run --allow-net --allow-read sail_server.ts --port 43384 --debug
