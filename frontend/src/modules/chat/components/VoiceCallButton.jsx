import { Mic, MicOff } from "lucide-react";
import Button from "../../../shared/components/Button.jsx";

export default function VoiceCallButton({
  isActive,
  isConnecting,
  disabled,
  onToggle,
}) {
  const label = isConnecting
    ? "Connecting..."
    : isActive
      ? "End call"
      : "Start voice";

  return (
    <Button
      type="button"
      variant={isActive ? "danger" : "secondary"}
      disabled={disabled || isConnecting}
      onClick={onToggle}
      className={`self-end whitespace-nowrap ${isActive ? "animate-pulse" : ""}`}
      aria-pressed={isActive}
      aria-label={label}
    >
      {isActive ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
      <span className="ml-2 hidden sm:inline">{label}</span>
    </Button>
  );
}
