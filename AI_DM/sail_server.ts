import { Sail } from "../tools/sail/Sail.ts";

const port = 43384;
const sail = new Sail({ port, debug: true });

sail.on("clientConnected", (client) => {
  console.log("[SailServer] Ship of Harkinian client connected!");

  client.on("disconnected", () => {
    console.log("[SailServer] Client disconnected.");
  });
});

console.log("[SailServer] Starting Sail server...");
await sail.start();
