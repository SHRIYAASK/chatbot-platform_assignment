import { useCallback, useEffect, useRef, useState } from "react";
import { isAbortError } from "../../../shared/utils/abortError.js";
import { useToast } from "../../../shared/hooks/useToast.jsx";
import { sendMessage } from "../services/chatService.js";

export function useChat(
  projectId,
  conversationId,
  { appendOptimisticUserMessage, finalizeMessages, syncMessages, onMessageSent },
) {
  const { showError } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [typing, setTyping] = useState(false);
  const abortControllerRef = useRef(null);
  const optimisticTempIdRef = useRef(null);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const stopGeneration = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const sendChatMessage = useCallback(
    async (content) => {
      const trimmed = content.trim();
      if (!trimmed || isGenerating || !projectId || !conversationId) {
        return false;
      }

      const controller = new AbortController();
      abortControllerRef.current = controller;
      optimisticTempIdRef.current = appendOptimisticUserMessage(trimmed);

      setIsGenerating(true);
      setTyping(true);

      try {
        const data = await sendMessage(projectId, conversationId, trimmed, {
          signal: controller.signal,
        });
        finalizeMessages(data.user_message, data.assistant_message, optimisticTempIdRef.current);
        onMessageSent?.();
        return true;
      } catch (error) {
        if (isAbortError(error)) {
          await syncMessages();
          return false;
        }

        await syncMessages();
        showError(error.response?.data?.detail || "Failed to send message.");
        return false;
      } finally {
        setIsGenerating(false);
        setTyping(false);
        abortControllerRef.current = null;
        optimisticTempIdRef.current = null;
      }
    },
    [
      projectId,
      conversationId,
      isGenerating,
      appendOptimisticUserMessage,
      finalizeMessages,
      syncMessages,
      onMessageSent,
      showError,
    ],
  );

  return {
    isGenerating,
    typing,
    sendChatMessage,
    stopGeneration,
  };
}
