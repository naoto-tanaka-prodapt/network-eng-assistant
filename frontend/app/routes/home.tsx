import { useEffect, useRef, useState } from "react";
import { Form, useNavigation } from "react-router";
import type { Route } from "../+types/root";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";

const PHASE_ENDPOINTS = {
  identify: "/api/identify",
  locating: "/api/locating",
  analyze: "/api/analyze",
  action: "/api/action",
  validate: "/api/conclusion",
};

const createSessionId = () => crypto.randomUUID();

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData();
  const phase = formData.get("phase");
  const endpoint = PHASE_ENDPOINTS[phase];
  const payload = new FormData();

  formData.forEach((value, key) => {
    if (key === "phase") return;
    payload.append(key, value);
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

  const submittingPhase = isSubmitting ? navigation.formData?.get("phase") ?? null : null;

  const [sessionId, setSessionId] = useState(() => createSessionId());
  const [query, setQuery] = useState("");
  const [identifyResult, setIdentifyResult] = useState(null);
  const [locatingResult, setLocatingResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [actionResult, setActionResult] = useState(null);
  const [conclusionResult, setConclusionResult] = useState(null);
  const [locatingResponseInput, setLocatingResponseInput] = useState("");
  const step1Ref = useRef(null);

  useEffect(() => {
    if (!actionData) return;
    if (!actionData.phase) return;

    switch (actionData.phase) {
      case "identify":
        setIdentifyResult(actionData.data);
        setLocatingResult(null);
        setAnalysisResult(null);
        setActionResult(null);
        setConclusionResult(null);
        setLocatingResponseInput("");
        break;
      case "locating":
        setLocatingResult(actionData.data);
        break;
      case "analyze":
        setAnalysisResult(actionData.data);
        break;
      case "action":
        setActionResult(actionData.data);
        break;
      case "validate":
        setConclusionResult(actionData.data);
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
  };

  const scrollToStep1 = () => {
    step1Ref.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const extractedKeywords = identifyResult?.extracted_keywords ?? [];
  const keywordsForPayload = extractedKeywords.join(", ");

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6">
      <div className="flex flex-wrap items-start justify-between">
        <Button variant="default" size="sm" onClick={resetSession} disabled={isSubmitting} className="ml-auto">
          New session
        </Button>
      </div>

      <div ref={step1Ref}>
        <Card>
          <CardHeader>
            <CardTitle>Step 1. Identify</CardTitle>
            <CardDescription>Interpreting alarms, symptoms, and error reports</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
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
                {submittingPhase === "identify" ? "Running..." : "Run identify"}
              </Button>
            </Form>

            {identifyResult && (
              <div className="space-y-3 rounded-xl border border-slate-200/70 bg-white/80 p-4 text-sm text-foreground shadow-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Facts</p>
                </div>
                <p className="leading-6 text-slate-800">{identifyResult.facts}</p>
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Extracted keywords</p>
                  <div className="flex flex-wrap gap-2">
                    {identifyResult.extracted_keywords.map((keyword) => (
                      <span
                        key={keyword}
                        className="rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-[11px] font-semibold uppercase text-indigo-800 shadow-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Category</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-full bg-indigo-100 text-indigo-800 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide">
                      {identifyResult.media_hint}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Step 2. Locating</CardTitle>
          <CardDescription>Isolating the fault using tests and narrowing down affected components</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
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
              {submittingPhase === "locating" ? "Running..." : "Run locating"}
            </Button>
          </Form>

          {locatingResult && (
            <div className="space-y-5 rounded-xl border border-slate-200/70 bg-white/90 p-4 text-sm text-foreground shadow-sm">
              <div className="space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Safety checks</p>
                <ul className="space-y-3">
                  {locatingResult.safety_checks.map((item, index) => (
                    <li
                      key={`${item.content}-${index}`}
                      className="space-y-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-semibold uppercase tracking-wide text-amber-800">
                          Check {index + 1}
                        </span>
                      </div>
                      <p className="leading-6 text-amber-900">{item.content}</p>
                      <div className="flex flex-wrap gap-2 pt-1">
                        <span className="rounded-md bg-amber-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-amber-900">
                          {item.guide_basis.chapter} p.{item.guide_basis.start_page}-{item.guide_basis.last_page}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Tests in order</p>
                <ol className="space-y-3">
                  {locatingResult.test_in_order.map((item, index) => (
                    <li
                      key={`${item.test_content}-${index}`}
                      className="space-y-3 rounded-xl border border-slate-200 bg-slate-50/80 px-4 py-3 shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="rounded-full bg-slate-900 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-white">
                          Step {index + 1}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <p className="font-semibold leading-6 text-slate-900">{item.test_content}</p>
                      </div>
                      <div className="grid gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                        <div className="space-y-1">
                          <p className="text-[11px] font-semibold uppercase tracking-wide text-indigo-500">Purpose</p>
                          <p className="leading-6 text-slate-800">{item.purpose}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[11px] font-semibold uppercase tracking-wide text-indigo-500">Required observations</p>
                          <p className="leading-6 text-slate-800">{item.required_observations}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[11px] font-semibold uppercase tracking-wide text-indigo-500">Proceed constraint</p>
                          <p className="leading-6 text-slate-800">{item.proceed_constraint}</p>
                        </div>
                      </div>
                      <span className="rounded-md font-semibold text-[11px] border border-indigo-100 bg-indigo-50 px-3 py-1">
                        {item.guide_basis.chapter} p.{item.guide_basis.start_page}-{item.guide_basis.last_page}
                      </span>
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
        <CardContent className="space-y-5">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="analyze" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="facts" value={identifyResult?.facts ?? ""} />
            <input type="hidden" name="media_hint" value={identifyResult?.media_hint ?? "unknown"} />
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
              {submittingPhase === "analyze" ? "Running..." : "Run analyze"}
            </Button>
          </Form>

          {analysisResult && (
            <div className="space-y-3 rounded-xl border border-slate-200/70 bg-white/90 p-4 text-sm text-foreground shadow-sm">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Root cause</p>
              <p className="text-base font-semibold leading-6 text-slate-900">{analysisResult.root_cause}</p>
              <p className="leading-6 text-foreground/80">{analysisResult.reasoning}</p>
              <div className="space-y-2 pt-1">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Guide basis</p>
                <ul className="flex flex-wrap gap-2 text-xs">
                  {analysisResult.guide_basis.map((item, index) => (
                    <li key={`${item.chapter}-${index}`} className="rounded-md font-semibold text-[11px] border border-indigo-100 bg-indigo-50 px-3 py-1">
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
        <CardContent className="space-y-5">
          <Form method="post" className="space-y-3">
            <input type="hidden" name="phase" value="action" />
            <input type="hidden" name="session_id" value={sessionId} />
            <input type="hidden" name="root_cause" value={analysisResult?.root_cause ?? ""} />
            <input type="hidden" name="media_hint" value={identifyResult?.media_hint ?? "unknown"} />
            <Button
              type="submit"
              variant="default"
              className="w-full sm:w-fit"
              disabled={!analysisResult || isSubmitting || !sessionId}
            >
              {submittingPhase === "action" ? "Running..." : "Run action"}
            </Button>
          </Form>

          {actionResult && (
            <div className="space-y-4 rounded-xl border border-slate-200/70 bg-white/90 p-4 text-sm text-foreground shadow-sm">
              <div className="space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Safety checks</p>
                <ul className="space-y-3">
                  {actionResult.safety_checks.map((step, index) => (
                    <li
                      key={`${step}-${index}`}
                      className="space-y-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-amber-900 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-semibold uppercase tracking-wide text-amber-800">
                          Check {index + 1}
                        </span>
                      </div>
                      <p className="leading-6">{step}</p>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Fix steps</p>
                <ol className="space-y-3">
                  {actionResult.fix_steps.map((step, index) => (
                    <li
                      key={`${step}-${index}`}
                      className="space-y-2 rounded-xl border border-slate-200 bg-slate-50/80 px-4 py-3 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <p className="rounded-full bg-slate-900 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-white">
                          Step {index + 1}
                        </p>
                      </div>
                      <p className="leading-6 text-slate-900">{step}</p>
                    </li>
                  ))}
                </ol>
              </div>
              <div className="space-y-2">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Guide basis</p>
                <ul className="flex flex-wrap gap-2 text-xs">
                  {actionResult.guide_basis.map((item, index) => (
                    <li key={`${item.chapter}-${index}`} className="rounded-md font-semibold text-[11px] border border-indigo-100 bg-indigo-50 px-3 py-1">
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
        <CardContent className="space-y-5">
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button
                type="button"
                variant="outline"
                onClick={scrollToStep1}
                disabled={!actionResult || isSubmitting || !sessionId}
                className="h-auto w-full flex-1 flex-col items-start justify-start px-4 py-3 text-left"
              >
                <span className="block text-sm font-semibold text-slate-900">Secondary impact detected</span>
                <span className="block text-xs text-slate-600">Return to Step 1 with the same session_id</span>
              </Button>

              <Form method="post" className="w-full flex-1">
                <input type="hidden" name="phase" value="validate" />
                <input type="hidden" name="session_id" value={sessionId} />
                <Button
                  type="submit"
                  variant="default"
                  className="h-auto w-full flex-1 flex-col items-start justify-start px-4 py-3 text-left"
                  disabled={!actionResult || isSubmitting || !sessionId}
                >
                  <span className="block text-sm font-semibold text-white">No secondary impact</span>
                  <span className="block text-xs text-white/80">Create & save doc</span>
                </Button>
              </Form>
            </div>

          {conclusionResult && (
            <div className="space-y-2 rounded-xl border border-slate-200/70 bg-white/90 p-4 text-sm text-foreground shadow-sm">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Copy below for User feedback</p>
                <p className="leading-6 text-slate-900">{conclusionResult.user_feedback}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
