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

const PHASES = [
  {
    title: "Identification",
    description: "Capture what is actually happening in the network.",
    steps: [
      "Summarize the reported alarms, symptoms, and timestamps.",
      "Confirm the affected services, regions, or customers.",
      "Flag any immediate safety risks such as power or cooling alerts.",
    ],
  },
  {
    title: "Localization",
    description: "Pinpoint where the problem lives.",
    steps: [
      "Correlate alarms with topology diagrams and recent maintenance.",
      "List the devices, links, or domains that require checks first.",
      "Capture known-good baselines for later comparison.",
    ],
  },
  {
    title: "Analysis",
    description: "Deep-dive diagnostics before making changes.",
    steps: [
      "Execute mandatory health commands in the documented order.",
      "Compare logs, counters, and KPIs against baselines.",
      "Note any prerequisite checks that must pass before actions.",
    ],
  },
  {
    title: "Corrective Action",
    description: "Only after analysis confirms the target component.",
    steps: [
      "List approved fixes and their rollback plan.",
      "Validate change windows and safety controls.",
      "Record the exact CLI or workflow steps to be executed.",
    ],
  },
  {
    title: "Validation & Documentation",
    description: "Prove recovery and capture evidence.",
    steps: [
      "Rerun key diagnostics to confirm service restoration.",
      "Collect screenshots, logs, and ticket updates.",
      "Document lessons learned and follow-up actions.",
    ],
  },
];

export async function clientLoader({ context }: Route.ClientLoaderArgs) {
  const res = await fetch("/api/health");
  const helloText = await res.json();
  return { helloText };
}

export default function Home({ loaderData }: Route.ComponentProps) {
  const [alarmPatterns, setAlarmPatterns] = useState("");
  const [errorMessages, setErrorMessages] = useState("");
  const [symptoms, setSymptoms] = useState("");

  const summary = useMemo(() => {
    const sections = [
      alarmPatterns && `Alarms: ${alarmPatterns}`,
      errorMessages && `Errors: ${errorMessages}`,
      symptoms && `Symptoms: ${symptoms}`,
    ].filter(Boolean);

    if (sections.length === 0) {
      return "Waiting for engineer input.";
    }

    return sections.join(" | ");
  }, [alarmPatterns, errorMessages, symptoms]);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6">
      <section className="flex flex-col gap-3 text-center sm:text-left">
        <p className="text-sm text-muted-foreground">
          Backend status: {loaderData.helloText.status}
        </p>
        <h1 className="text-3xl font-semibold">
          Troubleshooting playbook workspace
        </h1>
        <p className="text-muted-foreground text-base">
          Capture alarms, symptoms, and error details. The assistant keeps them
          structured across the five official troubleshooting phases.
        </p>
      </section>

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
            <Label htmlFor="alarms">Alarm patterns</Label>
            <Textarea
              id="alarms"
              value={alarmPatterns}
              onChange={(event) => setAlarmPatterns(event.target.value)}
              placeholder="Example: Multiple LOS alarms triggered on core switches SW-01 / SW-02 at 12:05 UTC."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="errors">Error messages</Label>
            <Textarea
              id="errors"
              value={errorMessages}
              onChange={(event) => setErrorMessages(event.target.value)}
              placeholder="Paste CLI or syslog excerpts that need to be referenced."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="symptoms">Symptom description</Label>
            <Textarea
              id="symptoms"
              value={symptoms}
              onChange={(event) => setSymptoms(event.target.value)}
              placeholder="e.g. North region customers cannot reach VoIP gateways; packet loss on MPLS PE routers."
            />
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted-foreground">
              Summary draft: {summary}
            </p>
            <Button type="button" variant="default" className="w-full sm:w-fit">
              Generate workflow (coming soon)
            </Button>
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-6 lg:grid-cols-2">
        {PHASES.map((phase) => (
          <Card key={phase.title}>
            <CardHeader>
              <CardTitle>{phase.title}</CardTitle>
              <CardDescription>{phase.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3 text-sm leading-relaxed text-foreground/90">
                {phase.steps.map((step, index) => (
                  <li key={step} className="flex gap-2">
                    <span className="text-muted-foreground">{index + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
              {phase.title === "Identification" && (
                <p className="mt-4 rounded-md border border-dashed border-amber-400 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-900">
                  Safety emphasis: confirm power/environment alarms before
                  touching live equipment.
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Guide references</CardTitle>
          <CardDescription>
            Link back to the source material for traceability.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            All steps follow the official workflow documented in
            TroubleshootingGuide-FrontlineLAN.pdf and the requirements doc in
            <code className="ml-1 rounded bg-muted px-1 py-0.5">
              docs/requirements/requirements-en.md
            </code>
            .
          </p>
          <p>
            A future version will deep-link to the exact section numbers once
            the retrieval pipeline is connected to the vector database.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
