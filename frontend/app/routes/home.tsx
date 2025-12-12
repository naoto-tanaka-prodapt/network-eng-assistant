import { useMemo, useState } from "react";
import type { Route } from "../+types/root";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";

type ProcedureStep = {
  text: string;
  kind: "action" | "check" | "caution" | string;
};

const KIND_STYLES: Record<string, string> = {
  action: "border-blue-100 bg-blue-50 text-blue-900",
  check: "border-emerald-100 bg-emerald-50 text-emerald-900",
  caution: "border-amber-100 bg-amber-50 text-amber-900",
};

export async function clientLoader({ context }: Route.ClientLoaderArgs) {
  const res = await fetch("/api/health");
  const helloText = await res.json();
  return { helloText };
}

export default function Home({ loaderData }: Route.ComponentProps) {
  const [alarmPatterns, setAlarmPatterns] = useState("");
  const [errorMessages, setErrorMessages] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [steps, setSteps] = useState<ProcedureStep[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState("");

  const queryText = useMemo(() => {
    const sections = [
      alarmPatterns && `Alarm patterns: ${alarmPatterns}`,
      errorMessages && `Error messages: ${errorMessages}`,
      symptoms && `Symptoms: ${symptoms}`,
    ].filter(Boolean);

    return sections.join("\n");
  }, [alarmPatterns, errorMessages, symptoms]);

  const summaryText = queryText || "Waiting for engineer input.";

  async function handleGenerate() {
    const trimmed = queryText.trim();

    if (trimmed.length < 3) {
      setError("Add at least a few details before generating.");
      setSteps([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("query", trimmed);

      const response = await fetch("/api/create-procedure", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();
      const rawSteps = data?.answer?.steps;
      const stepsResponse: ProcedureStep[] = Array.isArray(rawSteps)
        ? rawSteps
        : [];
      setSteps(stepsResponse);
      setLastQuery(trimmed);
    } catch (err) {
      const message =
        err instanceof Error
          ? `Unable to generate steps: ${err.message}`
          : "Unable to generate steps right now.";
      setError(message);
      setSteps([]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6">
      <Card>
        <CardHeader>
          <CardTitle>Incident intake</CardTitle>
          <CardDescription>
            Provide whatever the NOC reported. Everything remains local until
            retrieval is wired up.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="errors">Error messages</Label>
            <Textarea
              id="errors"
              value={errorMessages}
              onChange={(event) => setErrorMessages(event.target.value)}
              placeholder="Paste CLI or syslog excerpts that need to be referenced."
            />
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <Button
              type="button"
              variant="default"
              className="w-full sm:w-fit"
              onClick={handleGenerate}
              disabled={isLoading}
            >
              {isLoading ? "Generating..." : "Generate workflow"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Generated procedure</CardTitle>
          <CardDescription>
            The backend turns the intake summary into ordered troubleshooting
            steps. It matches the format expected by the vector search + LLM
            pipeline.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {lastQuery && (
            <p className="text-xs text-muted-foreground">
              Last query sent: {lastQuery}
            </p>
          )}
          {error && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </div>
          )}
          {isLoading && (
            <p className="text-sm text-muted-foreground">
              Generating procedure with /api/create-procedure...
            </p>
          )}
          {!isLoading && steps.length === 0 && !error && (
            <p className="text-sm text-muted-foreground">
              Provide incident details above, then generate to see the suggested
              sequence of checks and actions.
            </p>
          )}
          {steps.length > 0 && (
            <ol className="space-y-3">
              {steps.map((step, index) => {
                const kindKey =
                  typeof step.kind === "string" ? step.kind.toLowerCase() : "";
                const tone =
                  KIND_STYLES[kindKey] ??
                  "border-slate-200 bg-slate-50 text-slate-900";
                const kindLabel =
                  kindKey === "check"
                    ? "Check"
                    : kindKey === "caution"
                      ? "Caution"
                      : "Action";

                return (
                  <li
                    key={`${index}-${step.text}`}
                    className="rounded-md border bg-background px-3 py-3 shadow-sm"
                  >
                    <div className="flex gap-3">
                      <span className="mt-1 h-6 w-6 shrink-0 rounded-full bg-muted text-center text-xs font-semibold leading-6 text-muted-foreground">
                        {index + 1}
                      </span>
                      <div className="flex-1 space-y-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`rounded-full border px-2 py-1 text-xs font-semibold uppercase tracking-wide ${tone}`}
                          >
                            {kindLabel}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Suggested step from the assistant
                          </span>
                        </div>
                        <p className="text-sm leading-relaxed text-foreground/90">
                          {step.text}
                        </p>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
