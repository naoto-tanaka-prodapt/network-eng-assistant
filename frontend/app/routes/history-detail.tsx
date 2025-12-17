import { Link } from "react-router";
import { formatDate } from "~/lib/date-utils"
import type { Route } from "../+types/root";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const res = await fetch(`/api/history/${params.id}`);
  if (!res.ok) {
    throw new Error("Failed to load history detail");
  }
  const history = await res.json();
  return { history };
}

export default function HistoryDetail({ loaderData }: Route.ComponentProps) {

  
  const history = loaderData.history;

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-6 py-10">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase text-muted-foreground">History</p>
          <h1 className="text-xl font-semibold text-foreground">{history.title}</h1>
          <p className="text-xs text-muted-foreground">Created: {formatDate(history.created_at)}</p>
        </div>
        <Link to="/history" className="text-sm font-semibold text-primary hover:underline">
          Back
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Symptom signature</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-foreground">{history.symptom}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resolution</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-foreground">{history.resolution}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>User feedback</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-foreground">{history.user_feedback}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Guide</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-foreground">{history.guide}</p>
        </CardContent>
      </Card>
    </div>
  );
}
