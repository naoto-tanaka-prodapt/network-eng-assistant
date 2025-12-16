import { useEffect, useMemo, useState } from "react";
import { Form, useNavigation } from "react-router";
import type { Route } from "../+types/root";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";

type PhaseKey = "identify" | "locating" | "analyze" | "action" | "validate";

type MediaHint = "physical" | "switch" | "network" | "unknown";

type IdentifyResponse = {
  facts: string;
  extracted_keywords: string[];
  media_hint: MediaHint;
};

type GuideBasis = {
  start_page: string;
  last_page: string;
  chapter: string;
  note?: string | null;
};

type SafetyCheck = {
  content: string;
  guide_basis: GuideBasis;
};

type LocatingTest = {
  test_content: string;
  purpose: string;
  required_observations: string;
  proceed_constraint: string;
  guide_basis: GuideBasis;
};

type LocatingResponse = {
  safety_checks: SafetyCheck[];
  test_in_order: LocatingTest[];
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
  identify: "/api/identify",
  locating: "/api/locating",
  analyze: "/api/analyze",
  action: "/api/action",
  validate: "/api/conclusion",
};

const isPhaseKey = (value: string): value is PhaseKey =>
  ["identify", "locating", "analyze", "action", "validate"].includes(value);

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
  const [conclusionResult, setConclusionResult] = useState<ConclusionResponse | null>(null);
  const [locatingResponseInput, setLocatingResponseInput] = useState<string>("");
  const [validationChoice, setValidationChoice] = useState<"resolved" | "unresolved" | null>(null);
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
      case "identify":
        setIdentifyResult(actionData.data as IdentifyResponse);
        setLocatingResult(null);
        setAnalysisResult(null);
        setActionResult(null);
        setConclusionResult(null);
        setLocatingResponseInput("");
        setValidationChoice(null);
        break;
      case "locating":
        setLocatingResult(actionData.data as LocatingResponse);
        break;
      case "analyze":
        setAnalysisResult(actionData.data as AnalysisResponse);
        break;
      case "action":
        setActionResult(actionData.data as ActionResponse);
        break;
      case "validate":
        setConclusionResult(actionData.data as ConclusionResponse);
        break;
      default:
        break;
    }
  }, [actionData]);

  const resetSession = () => {
    setSessionId(createSessionId());
    setQuery("");
    setIdentifyResult(null);
    setLocatingResult(null);
    setAnalysisResult(null);
    setActionResult(null);
    setConclusionResult(null);
    setLocatingResponseInput("");
    setValidationChoice(null);
    setErrorMessage(null);
  };

  const restartWithSameSession = () => {
    setIdentifyResult(null);
    setLocatingResult(null);
    setAnalysisResult(null);
    setActionResult(null);
    setConclusionResult(null);
    setLocatingResponseInput("");
    setValidationChoice(null);
    setErrorMessage(null);
  };

  const extractedKeywords = identifyResult?.extracted_keywords ?? [];
  const keywordsForPayload = extractedKeywords.join(", ");

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-md bg-white px-4 py-3 text-sm">
        <div className="flex flex-wrap items-center gap-3 text-muted-foreground">
          {isSubmitting && submittingPhase && (
            <span className="rounded bg-amber-50 px-2 py-1 text-xs text-amber-800">
              {submittingPhase} is running...
            </span>
          )}
          {errorMessage && (
            <span className="rounded bg-destructive/10 px-2 py-1 text-xs text-destructive">{errorMessage}</span>
          )}
        </div>
        <Button variant="default" size="sm" onClick={resetSession} disabled={isSubmitting} className="ml-auto">
          New session
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Step 1. Identify</CardTitle>
          <CardDescription>Interpreting alarms, symptoms, and error reports</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="identify" />
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
              {submittingPhase === "identify" ? "Identifying..." : "Run identify"}
            </Button>
          </Form>

          {identifyResult && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Facts</p>
                <p>{identifyResult.facts}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Extracted keywords</p>
                <div className="flex flex-wrap gap-2">
                  {identifyResult.extracted_keywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="rounded-full bg-white px-2 py-1 text-[11px] font-semibold uppercase text-slate-700"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Category: <span className="font-semibold text-foreground">{identifyResult.media_hint}</span>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 2. Locating</CardTitle>
          <CardDescription>Isolating the fault using tests and narrowing down affected components</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="locating" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="facts" value={identifyResult?.facts ?? ""} />
            <input type="hidden" name="keywords" value={keywordsForPayload} />
            <input type="hidden" name="media_hint" value={identifyResult?.media_hint ?? "unknown"} />
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!identifyResult || isSubmitting || !sessionId}
            >
              {submittingPhase === "locating" ? "Generating checks..." : "Run locating"}
            </Button>
          </Form>

          {locatingResult && (
            <div className="space-y-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Safety checks</p>
                <ul className="space-y-2">
                  {locatingResult.safety_checks.map((item, index) => (
                    <li key={`${item.content}-${index}`} className="rounded bg-white px-2 py-1">
                      <p>{item.content}</p>
                      <p className="text-[11px] text-muted-foreground">
                        {item.guide_basis.chapter} p.{item.guide_basis.start_page}-{item.guide_basis.last_page}
                        {item.guide_basis.note ? ` (${item.guide_basis.note})` : ""}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase text-muted-foreground">Tests in order</p>
                <ol className="space-y-2">
                  {locatingResult.test_in_order.map((item, index) => (
                    <li key={`${item.test_content}-${index}`} className="space-y-2 rounded bg-white px-3 py-3">
                      <div className="space-y-1">
                        <p className="font-semibold">{item.test_content}</p>
                        <p className="text-foreground/80">{item.purpose}</p>
                      </div>
                      <div className="grid gap-2 rounded-md border border-slate-200 bg-slate-50 px-2 py-2 text-sm">
                        <div className="space-y-1">
                          <p className="text-[11px] font-semibold uppercase text-muted-foreground">Required observations</p>
                          <p>{item.required_observations}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[11px] font-semibold uppercase text-muted-foreground">Proceed constraint</p>
                          <p>{item.proceed_constraint}</p>
                        </div>
                      </div>
                      <p className="text-[11px] text-muted-foreground">
                        {item.guide_basis.chapter} p.{item.guide_basis.start_page}-{item.guide_basis.last_page}
                        {item.guide_basis.note ? ` (${item.guide_basis.note})` : ""}
                      </p>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step 3. Analyze</CardTitle>
          <CardDescription>Determining root cause from measurements and system behaviour</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="analyze" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="facts" value={identifyResult?.facts ?? ""} />
            <div className="space-y-2">
              <Label htmlFor="locating_response">Results from locating tests</Label>
              <Textarea
                id="locating_response"
                name="locating_response"
                value={locatingResponseInput}
                onChange={(event) => setLocatingResponseInput(event.target.value)}
                placeholder="Enter what you observed when you ran the locating checks (measurements, behavior, error messages)."
                rows={4}
              />
            </div>
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!locatingResult || !locatingResponseInput.trim() || isSubmitting || !sessionId}
            >
              {submittingPhase === "analyze" ? "Analyzing..." : "Run analyze"}
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
          <CardDescription>Applying fixes and verifying their effectiveness</CardDescription>
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
          <CardTitle>Step 5. Validate & Document</CardTitle>
          <CardDescription>Ensuring no secondary issues remain</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="space-y-2">
              <Label>Select the current state</Label>
              <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
                <label className="flex items-start gap-2">
                  <input
                    type="radio"
                    name="validationChoice"
                    value="resolved"
                    checked={validationChoice === "resolved"}
                    onChange={() => setValidationChoice("resolved")}
                    className="mt-1"
                  />
                  <span>Issue resolved and no secondary impact</span>
                </label>
                <label className="flex items-start gap-2">
                  <input
                    type="radio"
                    name="validationChoice"
                    value="unresolved"
                    checked={validationChoice === "unresolved"}
                    onChange={() => setValidationChoice("unresolved")}
                    className="mt-1"
                  />
                  <span>Unresolved or secondary impact - go back to Step 1 with the same session_id</span>
                </label>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={restartWithSameSession}
                disabled={validationChoice !== "unresolved" || isSubmitting}
              >
                Return to Step 1
              </Button>

              <Form method="post" className="flex flex-wrap gap-3">
                <input type="hidden" name="phase" value="validate" />
                <input type="hidden" name="session_id" value={sessionId} />
                <Button
                  type="submit"
                  variant="default"
                  className="w-full sm:w-fit"
                  disabled={validationChoice !== "resolved" || !actionResult || isSubmitting || !sessionId}
                >
                  {submittingPhase === "validate" ? "Creating doc..." : "Create & save doc"}
                </Button>
              </Form>
            </div>
          </div>

          {conclusionResult && (
            <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-foreground">
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">User feedback</p>
                <p>{conclusionResult.user_feedback}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
