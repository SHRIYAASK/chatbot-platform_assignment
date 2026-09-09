from livekit import agents

from app.modules.voice.worker.agent import server

if __name__ == "__main__":
    agents.cli.run_app(server)
