import logging
import os
import subprocess
import sys
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

_process: subprocess.Popen | None = None


def voice_agent_configured() -> bool:
    return bool(
        settings.LIVEKIT_URL.strip()
        and settings.LIVEKIT_API_KEY.strip()
        and settings.LIVEKIT_API_SECRET.strip()
        and settings.SARVAM_API_KEY.strip()
    )


def _worker_env() -> dict[str, str]:
    env = os.environ.copy()
    env["LIVEKIT_URL"] = settings.LIVEKIT_URL
    env["LIVEKIT_API_KEY"] = settings.LIVEKIT_API_KEY
    env["LIVEKIT_API_SECRET"] = settings.LIVEKIT_API_SECRET
    env["SARVAM_API_KEY"] = settings.SARVAM_API_KEY
    env["BACKEND_INTERNAL_URL"] = settings.BACKEND_INTERNAL_URL
    return env


def start_embedded_voice_agent() -> bool:
    """Spawn the LiveKit voice worker as a child process of the API server."""
    global _process

    if not settings.VOICE_AGENT_ENABLED:
        logger.info("Embedded voice agent disabled (VOICE_AGENT_ENABLED=false).")
        return False

    if not voice_agent_configured():
        logger.info(
            "Voice agent not started: set LIVEKIT_URL, LIVEKIT_API_KEY, "
            "LIVEKIT_API_SECRET, and SARVAM_API_KEY to enable voice."
        )
        return False

    if _process is not None and _process.poll() is None:
        logger.warning("Embedded voice agent is already running.")
        return True

    backend_root = Path(__file__).resolve().parents[4]
    cmd = [sys.executable, "-m", "app.modules.voice.worker", "start"]
    logger.info("Starting embedded voice agent worker")
    _process = subprocess.Popen(
        cmd,
        cwd=backend_root,
        env=_worker_env(),
    )
    return True


def stop_embedded_voice_agent() -> None:
    global _process

    if _process is None:
        return

    if _process.poll() is None:
        logger.info("Stopping embedded voice agent worker")
        _process.terminate()
        try:
            _process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            logger.warning("Voice agent did not exit gracefully; killing process.")
            _process.kill()
            _process.wait()

    _process = None
