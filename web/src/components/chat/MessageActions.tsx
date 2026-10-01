import {
  Copy,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Pencil,
  Info,
  ChevronDown,
} from "lucide-react";
import { toast } from "sonner";
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
  const branches = siblings(messages, message),
    index = branches.findIndex((m) => m.id === message.id);
  return (
    <div className="flex flex-wrap items-center">
      <IconButton
        label="Copy message"
        onClick={() =>
          void navigator.clipboard
            .writeText(
              message.role === "assistant"
                ? message.content.replace(/\[\d+\]/g, "")
                : message.content,
            )
            .then(() => toast("Copied"))
        }
      >
        <Copy />
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
              <p className="font-medium break-all">
                {message.model?.display_name}
              </p>
              <dl className="mt-3 space-y-2 text-xs">
                {Object.entries(message.stats ?? {}).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-fg-3">{key.replaceAll("_", " ")}</dt>
                    <dd className="break-all">
                      {key === "params" && !Object.keys(value as object).length
                        ? "Model defaults"
                        : typeof value === "object"
                          ? JSON.stringify(value)
                          : String(value)}
                    </dd>
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
