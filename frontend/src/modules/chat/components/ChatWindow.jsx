import Loader from "../../../shared/components/Loader.jsx";
import ScrollToBottomButton from "../../../shared/components/ScrollToBottomButton/ScrollToBottomButton.jsx";
import { useChatScroll } from "../hooks/useChatScroll.js";
import ChatHistoryLoader from "./ChatHistoryLoader.jsx";
import MessageBubble from "./MessageBubble.jsx";
import MessageInput from "./MessageInput.jsx";
import TypingIndicator from "./TypingIndicator.jsx";

export default function ChatWindow({
  messages,
  loading,
  loadingOlder,
  hasMore,
  onScroll,
  typing,
  isGenerating,
  onSend,
  onStop,
  focusInputToken,
}) {
  const { scrollContainerRef, bottomRef, showScrollButton, scrollToBottom } =
    useChatScroll(messages, typing, loading, loadingOlder);

  const handleScroll = () => {
    onScroll?.(scrollContainerRef);
  };

  return (
    <div className="relative flex min-h-0 flex-1 flex-col bg-slate-50">
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-6 sm:px-6"
      >
        {loading ? (
          <Loader label="Loading chat history..." />
        ) : messages.length === 0 ? (
          <div className="flex h-full min-h-[320px] items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-medium text-slate-900">Start the conversation</p>
              <p className="mt-2 text-sm text-slate-600">
                Send a message to begin chatting with this AI agent.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto w-full max-w-4xl space-y-5">
            <ChatHistoryLoader loadingOlder={loadingOlder} hasMore={hasMore} />
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {typing ? <TypingIndicator /> : null}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <ScrollToBottomButton
        showButton={showScrollButton}
        onScrollToBottom={() => scrollToBottom("smooth")}
      />

      <MessageInput
        onSend={onSend}
        onStop={onStop}
        isGenerating={isGenerating}
        disabled={loading}
        focusInputToken={focusInputToken}
      />
    </div>
  );
}
