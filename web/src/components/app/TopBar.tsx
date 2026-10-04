import { PanelLeftOpen, SlidersHorizontal, Ellipsis } from "lucide-react";
import { useUI } from "@/stores/ui";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { IconButton } from "./IconButton";
import { ModelPicker } from "./ModelPicker";
import { fixtureModels } from "@/design/ProductionFixtures";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
export function TopBar() {
  const { collapsed, set } = useUI();
  const [current, choose] = useState(fixtureModels[0]);
  const desktop = useMediaQuery("(min-width: 1024px)");
  return (
    <header className="topbar">
      <div className="flex min-w-0 flex-1 items-center">
        {(!desktop || collapsed) && (
          <IconButton
            label="Open sidebar"
            onClick={() =>
              set(desktop ? { collapsed: false } : { sidebar: true })
            }
          >
            <PanelLeftOpen />
          </IconButton>
        )}
        <ModelPicker
          models={fixtureModels}
          current={current}
          onChoose={choose}
        />
      </div>
      <span className="hidden max-w-64 flex-1 truncate text-center text-xs text-fg-3 md:block">
        A clearer way to learn
      </span>
      <div className="flex shrink-0 items-center">
        <IconButton
          label="Chat settings"
          onClick={() => set({ panel: !useUI.getState().panel })}
        >
          <SlidersHorizontal />
        </IconButton>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <IconButton label="Chat actions">
              <Ellipsis />
            </IconButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {["Rename", "Pin", "Export", "Delete"].map((action) => (
              <DropdownMenuItem
                key={action}
                onSelect={() =>
                  toast(
                    "Design preview · open the main app to manage saved chats",
                  )
                }
              >
                {action}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
