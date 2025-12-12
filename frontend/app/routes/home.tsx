import { Form, useNavigation } from "react-router";
import type { Route } from "../+types/root";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
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
  const steps: ProcedureStep[] = actionData?.answer?.steps ?? [];
  const lastQuery = pendingQuery || actionData?.query || "";

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
          {!isSubmitting && steps.length === 0 && !actionData?.error && (
            <p className="text-sm text-muted-foreground">
              Provide incident details above, then generate to see the suggested sequence of checks and actions.
            </p>
          )}
          {steps.length > 0 && (
            <ol className="space-y-3">
              {steps.map((step, index) => {
                const kindKey = typeof step.kind === "string" ? step.kind.toLowerCase() : "";
                const tone = KIND_STYLES[kindKey] ?? "border-slate-200 bg-slate-50 text-slate-900";
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
