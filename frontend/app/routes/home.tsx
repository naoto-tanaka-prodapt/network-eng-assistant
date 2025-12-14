import { useEffect, useMemo, useState } from "react";
import { Form, useNavigation } from "react-router";
import type { Route } from "../+types/root";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";

type PhaseKey = "identification" | "localization" | "analysis" | "action" | "validation" | "conclusion";

type IdentifyResponse = {
  problem_interpretation: string;
  complaint_type: string;
};

type LocatingCheck = {
  type: "question_to_user" | "procedure" | string;
  check_content: string;
};

type LocatingResponse = {
  checks_in_order: LocatingCheck[];
};

type GuideBasis = {
  start_page: string;
  last_page: string;
  chapter: string;
  note?: string | null;
};

type AnalysisResponse = {
  root_cause: string;
  reasoning: string;
  guide_basis: GuideBasis[];
};

type ActionResponse = {
  fix_steps: string[];
  safety_checks: string[];
  impact_assessment: string;
  rollback_plan: string[];
  guide_basis: GuideBasis[];
};

type ValidateCheck = {
  type: "question_to_user" | "procedure" | string;
  check_content: string;
};

type ValidateResponse = {
  validation_steps: ValidateCheck[];
  guide_basis: GuideBasis[];
};

type ConclusionResponse = {
  symptom: string;
  resolution: string;
  user_feedback: string;
  guide: string;
};

type ClientActionResponse = {
  phase?: PhaseKey;
  data?: unknown;
  error?: string;
};

const PHASE_ENDPOINTS: Record<PhaseKey, string> = {
  identification: "/api/identify",
  localization: "/api/locating",
  analysis: "/api/analyze",
  action: "/api/action",
  validation: "/api/validate",
  conclusion: "/api/conclusion",
};

const isPhaseKey = (value: string): value is PhaseKey =>
  ["identification", "localization", "analysis", "action", "validation", "conclusion"].includes(value);

const createSessionId = () =>
  typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

export async function clientAction({ request }: Route.ClientActionArgs): Promise<ClientActionResponse> {
  const formData = await request.formData();
  const phaseRaw = (formData.get("phase") ?? "").toString();
  const phase = isPhaseKey(phaseRaw) ? phaseRaw : undefined;

  if (!phase) {
    return { error: "Invalid phase was provided. Please try again." };
  }

  const endpoint = PHASE_ENDPOINTS[phase];
  const payload = new FormData();

  formData.forEach((value, key) => {
    if (key === "phase") {
      return;
    }
    if (typeof value === "string") {
      payload.append(key, value);
    } else {
      payload.append(key, value, value.name);
    }
  });

  const response = await fetch(endpoint, { method: "POST", body: payload });
  if (!response.ok) {
    return { error: `Failed to call ${endpoint}.`, phase };
  }

  const data = await response.json();
  return { phase, data };
}

export default function Home({ actionData }: Route.ComponentProps) {
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";
  const submittingPhase = useMemo(
    () => (isSubmitting ? navigation.formData?.get("phase")?.toString() ?? null : null),
    [isSubmitting, navigation.formData],
  );

  const [sessionId, setSessionId] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [identifyResult, setIdentifyResult] = useState<IdentifyResponse | null>(null);
  const [locatingResult, setLocatingResult] = useState<LocatingResponse | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [actionResult, setActionResult] = useState<ActionResponse | null>(null);
  const [validateResult, setValidateResult] = useState<ValidateResponse | null>(null);
  const [conclusionResult, setConclusionResult] = useState<ConclusionResponse | null>(null);
  const [locatingResponseInput, setLocatingResponseInput] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setSessionId(createSessionId());
    }
  }, [sessionId]);

  useEffect(() => {
    if (!actionData) return;

    if (actionData.error) {
      setErrorMessage(actionData.error);
      return;
    }

    setErrorMessage(null);

    if (!actionData.phase) return;

    switch (actionData.phase) {
      case "identification":
        setIdentifyResult(actionData.data as IdentifyResponse);
        setLocatingResult(null);
        setAnalysisResult(null);
        setActionResult(null);
        setValidateResult(null);
        setConclusionResult(null);
        break;
      case "localization":
        setLocatingResult(actionData.data as LocatingResponse);
        break;
      case "analysis":
        setAnalysisResult(actionData.data as AnalysisResponse);
        break;
      case "action":
        setActionResult(actionData.data as ActionResponse);
        break;
      case "validation":
        setValidateResult(actionData.data as ValidateResponse);
        break;
      case "conclusion":
        setConclusionResult(actionData.data as ConclusionResponse);
        break;
      default:
        break;
    }
  }, [actionData]);

  const resetSession = () => {
    setSessionId(createSessionId());
    setIdentifyResult(null);
    setLocatingResult(null);
    setAnalysisResult(null);
    setActionResult(null);
    setValidateResult(null);
    setConclusionResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-3">
          <div>
            <CardTitle>Session</CardTitle>
            <CardDescription>session_id is generated once and reused across phases.</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={resetSession} disabled={isSubmitting}>
            New session
          </Button>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">session_id</span>
            <code className="rounded bg-slate-100 px-2 py-1 text-xs text-foreground">{sessionId}</code>
            {isSubmitting && submittingPhase && (
              <span className="rounded bg-amber-50 px-2 py-1 text-xs text-amber-800">
                {submittingPhase} is running...
              </span>
            )}
            {errorMessage && (
              <span className="rounded bg-destructive/10 px-2 py-1 text-xs text-destructive">{errorMessage}</span>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 1. Identification</CardTitle>
          <CardDescription>Take the raw incident input and turn it into a normalized interpretation.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="identification" />
            <input type="hidden" name="session_id" value={sessionId} />
            <div className="space-y-2">
              <Label htmlFor="query">Incident details</Label>
              <Textarea
                id="query"
                name="query"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Include alarms, error messages, symptoms."
                rows={4}
              />
            </div>
            <Button type="submit" variant="default" className="w-full sm:w-fit" disabled={isSubmitting || !sessionId}>
              {submittingPhase === "identification" ? "Identifying..." : "Run identification"}
            </Button>
          </Form>

          {identifyResult && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Interpretation</p>
              <p className="text-sm text-foreground">{identifyResult.problem_interpretation}</p>
              <p className="text-xs text-muted-foreground">Complaint type: {identifyResult.complaint_type}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 2. Localization</CardTitle>
          <CardDescription>Divide-and-conquer checks to narrow the fault domain.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="localization" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="problem_interpretation" value={identifyResult?.problem_interpretation ?? ""} />
            <input type="hidden" name="complaint_type" value={identifyResult?.complaint_type ?? ""} />
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!identifyResult || isSubmitting || !sessionId}
            >
              {submittingPhase === "localization" ? "Generating checks..." : "Run localization"}
            </Button>
          </Form>

          {locatingResult && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Checks</p>
              <ol className="space-y-2 text-sm text-foreground">
                {locatingResult.checks_in_order.map((check, index) => (
                  <li key={`${check.check_content}-${index}`} className="flex items-start gap-2">
                    <span className="mt-0.5 rounded-full bg-slate-200 px-2 py-0.5 text-[11px] uppercase text-slate-700">
                      {check.type}
                    </span>
                    <span>{check.check_content}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 3. Analysis</CardTitle>
          <CardDescription>Turn observations into a single root cause with guide citations.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="analysis" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="problem_interpretation" value={identifyResult?.problem_interpretation ?? ""} />
            <div className="space-y-2">
              <Label htmlFor="locating_response">Results from localization checks</Label>
              <Textarea
                id="locating_response"
                name="locating_response"
                value={locatingResponseInput}
                onChange={(event) => setLocatingResponseInput(event.target.value)}
                placeholder="Enter what you observed when you ran the localization checks (measurements, behavior, error messages)."
                rows={4}
              />
            </div>
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!locatingResult || !locatingResponseInput.trim() || isSubmitting || !sessionId}
            >
              {submittingPhase === "analysis" ? "Analyzing..." : "Run analysis"}
            </Button>
          </Form>

          {analysisResult && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Root cause</p>
              <p className="font-semibold">{analysisResult.root_cause}</p>
              <p className="text-foreground/80">{analysisResult.reasoning}</p>
              <div className="space-y-1 pt-2">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Guide basis</p>
                <ul className="space-y-1 text-xs">
                  {analysisResult.guide_basis.map((item, index) => (
                    <li key={`${item.chapter}-${index}`} className="rounded bg-white px-2 py-1">
                      {item.chapter} p.{item.start_page}-{item.last_page}
                      {item.note ? ` — ${item.note}` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 4. Action</CardTitle>
          <CardDescription>Safety-first corrective actions with rollback and impact callouts.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="action" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="root_cause" value={analysisResult?.root_cause ?? ""} />
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!analysisResult || isSubmitting || !sessionId}
            >
              {submittingPhase === "action" ? "Preparing fixes..." : "Run action"}
            </Button>
          </Form>

          {actionResult && (
            <div className="space-y-3 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Fix steps</p>
                <ol className="list-decimal space-y-1 pl-5">
                  {actionResult.fix_steps.map((step, index) => (
                    <li key={`${step}-${index}`}>{step}</li>
                  ))}
                </ol>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Safety checks</p>
                <ul className="list-disc space-y-1 pl-5">
                  {actionResult.safety_checks.map((step, index) => (
                    <li key={`${step}-${index}`}>{step}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Impact assessment</p>
                <p>{actionResult.impact_assessment}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Rollback plan</p>
                <ol className="list-decimal space-y-1 pl-5">
                  {actionResult.rollback_plan.map((step, index) => (
                    <li key={`${step}-${index}`}>{step}</li>
                  ))}
                </ol>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Guide basis</p>
                <ul className="space-y-1 text-xs">
                  {actionResult.guide_basis.map((item, index) => (
                    <li key={`${item.chapter}-${index}`} className="rounded bg-white px-2 py-1">
                      {item.chapter} p.{item.start_page}-{item.last_page}
                      {item.note ? ` — ${item.note}` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 5. Validation</CardTitle>
          <CardDescription>Verify resolution and check for secondary issues.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="validation" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="problem_interpretation" value={identifyResult?.problem_interpretation ?? ""} />
            <input type="hidden" name="root_cause" value={analysisResult?.root_cause ?? ""} />
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!actionResult || isSubmitting || !sessionId}
            >
              {submittingPhase === "validation" ? "Validating..." : "Run validation"}
            </Button>
          </Form>

          {validateResult && (
            <div className="space-y-3 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Validation steps</p>
                <ol className="space-y-1">
                  {validateResult.validation_steps.map((item, index) => (
                    <li key={`${item.check_content}-${index}`} className="flex items-start gap-2">
                      <span className="mt-0.5 rounded-full bg-slate-200 px-2 py-0.5 text-[11px] uppercase text-slate-700">
                        {item.type}
                      </span>
                      <span>{item.check_content}</span>
                    </li>
                  ))}
                </ol>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Guide basis</p>
                <ul className="space-y-1 text-xs">
                  {validateResult.guide_basis.map((item, index) => (
                    <li key={`${item.chapter}-${index}`} className="rounded bg-white px-2 py-1">
                      {item.chapter} p.{item.start_page}-{item.last_page}
                      {item.note ? ` — ${item.note}` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 6. Documentation & Feedback</CardTitle>
          <CardDescription>Summarize learnings for reuse and user-facing comms.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="conclusion" />
            <input type="hidden" name="session_id" value={sessionId} />
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!validateResult || isSubmitting || !sessionId}
            >
              {submittingPhase === "conclusion" ? "Documenting..." : "Run conclusion"}
            </Button>
          </Form>

          {conclusionResult && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Symptom signature</p>
                <p>{conclusionResult.symptom}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Resolution</p>
                <p>{conclusionResult.resolution}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">User feedback</p>
                <p>{conclusionResult.user_feedback}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Guide</p>
                <p>{conclusionResult.guide}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
