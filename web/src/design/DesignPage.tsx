import { lazy, Suspense } from "react";
import { Link } from "react-router";
import { Button } from "@/components/ui/button";
import {
  AssistantMessage,
  type AssistantState,
} from "@/components/chat/AssistantMessage";
import { UserMessage } from "@/components/chat/UserMessage";
import { Composer } from "@/components/chat/Composer";
import { Sidebar, type SidebarState } from "@/components/app/Sidebar";
import { ModelPicker, type PickerState } from "@/components/app/ModelPicker";
import { ChatSettingsPanel } from "@/components/settings/ChatSettingsPanel";
import { useUI } from "@/stores/ui";
const Markdown = lazy(() => import("@/components/chat/Markdown"));
export function DesignPage() {
  const ui = useUI();
  return (
    <div className="design-page">
      <header className="mb-10">
        <p className="mb-3 text-xs text-fg-3">WORKBENCH / FOUNDATION</p>
        <h1 className="font-serif text-3xl leading-10">
          A quieter place to think.
        </h1>
        <p className="mt-3 max-w-xl text-fg-2">
          The living component guide. Every answer and statistic here is a Fake
          runtime fixture. Switch themes to review the same states.
        </p>
        <div className="mt-5 flex flex-wrap gap-2">
          <Button
            variant={ui.theme === "light" ? "default" : "outline"}
            onClick={() => ui.set({ theme: "light" })}
          >
            Light
          </Button>
          <Button
            variant={ui.theme === "dark" ? "default" : "outline"}
            onClick={() => ui.set({ theme: "dark" })}
          >
            Dark
          </Button>
          <Button variant="outline" onClick={() => ui.set({ theme: "system" })}>
            System
          </Button>
          <Button asChild variant="outline">
            <Link to="/c/fixture">Fixture chat</Link>
          </Button>
          <Button variant="outline" onClick={() => ui.set({ settings: true })}>
            Appearance
          </Button>
        </div>
      </header>
      <section aria-labelledby="typography" className="design-card mb-8">
        <h2 id="typography" className="mb-5 text-lg font-medium">
          Typography & surfaces
        </h2>
        <p className="font-serif text-2xl leading-8">
          Space for the answer to breathe.
        </p>
        <p className="mt-3 text-fg-2">
          Geist for controls. Newsreader for answers. Geist Mono for code.
        </p>
        <p className="meta mt-2">Metadata · 12 / 16 · tabular numbers</p>
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {["bg", "surface", "surface-2", "surface-3"].map((surface) => (
            <div
              key={surface}
              className={`rounded-md border border-line p-4 bg-${surface}`}
            >
              <span className="text-fg">{surface}</span>
            </div>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <Button>Primary</Button>
          <Button variant="outline">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>
      <section aria-labelledby="models" className="mb-8">
        <h2 id="models" className="mb-4 text-lg font-medium">
          Model picker
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {(
            [
              "ready",
              "loading",
              "offline",
              "empty",
              "loading-model",
            ] as PickerState[]
          ).map((state) => (
            <div className="design-card" key={state}>
              <h3 className="mb-3 font-medium">{state}</h3>
              <ModelPicker state={state} />
            </div>
          ))}
        </div>
      </section>
      <section aria-labelledby="sidebar-states" className="mb-8">
        <h2 id="sidebar-states" className="mb-4 text-lg font-medium">
          Sidebar states
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(
            ["ready", "loading", "empty", "search", "error"] as SidebarState[]
          ).map((state) => (
            <div
              className="overflow-hidden rounded-lg border border-line"
              key={state}
            >
              <h3 className="bg-surface px-4 py-3 font-medium">{state}</h3>
              <div className="h-80">
                <Sidebar state={state} />
              </div>
            </div>
          ))}
          <div className="overflow-hidden rounded-lg border border-line">
            <h3 className="bg-surface px-4 py-3 font-medium">Collapsed rail</h3>
            <div className="h-80 w-14">
              <Sidebar collapsed />
            </div>
          </div>
        </div>
      </section>
      <section aria-labelledby="messages" className="mb-8">
        <h2 id="messages" className="mb-4 text-lg font-medium">
          Messages
        </h2>
        <div className="design-card mb-4">
          <h3 className="mb-5 font-medium">User · text, attachment, edit</h3>
          <UserMessage />
          <UserMessage attachment />
          <UserMessage editing />
        </div>
        <div className="design-card mb-4">
          <h3 className="mb-5 font-medium">Assistant · complete</h3>
          <AssistantMessage />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {(
            [
              "queued",
              "loading-model",
              "waiting",
              "reasoning",
              "streaming",
              "stopped",
              "error",
              "interrupted",
            ] as AssistantState[]
          ).map((state) => (
            <div className="design-card" key={state}>
              <h3 className="mb-3 font-medium">{state}</h3>
              <AssistantMessage
                state={state}
                text="A partial answer from the Fake runtime. **Formatting stays readable** while the rest arrives."
              />
            </div>
          ))}
        </div>
      </section>
      <section aria-labelledby="composer-states" className="mb-8">
        <h2 id="composer-states" className="mb-4 text-lg font-medium">
          Composer
        </h2>
        <div className="space-y-4">
          <Composer />
          <Composer starter="An editable fixture message" attached reasoning />
          <Composer starter="A fixture message in progress" running />
        </div>
      </section>
      <section aria-labelledby="chat-settings" className="design-card mb-8">
        <h2 id="chat-settings" className="text-lg font-medium">
          Chat settings · model defaults
        </h2>
        <div className="max-w-sm">
          <ChatSettingsPanel />
        </div>
      </section>
      <section aria-labelledby="markdown-safety" className="design-card mb-8">
        <h2 id="markdown-safety" className="mb-4 text-lg font-medium">
          Markdown safety
        </h2>
        <Suspense fallback={<p>Loading example…</p>}>
          <Markdown
            text={
              '[Unsafe link](javascript:alert(1))\n\n![Remote example](https://example.invalid/picture.jpg)\n\n<div data-untrusted="true">Raw HTML fixture</div>'
            }
          />
        </Suspense>
        <p className="mt-4 text-fg-2">
          Remote images appear as links. Raw HTML and unsafe links are disabled.
        </p>
      </section>
      <section aria-labelledby="screens" className="design-card">
        <h2 id="screens" className="mb-4 text-lg font-medium">
          Screen previews
        </h2>
        <div className="flex flex-wrap gap-3">
          <Button asChild variant="outline">
            <Link to="/">New chat</Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/c/fixture">Completed chat</Link>
          </Button>
          <Button variant="outline" onClick={() => ui.set({ settings: true })}>
            Settings dialog
          </Button>
          <Button variant="outline" onClick={() => ui.set({ command: true })}>
            Chat search
          </Button>
        </div>
        <p className="mt-5 text-fg-2">
          Live chat and connections arrive in Phase 1. Web search and citations
          arrive in Phase 2. This foundation does not connect to your library or
          perform web searches.
        </p>
      </section>
    </div>
  );
}
