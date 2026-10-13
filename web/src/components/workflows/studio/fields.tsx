import { useId, type ReactNode } from "react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
export function TextField({
  label,
  value,
  onChange,
  help,
  ...props
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  help?: string;
} & Omit<React.ComponentProps<typeof Input>, "onChange" | "value">) {
  const id = useId();
  return (
    <div className="wf-field">
      <label htmlFor={id}>{label}</label>
      <Input
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        {...props}
      />
      {help && <p className="wf-help">{help}</p>}
    </div>
  );
}
export function Choice({
  label,
  value,
  choices,
  onChange,
  help,
  placeholder = "Choose…",
  disabled = false,
}: {
  label: string;
  value: string;
  choices: { value: string; label: string; disabled?: boolean }[];
  onChange: (v: string) => void;
  help?: string;
  placeholder?: string;
  disabled?: boolean;
}) {
  return (
    <div className="wf-field">
      <span className="wf-label">{label}</span>
      <Select
        value={value || undefined}
        onValueChange={onChange}
        disabled={disabled}
      >
        <SelectTrigger aria-label={label} className="w-full">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {choices.map((c) => (
            <SelectItem key={c.value} value={c.value} disabled={c.disabled}>
              {c.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {help && <p className="wf-help">{help}</p>}
    </div>
  );
}
export function Toggle({
  label,
  checked,
  onChange,
  help,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  help?: string;
}) {
  const id = useId();
  return (
    <div className="wf-field">
      <div className="flex items-center justify-between gap-3">
        <label htmlFor={id}>{label}</label>
        <Switch id={id} checked={checked} onCheckedChange={onChange} />
      </div>
      {help && <p className="wf-help">{help}</p>}
    </div>
  );
}
export function Segments({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: [string, string][];
  onChange: (v: string) => void;
}) {
  return (
    <div className="wf-field">
      <span className="wf-label">{label}</span>
      <div className="wf-segments" role="group" aria-label={label}>
        {options.map(([id, name]) => (
          <Button
            key={id}
            variant="ghost"
            aria-pressed={id === value}
            onClick={() => onChange(id)}
          >
            {name}
          </Button>
        ))}
      </div>
    </div>
  );
}
export function Advanced({
  title = "Advanced",
  children,
}: {
  title?: string;
  children: ReactNode;
}) {
  return (
    <details className="wf-advanced">
      <summary>{title}</summary>
      <div className="wf-field-stack">{children}</div>
    </details>
  );
}
