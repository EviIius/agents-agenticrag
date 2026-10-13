import {
  Play,
  Sparkles,
  Split,
  Globe,
  Library,
  FileText,
  AudioLines,
  Eraser,
  ImagePlus,
  GitBranch,
  TextCursorInput,
  UserCheck,
  Star,
  Save,
  StickyNote,
} from "lucide-react";
import type { Block, Kind, Catalog } from "./types";
export const registry = {
  start: {
    label: "Start",
    category: "Inputs",
    tone: "input",
    Icon: Play,
    description: "Define what each run needs.",
  },
  generate: {
    label: "Generate text",
    category: "AI",
    tone: "ai",
    Icon: Sparkles,
    description: "Write with your instructions and a chosen model.",
  },
  classify: {
    label: "Classify",
    category: "AI",
    tone: "ai",
    Icon: Split,
    description: "Choose a category. This block isn’t available yet.",
  },
  web_search: {
    label: "Search the web",
    category: "Knowledge",
    tone: "knowledge",
    Icon: Globe,
    description: "Find sources. This block isn’t available yet.",
  },
  library_search: {
    label: "Search my files",
    category: "Knowledge",
    tone: "knowledge",
    Icon: Library,
    description: "Retrieve your passages. This block isn’t available yet.",
  },
  read_document: {
    label: "Read a document",
    category: "Knowledge",
    tone: "knowledge",
    Icon: FileText,
    description: "Extract document text. This block isn’t available yet.",
  },
  transcribe: {
    label: "Transcribe recording",
    category: "Media",
    tone: "media",
    Icon: AudioLines,
    description: "Keep the original transcript and timestamps.",
  },
  clean_transcript: {
    label: "Clean up transcript",
    category: "Media",
    tone: "media",
    Icon: Eraser,
    description: "Clean up a reading copy; preserve the original.",
  },
  generate_image: {
    label: "Create images",
    category: "Media",
    tone: "media",
    Icon: ImagePlus,
    description: "Create one to three images on your Mac.",
  },
  condition: {
    label: "If / else",
    category: "Logic",
    tone: "logic",
    Icon: GitBranch,
    description: "Branch on a value. This block isn’t available yet.",
  },
  compose: {
    label: "Compose text",
    category: "Logic",
    tone: "logic",
    Icon: TextCursorInput,
    description: "Fill a text template. This block isn’t available yet.",
  },
  review: {
    label: "Approve or edit",
    category: "Review",
    tone: "review",
    Icon: UserCheck,
    description: "Pause for your review before continuing.",
  },
  pick: {
    label: "Pick favorites",
    category: "Review",
    tone: "review",
    Icon: Star,
    description: "Choose results. This block isn’t available yet.",
  },
  output: {
    label: "Save results",
    category: "Output",
    tone: "output",
    Icon: Save,
    description: "Choose the outputs to keep and export.",
  },
  note: {
    label: "Note",
    category: "Notes",
    tone: "logic",
    Icon: StickyNote,
    description: "Add a canvas annotation.",
  },
} as const;
export type CatalogKind = keyof typeof registry;
export const categories = [
  "Inputs",
  "AI",
  "Knowledge",
  "Media",
  "Logic",
  "Review",
  "Output",
];
export function availability(kind: CatalogKind, catalog?: Catalog) {
  if (kind === "note") return { available: true, reason: "" };
  return (
    catalog?.blocks.find((b) => b.kind === kind) ?? {
      available: false,
      reason: registry[kind].description,
    }
  );
}
export function ports(node: Block) {
  return node.kind === "review"
    ? ["approved", "rejected"]
    : node.kind === "output"
      ? []
      : ["out"];
}
export function outputs(node: Block): Record<string, string> {
  if (node.kind === "start")
    return Object.fromEntries(node.config.fields.map((f) => [f.name, f.type]));
  if (node.kind === "generate")
    return {
      text: "text",
      ...Object.fromEntries(
        node.config.json_fields.map((f) => [f.name, f.type]),
      ),
    };
  return {
    transcribe: {
      transcript: "transcript",
      text: "text",
      timestamped_text: "text",
      segments: "json",
      filename: "text",
    },
    clean_transcript: { text: "text" },
    generate_image: { images: "image_list", prompt: "text" },
    review: { value: "text" },
    output: {},
  }[node.kind];
}
export function summary(node: Block, defaultName?: string): string {
  if (node.disabled) return "Disabled · skipped when the workflow runs";
  switch (node.kind) {
    case "start":
      return node.config.fields.length
        ? "Inputs: " + node.config.fields.map((f) => f.label).join(", ")
        : "No inputs";
    case "generate":
      return (
        (node.config.model === "workflow_default"
          ? (defaultName ?? "Workflow default")
          : node.config.model.model_id) +
        (node.config.params.temperature != null
          ? ` · temperature ${node.config.params.temperature}`
          : "") +
        (node.config.format !== "text"
          ? ` · ${node.config.format === "json" ? "JSON" : "Markdown"}`
          : "")
      );
    case "transcribe":
      return node.config.recording || "Choose a recording input";
    case "clean_transcript":
      return (
        "Original kept · " +
        (node.config.model === "workflow_default"
          ? (defaultName ?? "Workflow default")
          : node.config.model.model_id)
      );
    case "generate_image":
      return `${node.config.count} ${node.config.count === 1 ? "image" : "images"} · FLUX.2 klein`;
    case "review":
      return `Review ${node.config.show || "an output"}${node.config.editable ? " · editable" : ""}`;
    case "output":
      return (
        node.config.formats
          .map((f) => (f === "md" ? "Markdown" : "JSON"))
          .join(", ") + ` · ${node.config.include.length} items`
      );
  }
}
export function defaults(kind: Kind): Block["config"] {
  switch (kind) {
    case "start":
      return { fields: [] };
    case "generate":
      return {
        model: "workflow_default",
        instructions: "",
        prompt: "",
        format: "text",
        json_fields: [],
        params: {},
      };
    case "transcribe":
      return { recording: "" };
    case "clean_transcript":
      return { transcript: "", model: "workflow_default" };
    case "generate_image":
      return { prompt: "", count: 1, seeds: "auto" };
    case "review":
      return {
        show: "",
        editable: true,
        message: "Check this result before continuing.",
      };
    case "output":
      return { include: [], formats: ["md", "json"], include_sources: true };
  }
}
