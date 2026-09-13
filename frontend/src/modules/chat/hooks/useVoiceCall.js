import { useCallback, useEffect, useRef, useState } from "react";
import { ParticipantKind, Room, RoomEvent, Track } from "livekit-client";
import { fetchVoiceToken } from "../services/voiceService.js";

const AGENT_JOIN_TIMEOUT_MS = 20000;

function isAgentParticipant(participant) {
  return (
    participant?.kind === ParticipantKind.AGENT ||
    String(participant?.identity || "").includes("agent")
  );
}

function attachAudioTrack(track, elements) {
  const element = track.attach();
  element.autoplay = true;
  element.playsInline = true;
  document.body.appendChild(element);
  elements.add(element);
  element.play?.().catch(() => {});
}

function detachAudioTrack(track, elements) {
  track.detach().forEach((element) => {
    elements.delete(element);
    element.remove();
  });
}

export function useVoiceCall(projectId, conversationId, { onTurnComplete } = {}) {
  const roomRef = useRef(null);
  const audioElementsRef = useRef(new Set());
  const agentWaitRef = useRef(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);

  const cleanupAudio = useCallback(() => {
    audioElementsRef.current.forEach((element) => element.remove());
    audioElementsRef.current.clear();
  }, []);

  const disconnect = useCallback(async () => {
    if (agentWaitRef.current) {
      clearTimeout(agentWaitRef.current);
      agentWaitRef.current = null;
    }

    const room = roomRef.current;
    roomRef.current = null;
    setIsActive(false);
    cleanupAudio();

    if (room) {
      await room.disconnect();
    }
  }, [cleanupAudio]);

  const connect = useCallback(async () => {
    if (!projectId || !conversationId || isConnecting || isActive) {
      return;
    }

    setError(null);
    setIsConnecting(true);

    try {
      const { livekit_url: livekitUrl, token } = await fetchVoiceToken(
        projectId,
        conversationId,
      );

      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      roomRef.current = room;

      const markAgentPresent = () => {
        if (agentWaitRef.current) {
          clearTimeout(agentWaitRef.current);
          agentWaitRef.current = null;
        }
      };

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === Track.Kind.Audio) {
          attachAudioTrack(track, audioElementsRef.current);
        }
      });

      room.on(RoomEvent.TrackUnsubscribed, (track) => {
        if (track.kind === Track.Kind.Audio) {
          detachAudioTrack(track, audioElementsRef.current);
        }
      });

      room.on(RoomEvent.ParticipantConnected, (participant) => {
        if (isAgentParticipant(participant)) {
          markAgentPresent();
        }
      });

      room.on(RoomEvent.Disconnected, () => {
        setIsActive(false);
        roomRef.current = null;
        cleanupAudio();
      });

      await room.connect(livekitUrl, token);
      await room.startAudio();
      await room.localParticipant.setMicrophoneEnabled(true);

      const agentAlreadyPresent = [...room.remoteParticipants.values()].some(isAgentParticipant);
      if (!agentAlreadyPresent) {
        agentWaitRef.current = setTimeout(() => {
          setError(
            "Voice agent did not join the room. Ensure LiveKit and Sarvam credentials are configured on the backend and the embedded voice worker is running.",
          );
        }, AGENT_JOIN_TIMEOUT_MS);
      }

      setIsActive(true);
    } catch (connectError) {
      const detail = connectError?.response?.data?.detail;
      setError(
        (typeof detail === "string" && detail) ||
          connectError.message ||
          "Voice call failed.",
      );
      await disconnect();
    } finally {
      setIsConnecting(false);
    }
  }, [cleanupAudio, conversationId, disconnect, isActive, isConnecting, projectId]);

  const toggleCall = useCallback(async () => {
    if (isActive || isConnecting) {
      await disconnect();
      onTurnComplete?.();
      return;
    }

    await connect();
  }, [connect, disconnect, isActive, isConnecting, onTurnComplete]);

  useEffect(() => {
    if (!isActive || !onTurnComplete) {
      return undefined;
    }

    const intervalId = setInterval(() => {
      onTurnComplete();
    }, 4000);

    return () => clearInterval(intervalId);
  }, [isActive, onTurnComplete]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect, projectId, conversationId]);

  return {
    isActive,
    isConnecting,
    error,
    toggleCall,
    disconnect,
  };
}
