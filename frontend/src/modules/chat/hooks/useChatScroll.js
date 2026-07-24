import { useCallback, useEffect, useRef, useState } from "react";

const NEAR_BOTTOM_THRESHOLD = 100;

export function useChatScroll(messages, typing, loading, loadingOlder) {
  const scrollContainerRef = useRef(null);
  const bottomRef = useRef(null);
  const isNearBottomRef = useRef(true);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const prevLastMessageIdRef = useRef(null);
  const prevMessageCountRef = useRef(0);
  const initialScrollDoneRef = useRef(false);

  const checkIfNearBottom = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) {
      return true;
    }

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    return distanceFromBottom < NEAR_BOTTOM_THRESHOLD;
  }, []);

  const updateScrollState = useCallback(() => {
    const nearBottom = checkIfNearBottom();
    isNearBottomRef.current = nearBottom;
    setShowScrollButton(!nearBottom);
  }, [checkIfNearBottom]);

  const scrollToBottom = useCallback((behavior = "smooth") => {
    bottomRef.current?.scrollIntoView({ behavior, block: "end" });
    isNearBottomRef.current = true;
    setShowScrollButton(false);
  }, []);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) {
      return undefined;
    }

    const handleScroll = () => updateScrollState();

    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, [updateScrollState, loading, messages.length]);

  useEffect(() => {
    if (loading || loadingOlder) {
      return;
    }

    const lastMessage = messages[messages.length - 1];
    const lastMessageId = lastMessage?.id ?? null;
    const messageCount = messages.length;
    const prependedOlderMessages =
      messageCount > prevMessageCountRef.current &&
      lastMessageId === prevLastMessageIdRef.current;

    prevMessageCountRef.current = messageCount;
    prevLastMessageIdRef.current = lastMessageId;

    if (prependedOlderMessages) {
      return;
    }

    if (!initialScrollDoneRef.current && messageCount > 0) {
      initialScrollDoneRef.current = true;
      requestAnimationFrame(() => scrollToBottom("auto"));
      return;
    }

    if (isNearBottomRef.current) {
      requestAnimationFrame(() => scrollToBottom("smooth"));
      return;
    }

    if (messageCount > 0) {
      setShowScrollButton(true);
    }
  }, [messages, typing, loading, loadingOlder, scrollToBottom]);

  useEffect(() => {
    if (loading) {
      initialScrollDoneRef.current = false;
      prevLastMessageIdRef.current = null;
      prevMessageCountRef.current = 0;
    }
  }, [loading]);

  return {
    scrollContainerRef,
    bottomRef,
    showScrollButton: showScrollButton && messages.length > 0 && !loading,
    scrollToBottom,
  };
}
