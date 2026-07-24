import { useCallback, useEffect, useRef, useState } from "react";
import { CHAT_PAGE_SIZE, fetchMessages } from "../services/chatService.js";

const SCROLL_TOP_THRESHOLD = 100;

function mergeUniqueMessages(existing, incoming) {
  const seen = new Set(existing.map((message) => String(message.id)));
  const uniqueIncoming = incoming.filter((message) => !seen.has(String(message.id)));
  return [...uniqueIncoming, ...existing];
}

export function useInfiniteChat(projectId, conversationId) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingOlder, setLoadingOlder] = useState(false);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(false);

  const nextCursorRef = useRef(null);
  const loadingOlderRef = useRef(false);
  const initialLoadRef = useRef(false);

  const applyPage = useCallback((data) => {
    nextCursorRef.current = data.next_cursor || null;
    setHasMore(Boolean(data.has_more));
    return data.messages || [];
  }, []);

  const loadInitial = useCallback(async () => {
    if (!projectId || !conversationId) {
      setMessages([]);
      setLoading(false);
      setHasMore(false);
      nextCursorRef.current = null;
      return;
    }

    setLoading(true);
    setError(null);
    initialLoadRef.current = false;

    try {
      const data = await fetchMessages(projectId, conversationId, { limit: CHAT_PAGE_SIZE });
      setMessages(applyPage(data));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load chat history.");
      setMessages([]);
      setHasMore(false);
      nextCursorRef.current = null;
    } finally {
      setLoading(false);
      initialLoadRef.current = true;
    }
  }, [projectId, conversationId, applyPage]);

  useEffect(() => {
    loadInitial();
  }, [loadInitial]);

  const loadOlderMessages = useCallback(
    async (scrollContainerRef) => {
      if (
        !projectId ||
        !conversationId ||
        !hasMore ||
        !nextCursorRef.current ||
        loadingOlderRef.current ||
        loading
      ) {
        return;
      }

      const container = scrollContainerRef?.current;
      const previousScrollHeight = container?.scrollHeight ?? 0;
      const previousScrollTop = container?.scrollTop ?? 0;

      loadingOlderRef.current = true;
      setLoadingOlder(true);
      setError(null);

      try {
        const data = await fetchMessages(projectId, conversationId, {
          cursor: nextCursorRef.current,
          limit: CHAT_PAGE_SIZE,
        });

        const pageMessages = data.messages || [];
        nextCursorRef.current = data.next_cursor || null;
        setHasMore(Boolean(data.has_more));

        setMessages((current) => mergeUniqueMessages(current, pageMessages));

        if (container) {
          requestAnimationFrame(() => {
            const heightDelta = container.scrollHeight - previousScrollHeight;
            container.scrollTop = previousScrollTop + heightDelta;
          });
        }
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load older messages.");
      } finally {
        loadingOlderRef.current = false;
        setLoadingOlder(false);
      }
    },
    [projectId, conversationId, hasMore, loading],
  );

  const handleScroll = useCallback(
    (scrollContainerRef) => {
      const container = scrollContainerRef?.current;
      if (!container || loading || loadingOlderRef.current || !hasMore) {
        return;
      }

      if (container.scrollTop <= SCROLL_TOP_THRESHOLD) {
        loadOlderMessages(scrollContainerRef);
      }
    },
    [loading, hasMore, loadOlderMessages],
  );

  const appendOptimisticUserMessage = useCallback((content) => {
    const tempId = `temp-${Date.now()}`;
    const message = {
      id: tempId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [...current, message]);
    return tempId;
  }, []);

  const finalizeMessages = useCallback((userMessage, assistantMessage, tempId) => {
    setMessages((current) => {
      const withoutTemp = tempId
        ? current.filter((message) => message.id !== tempId)
        : current.filter((message) => !String(message.id).startsWith("temp-"));

      return [...withoutTemp, userMessage, assistantMessage];
    });
  }, []);

  const syncMessages = useCallback(async () => {
    if (!projectId || !conversationId) {
      return;
    }

    try {
      const data = await fetchMessages(projectId, conversationId, { limit: CHAT_PAGE_SIZE });
      setMessages(applyPage(data));
    } catch {
      // Keep the current list if a background sync fails.
    }
  }, [projectId, conversationId, applyPage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setHasMore(false);
    nextCursorRef.current = null;
  }, []);

  return {
    messages,
    loading,
    loadingOlder,
    error,
    hasMore,
    initialLoadComplete: initialLoadRef.current,
    reloadMessages: loadInitial,
    loadOlderMessages,
    handleScroll,
    appendOptimisticUserMessage,
    finalizeMessages,
    syncMessages,
    clearMessages,
  };
}
