import {
  Workflow,
  ImagePlus,
  AudioLines,
  Library,
  FileText,
  Sparkles,
  Globe,
  Mail,
  Calendar,
  Star,
  Briefcase,
  Folder,
} from "lucide-react";
import type { Definition } from "./types";
export const workflowIcons = {
  workflow: Workflow,
  image: ImagePlus,
  audio: AudioLines,
  library: Library,
  file: FileText,
  sparkles: Sparkles,
  globe: Globe,
  mail: Mail,
  calendar: Calendar,
  star: Star,
  briefcase: Briefcase,
  folder: Folder,
} satisfies Record<Definition["icon"], typeof Workflow>;
