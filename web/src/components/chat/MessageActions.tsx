import {
  Copy,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Pencil,
  Info,
  ChevronDown,
} from "lucide-react";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import { CopyFeedback } from "./CopyFeedback";
import { IconButton } from "@/components/app/IconButton";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import type { Message, Model } from "@/lib/api";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { siblings } from "@/lib/tree";
export function MessageActions({
  message,
  messages,
  onEdit,
  onRegenerate,
  onBranch,
  models = [],
  onRegenerateWith,
}: {
  models?: Model[];
  onRegenerateWith?: (model: Model) => void;
  message: Message;
  messages: Message[];
  onEdit: () => void;
  onRegenerate: () => void;
  onBranch: (id: string) => void;
}) {
  const feedback = useCopyFeedback();
  const branches = siblings(messages, message),
    index = branches.findIndex((m) => m.id === message.id);
  return (
    <div className="flex flex-wrap items-center">
      <IconButton
        label="Copy message"
        onClick={() =>
          void feedback.copy(
            message.role === "assistant"
              ? message.content.replace(/\[\d+\]/g, "")
              : message.content,
          )
        }
      >
        {!feedback.copied && <Copy />}
        <CopyFeedback {...feedback} />
      </IconButton>
      {message.role === "user" ? (
        <IconButton label="Edit message" onClick={onEdit}>
          <Pencil />
        </IconButton>
      ) : (
        <>
          <IconButton label="Regenerate answer" onClick={onRegenerate}>
            <RotateCcw />
          </IconButton>
          {models.length > 0 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <IconButton label="Regenerate with another model">
                  <ChevronDown />
                </IconButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>Regenerate with…</DropdownMenuLabel>
                {models.map((m) => (
                  <DropdownMenuItem
                    key={m.connection_id + m.model_id}
                    onSelect={() => onRegenerateWith?.(m)}
                  >
                    {m.display_name}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          <Popover>
            <PopoverTrigger asChild>
              <IconButton label="Message info">
                <Info />
              </IconButton>
            </PopoverTrigger>
            <PopoverContent className="max-h-[60dvh] overflow-y-auto">
              <dl className="space-y-3 text-xs">
                {[
                  ["Model", message.model?.display_name ?? "Unknown"],
                  [
                    "Speed",
                    message.stats
                      ? `${message.stats.tokens_per_sec.toFixed(1)} tokens/s`
                      : "Unavailable",
                  ],
                  [
                    "Tokens",
                    message.stats
                      ? `${message.stats.tokens_estimated ? "≈" : ""}${message.stats.completion_tokens}`
                      : "Unavailable",
                  ],
                  [
                    "Time to first token",
                    message.stats?.ttft_ms == null
                      ? "Unavailable"
                      : `${(message.stats.ttft_ms / 1000).toFixed(2)} s`,
                  ],
                  [
                    "Context used",
                    message.stats?.prompt_tokens == null
                      ? "Unavailable"
                      : `${message.stats.prompt_tokens} of ${message.stats.context_length} tokens`,
                  ],
                  [
                    "Parameters sent",
                    Object.entries(message.stats?.params ?? {})
                      .map(([key, value]) => `${key}: ${String(value)}`)
                      .join(" · ") || "Model defaults",
                  ],
                  ...(message.web?.ranking
                    ? [["Ranking", message.web.ranking]]
                    : []),
                ].map(([label, value]) => (
                  <div key={label}>
                    <dt className="text-fg-3">{label}</dt>
                    <dd className="break-words">{value}</dd>
                  </div>
                ))}
              </dl>
            </PopoverContent>
          </Popover>
        </>
      )}
      {branches.length > 1 && (
        <>
          <IconButton
            label="Previous branch"
            disabled={index === 0}
            onClick={() => onBranch(branches[index - 1]!.id)}
          >
            <ChevronLeft />
          </IconButton>
          <span className="meta">
            {index + 1} / {branches.length}
          </span>
          <IconButton
            label="Next branch"
            disabled={index === branches.length - 1}
            onClick={() => onBranch(branches[index + 1]!.id)}
          >
            <ChevronRight />
          </IconButton>
        </>
      )}
    </div>
  );
}
