import { Brain, BookOpen, Globe, ImageIcon, Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from "@/components/ui/dropdown-menu";
import type { Model } from "@/lib/api";
import type { LibraryControl } from "./LibraryControl";

export type LibraryTools = React.ComponentProps<typeof LibraryControl>;
export function ToolsMenu({
  open,
  onOpenChange,
  buttonRef,
  web,
  onWebChange,
  webBlocked,
  library,
  images,
  imageAvailable,
  imageReason,
  onImage,
  model,
  thinkValue,
  onThinkChange,
}: {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  buttonRef: React.RefObject<HTMLButtonElement | null>;
  web: boolean;
  onWebChange?: (value: boolean) => void;
  webBlocked: boolean;
  library?: LibraryTools;
  images: boolean;
  imageAvailable: boolean;
  imageReason?: string;
  onImage: () => void;
  model?: Model;
  thinkValue?: string;
  onThinkChange?: (value: string | null) => void;
}) {
  return (
    <DropdownMenu modal={false} open={open} onOpenChange={onOpenChange}>
      <DropdownMenuTrigger asChild>
        <Button
          ref={buttonRef}
          type="button"
          variant="outline"
          disabled={
            !onWebChange &&
            !library &&
            !images &&
            !model?.reasoning &&
            !thinkValue
          }
          className="composer-tools"
          aria-label="Tools"
        >
          <Wrench />
          <span>Tools</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side="top"
        align="start"
        className="composer-tools-menu"
        aria-label="Tools"
      >
        <DropdownMenuLabel>Tools</DropdownMenuLabel>
        {onWebChange && (
          <DropdownMenuCheckboxItem
            checked={web && !webBlocked}
            disabled={webBlocked}
            onSelect={(e) => e.preventDefault()}
            onCheckedChange={onWebChange}
            className="composer-tool-row"
            aria-label="Search the web"
            aria-description={
              webBlocked ? "Search is off in chats with a recording" : undefined
            }
          >
            <Globe />
            <span>
              <b>Search the web</b>
              <small>
                {webBlocked
                  ? "Search is off in chats with a recording"
                  : "Look things up while answering"}
              </small>
            </span>
            <i
              className="composer-switch"
              data-on={web && !webBlocked}
              aria-hidden
            />
          </DropdownMenuCheckboxItem>
        )}
        {library && (
          <DropdownMenuCheckboxItem
            checked={library.enabled}
            disabled={!library.enabled && !!library.reason}
            onSelect={(e) => e.preventDefault()}
            onCheckedChange={library.onToggle}
            className="composer-tool-row"
            aria-label="Library"
            aria-description={library.reason}
          >
            <BookOpen />
            <span>
              <b>Library</b>
              <small>{library.reason ?? "Answer from your saved files"}</small>
            </span>
            <i
              className="composer-switch"
              data-on={library.enabled}
              aria-hidden
            />
          </DropdownMenuCheckboxItem>
        )}
        {images && (
          <DropdownMenuItem
            disabled={!imageAvailable}
            className="composer-tool-row"
            onSelect={onImage}
            aria-label="Create image"
            aria-description={!imageAvailable ? imageReason : undefined}
          >
            <ImageIcon />
            <span>
              <b>Create image</b>
              <small>
                {!imageAvailable
                  ? (imageReason ?? "Connecting to the image service…")
                  : "Describe it and get pictures in the chat"}
              </small>
            </span>
          </DropdownMenuItem>
        )}
        {(model?.reasoning || thinkValue) && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuLabel className="flex items-center gap-2">
              <Brain className="size-4" />
              Thinking
            </DropdownMenuLabel>
            <DropdownMenuRadioGroup
              className="composer-thinking-levels"
              value={thinkValue ?? "auto"}
              aria-label="Thinking"
              onValueChange={(level) =>
                onThinkChange?.(level === "auto" ? null : level)
              }
              onKeyDown={(e) => {
                if (!["ArrowLeft", "ArrowRight"].includes(e.key)) return;
                const items = [
                  ...e.currentTarget.querySelectorAll<HTMLElement>(
                    '[role="menuitemradio"]',
                  ),
                ];
                const index = items.indexOf(
                  document.activeElement as HTMLElement,
                );
                if (index >= 0) {
                  e.preventDefault();
                  items[
                    (index + (e.key === "ArrowRight" ? 1 : items.length - 1)) %
                      items.length
                  ].focus();
                }
              }}
            >
              {["auto", ...(model?.reasoning?.options ?? [])].map((level) => (
                <DropdownMenuRadioItem
                  key={level}
                  value={level}
                  onSelect={(e) => e.preventDefault()}
                  title={level === "auto" ? "Model default" : undefined}
                  aria-label={
                    level === "auto"
                      ? "Model default"
                      : level[0].toUpperCase() + level.slice(1)
                  }
                >
                  {level === "auto"
                    ? "Model default"
                    : level[0].toUpperCase() + level.slice(1)}
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
