/**
 * TH1/TH2 · Theme lab. Every palette, both modes, and each palette's motion,
 * drawn with the production components. Open at /design?themes.
 */
import { useEffect, useRef, useState } from "react";
import { AnimatedGreeting } from "@/components/app/AnimatedGreeting";
import { PaletteScene } from "@/components/app/PaletteScene";
import { Sidebar } from "@/components/app/Sidebar";
import { AtelierMark } from "@/components/chat/AtelierMark";
import { Composer } from "@/components/chat/Composer";
import { MessageRow } from "@/components/chat/LiveThread";
import { WorkingLine } from "@/components/chat/WorkingLine";
import { GreetingChoice } from "@/components/settings/PalettePicker";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import type { Message } from "@/lib/api";
import { resolvedAppearance } from "@/lib/appearance";
import {
  PALETTES,
  paletteById,
  paletteIcons,
  type PaletteId,
} from "@/lib/palettes";
import type { ThemePreference } from "@/lib/theme";
import { useFreshRows } from "@/stores/fresh";
import { useUI } from "@/stores/ui";
import { fixtureMessage, fixtureModels } from "./ProductionFixtures";
import "./theme-lab.css";

const SEND_TEXT = "Plan a three-day trip to Lisbon in spring.";
const ANSWER =
  "Lisbon in spring is mild and bright, so plan on foot. **Day 1:** Alfama and the castle at sunset. **Day 2:** Belém in the morning, LX Factory after lunch. **Day 3:** a train to Sintra, back for dinner in Príncipe Real.";

function hex(value: string) {
  return /^#[0-9a-f]{6}$/i.test(value.trim()) ? value.trim() : null;
}
function luminance(color: string) {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const v = parseInt(color.slice(i, i + 2), 16) / 255;
    return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function ratio(a: string, b: string) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Reads the palette tokens an element resolves to, after paint. */
function useTokens(names: string[], deps: unknown[]) {
  const ref = useRef<HTMLDivElement>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      if (!ref.current) return;
      const style = getComputedStyle(ref.current);
      setValues(
        Object.fromEntries(
          names.map((name) => [
            name,
            style.getPropertyValue(`--${name}`).trim(),
          ]),
        ),
      );
    });
    return () => cancelAnimationFrame(frame);
  }, deps);
  return [ref, values] as const;
}

const SWATCH_TOKENS = [
  "bg",
  "surface",
  "user-bubble",
  "text",
  "text-2",
  "brand",
  "brand-fill",
  "on-brand-fill",
];

function PaletteCard({ id, mode }: { id: PaletteId; mode: "light" | "dark" }) {
  const palette = paletteById(id);
  const [ref, tokens] = useTokens(SWATCH_TOKENS, [id, mode]);
  return (
    <div
      ref={ref}
      data-palette={id}
      data-theme={mode}
      className="theme-lab-card"
    >
      <div className="flex items-center gap-3">
        <AtelierMark think />
        <span className="font-medium">{palette.name}</span>
        <span className="ml-auto text-xs capitalize text-fg-3">{mode}</span>
      </div>
      <div className="theme-lab-bubble">How warm is Lisbon in April?</div>
      <p className="theme-lab-answer">
        Usually 15–21 °C, with long dry spells.{" "}
        <span className="text-brand underline underline-offset-2">Source</span>
      </p>
      <div className="flex items-center gap-2">
        <span className="theme-lab-send" aria-hidden="true">
          ↑
        </span>
        <span className="text-xs text-fg-3">
          {palette.words?.slice(0, 3).join(" · ") ??
            "Spelunking · Pondering · Mulling"}
        </span>
      </div>
      <dl className="theme-lab-tokens">
        {SWATCH_TOKENS.map((name) => (
          <div key={name}>
            <dt>
              <span style={{ background: `var(--${name})` }} />
              {name}
            </dt>
            <dd>{tokens[name] ?? ""}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

const CONTRAST_PAIRS: [string, string, number][] = [
  ["text", "bg", 11.8],
  ["text-2", "surface-2", 6.4],
  ["text-3", "surface-2", 4.5],
  ["brand", "bg", 4.7],
  ["on-brand", "brand", 5.5],
  ["on-brand-fill", "brand-fill", 4.5],
  ["brand", "brand-soft", 4.5],
  ["danger", "surface", 4.5],
];

function ContrastPanel({
  palette,
  mode,
}: {
  palette: PaletteId;
  mode: string;
}) {
  const names = [...new Set(CONTRAST_PAIRS.flatMap(([a, b]) => [a, b]))];
  const [ref, tokens] = useTokens(names, [palette, mode]);
  return (
    <div ref={ref} className="design-card min-w-0">
      <h3 className="mb-1 font-medium">Contrast, live</h3>
      <p className="mb-4 text-sm text-fg-2">
        Read from the page as it renders now. The full 57-pair check per mode
        runs in <code>scripts/check_contrast.py</code>.
      </p>
      <table className="w-full text-sm tabular-nums">
        <tbody>
          {CONTRAST_PAIRS.map(([fg, bg, min]) => {
            const a = hex(tokens[fg] ?? ""),
              b = hex(tokens[bg] ?? "");
            const value = a && b ? ratio(a, b) : null;
            return (
              <tr key={fg + bg} className="border-t border-line">
                <td className="py-1.5 pr-3">
                  {fg} on {bg}
                </td>
                <td className="py-1.5 pr-3 text-right">
                  {value ? `${value.toFixed(2)}:1` : "…"}
                </td>
                <td className="py-1.5 text-right text-fg-3">
                  {value && value + 0.001 >= min ? "pass" : value ? "fail" : ""}
                  {` ≥ ${min}`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function rowFor(id: string, role: "user" | "assistant", text: string): Message {
  const message = fixtureMessage(role, "complete", text);
  message.id = id;
  if (role === "assistant") message.reasoning = null;
  return message;
}

export default function ThemesPreview() {
  const ui = useUI();
  const systemDark = useMediaQuery("(prefers-color-scheme: dark)");
  const mode = resolvedAppearance(ui.theme, ui.palette, systemDark);
  const palette = paletteById(ui.palette);
  const [view, setView] = useState<"new" | "thread">("new");
  const [replay, setReplay] = useState(1);
  const [rows, setRows] = useState<Message[]>([
    rowFor("lab-user-0", "user", "How warm is Lisbon in April?"),
    rowFor(
      "lab-assistant-0",
      "assistant",
      "Usually **15–21 °C** in the afternoon, with long dry spells and the odd shower. Bring a light layer for the evenings by the river.",
    ),
  ]);
  const [working, setWorking] = useState<null | {
    began: number;
    kind: "working" | "thinking";
  }>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const thread = useRef<HTMLDivElement>(null);
  // Keep the newest row in view, including when a lazy answer renderer grows it.
  useEffect(() => {
    const el = thread.current;
    const column = el?.firstElementChild;
    if (!el || !column) return;
    const pin = () => el.scrollTo({ top: el.scrollHeight });
    pin();
    const observer = new ResizeObserver(pin);
    observer.observe(column);
    return () => observer.disconnect();
  }, [rows, working, view]);
  useEffect(() => () => timers.current.forEach(clearTimeout), []);
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState("");

  const send = () => {
    setView("thread");
    const n = Date.now();
    const user = rowFor(`lab-user-${n}`, "user", SEND_TEXT);
    useFreshRows.getState().add(user.id);
    setRows((list) => [...list, user]);
    setWorking({ began: Date.now(), kind: "thinking" });
    timers.current.push(
      setTimeout(
        () => setWorking({ began: Date.now(), kind: "working" }),
        2200,
      ),
      setTimeout(() => {
        const answer = rowFor(`lab-assistant-${n}`, "assistant", ANSWER);
        useFreshRows.getState().add(answer.id);
        setWorking(null);
        setRows((list) => [...list, answer]);
      }, 4200),
    );
  };

  return (
    <div className="design-page theme-lab">
      <header className="mb-8">
        <p className="mb-3 text-xs tracking-wide text-fg-3">
          AETHER / THEMES · AERO LOCAL PREVIEW
        </p>
        <h1 className="font-serif text-3xl leading-10">
          Eight palettes, one app.
        </h1>
        <p className="mt-3 max-w-2xl text-fg-2">
          Every surface below is a production component. Pick a palette and a
          mode: the page changes the way the app will, with the palette&apos;s
          own greeting, thinking mark, status words and send motion.
        </p>
        <p className="mt-2 max-w-2xl text-sm text-fg-2">
          Aero is here for visual review. Saved settings and live chat
          integration will follow after review.
        </p>
      </header>

      <section aria-label="Controls" className="theme-lab-controls">
        <div className="flex flex-wrap gap-2" aria-label="Palette">
          {PALETTES.map((p) => (
            <button
              key={p.id}
              type="button"
              className="theme-lab-chip"
              aria-pressed={p.id === ui.palette}
              onClick={() => {
                ui.set({ palette: p.id });
                setReplay((r) => r + 1);
              }}
            >
              <span
                data-palette={p.id}
                data-theme={resolvedAppearance(ui.theme, p.id, systemDark)}
                className="theme-lab-dot"
                aria-hidden="true"
              />
              {p.name}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {(["system", "light", "dark"] as ThemePreference[]).map((theme) => (
            <Button
              key={theme}
              variant={theme === ui.theme ? "default" : "outline"}
              className="min-h-11"
              aria-pressed={theme === ui.theme}
              disabled={!palette.modes.includes("light") && theme !== "dark"}
              onClick={() => ui.set({ theme })}
            >
              {theme[0].toUpperCase() + theme.slice(1)}
            </Button>
          ))}
          <label className="ml-1 flex min-h-11 items-center gap-1 text-sm text-fg-2">
            <Switch
              checked={ui.reduceMotion === "always"}
              onCheckedChange={(on) =>
                ui.set({ reduceMotion: on ? "always" : "system" })
              }
            />
            Reduce motion
          </label>
        </div>
      </section>

      <section aria-label="App preview" className="mb-10">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <Button
            variant={view === "new" ? "secondary" : "outline"}
            aria-pressed={view === "new"}
            onClick={() => {
              setView("new");
              setReplay((r) => r + 1);
            }}
          >
            New chat
          </Button>
          <Button
            variant={view === "thread" ? "secondary" : "outline"}
            aria-pressed={view === "thread"}
            onClick={() => setView("thread")}
          >
            Conversation
          </Button>
          <span className="mx-1 h-6 w-px bg-line" aria-hidden="true" />
          <Button
            variant="outline"
            onClick={() => {
              setView("new");
              setReplay((r) => r + 1);
            }}
          >
            Replay greeting
          </Button>
          <Button onClick={send} disabled={!!working}>
            Send a message
          </Button>
        </div>
        <div className="theme-lab-window">
          <div className="theme-lab-sidebar">
            <Sidebar state="ready" />
          </div>
          <div className="theme-lab-main">
            <div className="theme-lab-topbar">
              <AtelierMark />
              <span className="font-medium">Qwen 3.8 27B · 32K</span>
              <span className="ml-auto text-xs text-fg-3">
                {palette.name} · {mode}
              </span>
            </div>
            {view === "new" ? (
              <section className="empty-chat" aria-label="New chat">
                <PaletteScene />
                <AnimatedGreeting replay={replay} always />
                <Composer model={fixtureModels[0]} suggestions />
                <p className="mt-4 text-center text-xs text-fg-3">
                  Your models. Your Mac.
                </p>
              </section>
            ) : (
              <div className="theme-lab-thread" ref={thread}>
                <div className="thread-column">
                  {rows.map((message) => (
                    <MessageRow
                      key={message.id}
                      message={message}
                      all={[message]}
                      stage="complete"
                      selectedModel={fixtureModels[0]}
                      models={fixtureModels}
                      editing={editing}
                      draft={draft}
                      setEditing={setEditing}
                      setDraft={setDraft}
                      onRegenerate={() => {}}
                      onBranch={() => {}}
                      onEdit={async () => true}
                    />
                  ))}
                  {working && (
                    <WorkingLine
                      id={`lab-${working.began}`}
                      began={working.began}
                      phase={{
                        kind: working.kind,
                        label:
                          working.kind === "thinking" ? "Thinking" : "Writing",
                        announcement: "Working",
                      }}
                    />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <section
        aria-labelledby="lab-motion"
        className="mb-10 grid gap-4 lg:grid-cols-[1.4fr_1fr]"
      >
        <div className="design-card min-w-0">
          <h2 id="lab-motion" className="mb-4 text-lg font-medium">
            Motion personality
          </h2>
          <div
            className="overflow-x-auto"
            role="region"
            aria-label="Theme motion comparison"
            tabIndex={0}
          >
            <table className="w-full text-sm">
              <thead className="text-left text-fg-3">
                <tr>
                  <th className="pb-2 pr-3 font-normal">Palette</th>
                  <th className="pb-2 pr-3 font-normal">Greeting</th>
                  <th className="pb-2 pr-3 font-normal">Thinking mark</th>
                  <th className="pb-2 pr-3 font-normal">Send</th>
                  <th className="pb-2 font-normal">Switch</th>
                </tr>
              </thead>
              <tbody>
                {PALETTES.map((p) => (
                  <tr key={p.id} className="border-t border-line align-top">
                    <td className="py-2 pr-3 font-medium">{p.name}</td>
                    <td className="py-2 pr-3">{MOTION[p.id].greeting}</td>
                    <td className="py-2 pr-3">{MOTION[p.id].mark}</td>
                    <td className="py-2 pr-3">{MOTION[p.id].send}</td>
                    <td className="py-2">
                      {p.reveal === "circle"
                        ? "Circle from the tap"
                        : "Crossfade"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-5">
            <GreetingChoice />
          </div>
        </div>
        <ContrastPanel palette={ui.palette} mode={mode} />
      </section>

      <section aria-labelledby="lab-palettes" className="mb-10">
        <h2 id="lab-palettes" className="mb-1 text-lg font-medium">
          Every palette, both modes
        </h2>
        <p className="mb-4 text-sm text-fg-2">
          Each card sets its own <code>data-palette</code> and{" "}
          <code>data-theme</code>, the same way the Settings swatches do. The
          marks run their thinking loop.
        </p>
        <div className="theme-lab-grid">
          {PALETTES.flatMap((p) =>
            p.modes.map((m) => (
              <PaletteCard key={p.id + m} id={p.id} mode={m} />
            )),
          )}
        </div>
      </section>

      <section aria-labelledby="lab-icons" className="design-card">
        <h2 id="lab-icons" className="mb-1 text-lg font-medium">
          Home Screen icons
        </h2>
        <p className="mb-5 max-w-2xl text-sm text-fg-2">
          Settings points the page&apos;s icon links at the chosen palette. An
          existing Home Screen icon may keep its previous appearance; verify
          icon updates on the actual device.
        </p>
        <div className="flex flex-wrap gap-5">
          {PALETTES.map((p) => (
            <figure key={p.id} className="m-0 text-center">
              <img
                src={paletteIcons(p.id).touch.replace(/^\//, "")}
                alt={`${p.name} icon`}
                width={72}
                height={72}
                className="theme-lab-icon"
                data-current={p.id === ui.palette || undefined}
              />
              <figcaption className="mt-2 text-xs text-fg-2">
                {p.name}
              </figcaption>
            </figure>
          ))}
        </div>
      </section>
    </div>
  );
}

const MOTION: Record<
  PaletteId,
  { greeting: string; mark: string; send: string }
> = {
  cobalt: {
    greeting: "Letters rise in a quick stagger",
    mark: "Dot bobs",
    send: "Lifts 8 px, eased",
  },
  lime: {
    greeting: "Slot-machine roll with a spring",
    mark: "Dot bounces and squashes",
    send: "Pops from 96 % with a spring",
  },
  paper: {
    greeting: "Typewriter with a caret",
    mark: "Ink blot swells; slower draw",
    send: "Settles 2 px, slow ease",
  },
  ember: {
    greeting: "Rises over a warm glow",
    mark: "Glow pulses behind the dot",
    send: "Lifts 10 px",
  },
  orchid: {
    greeting: "Blooms from the middle out",
    mark: "Dot orbits",
    send: "Glides 4 px from 98 %",
  },
  midnight: {
    greeting: "Decodes from scrambled glyphs",
    mark: "Dot twinkles, slow glow",
    send: "Lifts 8 px",
  },
  mono: {
    greeting: "Plain crossfade",
    mark: "Dot fades",
    send: "Quick 4 px, 120 ms",
  },
  aero: {
    greeting: "Glossy letters float up like bubbles",
    mark: "Dot rises as a bubble, with a glow",
    send: "Pops from 94 % with a spring",
  },
};
