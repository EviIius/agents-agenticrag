import {
  ArrowDown,
  FileText,
  ImageIcon,
  Play,
  Brain,
  Check,
  Mic,
  SlidersHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRef } from "react";

export type StepPanel =
  "input" | "model" | "cleanup" | "review" | "images" | "output";
export function WorkflowCanvas({
  template,
  onTemplate,
  panel,
  onPanel,
  cleanup,
  review,
  count,
  model,
  children,
  onStart,
  disabled,
  busy,
}: {
  template: "brief_images" | "meeting_pack";
  onTemplate: (template: "brief_images" | "meeting_pack") => void;
  panel: StepPanel;
  onPanel: (panel: StepPanel) => void;
  cleanup: boolean;
  review: boolean;
  count: number;
  model?: string;
  children: React.ReactNode;
  onStart: () => void;
  disabled: boolean;
  busy: boolean;
}) {
  const settings = useRef<HTMLElement>(null);
  const configure = (next: StepPanel) => {
    onPanel(next);
    if (matchMedia("(max-width: 1023px)").matches)
      requestAnimationFrame(() =>
        settings.current?.scrollIntoView({
          block: "nearest",
          behavior: "instant",
        }),
      );
  };
  const image = template === "brief_images";
  const steps = [
    {
      id: "input" as const,
      title: "Start",
      detail: image ? "Your image brief" : "Choose a recording",
      icon: Play,
    },
    ...(!image
      ? [
          {
            id: "cleanup" as const,
            title: "Clean up transcript",
            detail: cleanup ? "Enabled · original kept" : "Optional · skipped",
            icon: SlidersHorizontal,
          },
        ]
      : []),
    {
      id: "model" as const,
      title: image ? "Draft image prompt" : "Draft meeting pack",
      detail: model ?? "Choose your text model",
      icon: Brain,
    },
    ...(image
      ? [
          {
            id: "review" as const,
            title: "Review prompt",
            detail: review ? "Pause for your approval" : "Approval pause off",
            icon: Check,
          },
          {
            id: "images" as const,
            title: "Generate images",
            detail: `${count} ${count === 1 ? "image" : "images"} · FLUX.2 klein`,
            icon: ImageIcon,
          },
        ]
      : []),
    {
      id: "output" as const,
      title: "Review and save",
      detail: image ? "Choose your favorite" : "Check the original transcript",
      icon: FileText,
    },
  ];
  const selected = steps.find((step) => step.id === panel) ?? steps[0];
  return (
    <section
      aria-label="Workflow builder"
      className="mb-8 overflow-hidden rounded-xl border border-line bg-surface"
    >
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4">
        <div>
          <h2 className="font-semibold">
            {image ? "Brief to images" : "Recording to meeting pack"}
          </h2>
          <p className="mt-1 text-xs text-fg-3">
            Select a step to set it up. Runs start when you press Start
            workflow.
          </p>
        </div>
        <Button className="h-11 gap-2" disabled={disabled} onClick={onStart}>
          <Play className="size-4" />
          {busy ? "Accepting…" : "Start workflow"}
        </Button>
      </header>
      <div className="grid min-w-0 lg:grid-cols-[180px_minmax(240px,1fr)_340px]">
        <aside
          className="border-b border-line p-3 lg:border-r lg:border-b-0"
          aria-label="Workflow templates"
        >
          <h3 className="mb-2 text-xs font-medium text-fg-3">
            Start with a template
          </h3>
          <div className="flex flex-wrap gap-2 lg:flex-col">
            <Button
              variant={image ? "secondary" : "ghost"}
              aria-pressed={image}
              className="h-auto min-h-11 justify-start whitespace-normal text-left"
              onClick={() => onTemplate("brief_images")}
            >
              <ImageIcon className="size-4 shrink-0" /> Brief to images
            </Button>
            <Button
              variant={!image ? "secondary" : "ghost"}
              aria-pressed={!image}
              className="h-auto min-h-11 justify-start whitespace-normal text-left"
              onClick={() => onTemplate("meeting_pack")}
            >
              <Mic className="size-4 shrink-0" /> Recording to meeting pack
            </Button>
          </div>
          <p className="mt-4 hidden text-xs text-fg-3 lg:block">
            Each step keeps its output. You can review, cancel or retry a saved
            run.
          </p>
        </aside>
        <div
          className="workflow-canvas min-w-0 border-b border-line p-5 lg:border-r lg:border-b-0"
          aria-label="Connected workflow steps"
        >
          <ol className="mx-auto w-full max-w-72">
            {steps.map((step, index) => (
              <li key={step.id}>
                {index > 0 && (
                  <div
                    aria-hidden="true"
                    className="flex h-7 justify-center text-fg-3"
                  >
                    <ArrowDown className="h-7 w-4" />
                  </div>
                )}
                <button
                  type="button"
                  aria-label={`Configure ${step.title}`}
                  aria-pressed={panel === step.id}
                  onClick={() => configure(step.id)}
                  className={`flex min-h-16 w-full items-center gap-3 rounded-xl border bg-surface p-3 text-left shadow-sm ${panel === step.id ? "border-brand ring-2 ring-brand-soft" : "border-line hover:border-line-strong"}`}
                >
                  <span className="flex size-9 shrink-0 items-center justify-center rounded-md bg-surface-2 text-brand">
                    <step.icon className="size-4" />
                  </span>
                  <span className="min-w-0">
                    <span className="block text-sm font-medium">
                      {step.title}
                    </span>
                    <span className="mt-1 block break-words text-xs text-fg-2">
                      {step.detail}
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ol>
        </div>
        <aside
          ref={settings}
          aria-label="Selected step settings"
          className="min-w-0 p-4"
        >
          <h3 className="mb-4 flex items-center gap-2 font-medium">
            <selected.icon className="size-4 text-brand" />
            {selected.title}
          </h3>
          {children}
        </aside>
      </div>
    </section>
  );
}
