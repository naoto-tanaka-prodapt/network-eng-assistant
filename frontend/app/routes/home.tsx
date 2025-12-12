import { Form, useNavigation } from "react-router";
import type { Route } from "../+types/root";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";

type Citation = {
  chunk_id: string;
  page_start: number;
  page_end: number;
  section_path: string[];
  part?: string | null;
};

type Step = {
  title: string;
  instruction: string;
  expected_result?: string | null;
  citations?: Citation[];
};

type PhaseName = "identification" | "localization" | "analysis" | "action" | "verification" | string;

type Phase = {
  phase: PhaseName;
  steps: Step[];
};

type SafetyCheck = {
  warning: string;
  risk: "low" | "medium" | "high" | "unknown" | string;
  citations?: Citation[];
};

type TroubleshootingAnswer = {
  issue_summary?: string;
  assumptions?: string[];
  phases?: Phase[];
  safety_checks?: SafetyCheck[];
  not_found?: string[];
};

const PHASE_LABELS: Record<string, string> = {
  identification: "Identification",
  localization: "Localization",
  analysis: "Analysis",
  action: "Action",
  verification: "Verification",
};

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData();
  const query = (formData.get("query") ?? "").toString();

  const response = await fetch("/api/create-procedure", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    return {
      error: "Failed to generate procedure. Please try again.",
      query,
    };
  }

  const data = await response.json();
  return { answer: data.answer, query };
}

export default function Home({ actionData }: Route.ComponentProps) {
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";
  const pendingQuery = navigation.formData?.get("query")?.toString();
  const answer: TroubleshootingAnswer = actionData?.answer ?? {};
  const phases: Phase[] = answer.phases ?? [];
  const safetyChecks: SafetyCheck[] = answer.safety_checks ?? [];
  const assumptions: string[] = answer.assumptions ?? [];
  const notFound: string[] = answer.not_found ?? [];
  const lastQuery = pendingQuery || actionData?.query || "";
  const hasPhaseContent = phases.some((phase) => (phase.steps?.length ?? 0) > 0);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6">
      <Card>
        <CardHeader>
          <CardTitle>Incident intake</CardTitle>
          <CardDescription>Provide whatever the NOC reported.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Form method="post" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="query">Incident details</Label>
              <Textarea
                key={actionData?.query ?? ""}
                id="query"
                name="query"
                placeholder="Include alarms, error messages, symptoms."
                defaultValue={actionData?.query ?? ""}
              />
            </div>
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Generating..." : "Generate workflow"}
            </Button>
          </Form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Generated procedure</CardTitle>
          <CardDescription>
            The backend turns the intake summary into ordered troubleshooting steps.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {lastQuery && (
            <p className="text-xs text-muted-foreground">
              {isSubmitting ? "Submitting:" : "Last query sent:"} {lastQuery}
            </p>
          )}
          {actionData?.error && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {actionData.error}
            </div>
          )}
          {isSubmitting && (
            <p className="text-sm text-muted-foreground">
              Generating procedure with /api/create-procedure...
            </p>
          )}
          {!isSubmitting && !hasPhaseContent && !actionData?.error && (
            <p className="text-sm text-muted-foreground">
              Provide incident details above, then generate to see the suggested sequence of checks and actions.
            </p>
          )}
          {!isSubmitting && answer.issue_summary && (
            <div className="rounded-md border border-amber-100 bg-amber-50 px-3 py-2 text-sm text-amber-900">
              {answer.issue_summary}
            </div>
          )}
          {!isSubmitting && assumptions.length > 0 && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Assumptions</p>
              <ul className="list-disc space-y-1 pl-5 text-sm text-foreground/80">
                {assumptions.map((item, idx) => (
                  <li key={`${idx}-${item}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {!isSubmitting && safetyChecks.length > 0 && (
            <div className="space-y-2 rounded-md border border-red-100 bg-red-50 px-3 py-2">
              <p className="text-xs font-semibold uppercase text-red-800">Safety checks</p>
              <ul className="space-y-2">
                {safetyChecks.map((check, idx) => (
                  <li key={`${idx}-${check.warning}`} className="space-y-1 text-sm text-red-900">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-red-100 px-2 py-0.5 text-[11px] font-semibold uppercase text-red-800">
                        Risk: {check.risk ?? "unknown"}
                      </span>
                      <span className="text-xs text-red-800/80">
                        Citations: {(check.citations ?? []).map((c) => c.chunk_id).join(", ")}
                      </span>
                    </div>
                    <p>{check.warning}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {!isSubmitting && notFound.length > 0 && (
            <div className="space-y-1 rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Not found in manual</p>
              <ul className="list-disc space-y-1 pl-5 text-sm text-foreground/80">
                {notFound.map((item, idx) => (
                  <li key={`${idx}-${item}`}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {hasPhaseContent && (
            <div className="space-y-4">
              {phases.map((phase, phaseIndex) => {
                const readablePhase = PHASE_LABELS[phase.phase?.toLowerCase?.() ?? ""] ?? phase.phase;
                const steps = phase.steps ?? [];

                return (
                  <div
                    key={`${phase.phase}-${phaseIndex}`}
                    className="rounded-lg border border-slate-200 bg-white px-3 py-3 shadow-sm"
                  >
                    <div className="flex items-center gap-3 border-b border-slate-100 pb-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-700">
                        {phaseIndex + 1}
                      </span>
                      <div>
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">Phase</p>
                        <p className="text-base font-semibold text-foreground">
                          {readablePhase || "Phase"}{" "}
                          {readablePhase?.toLowerCase() !== phase.phase?.toLowerCase() && (
                            <span className="text-xs font-normal text-muted-foreground">({phase.phase})</span>
                          )}
                        </p>
                      </div>
                    </div>

                    {steps.length > 0 ? (
                      <ol className="mt-3 space-y-3">
                        {steps.map((step, stepIndex) => (
                          <li
                            key={`${step.title}-${stepIndex}`}
                            className="rounded-md border border-slate-100 bg-slate-50 px-3 py-3"
                          >
                            <div className="flex items-start gap-3">
                              <span className="mt-1 h-6 w-6 shrink-0 rounded-full bg-slate-200 text-center text-xs font-semibold leading-6 text-slate-800">
                                {stepIndex + 1}
                              </span>
                              <div className="space-y-2">
                                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                                  <p className="text-sm font-semibold text-foreground">{step.title}</p>
                                  {step.expected_result && (
                                    <span className="text-xs text-muted-foreground">
                                      Expected: {step.expected_result}
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-foreground/90">{step.instruction}</p>
                                {step.citations && step.citations.length > 0 && (
                                  <div className="flex flex-wrap gap-2 text-[11px] text-muted-foreground">
                                    {step.citations.map((citation, citationIndex) => (
                                      <span
                                        key={`${citation.chunk_id}-${citationIndex}`}
                                        className="rounded-full border border-slate-200 bg-white px-2 py-0.5"
                                      >
                                        {citation.chunk_id}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </li>
                        ))}
                      </ol>
                    ) : (
                      <p className="pt-3 text-sm text-muted-foreground">
                        No steps were retrieved for this phase in the provided context.
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
