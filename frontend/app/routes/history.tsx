import { Link } from "react-router";
import type { Route } from "../+types/root";

type HistoryListItem = {
  id: number;
  title: string;
  created_at: string;
};

export async function clientLoader({ context }: Route.ClientLoaderArgs) {
  const res = await fetch(`/api/history`);
  const histories = await res.json();
  return { histories: histories as HistoryListItem[] };
}

export default function HistoryList({ loaderData }: Route.ComponentProps) {
  const formatDate = (value: string) =>
    new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">History</h1>
        <p className="text-sm text-muted-foreground">{loaderData.histories.length} records</p>
      </div>

      <div className="divide-y divide-slate-200 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {loaderData.histories.map((history) => (
          <Link
            key={history.id}
            to={`/history/${history.id}`}
            className="flex items-center justify-between px-4 py-3 hover:bg-slate-50"
          >
            <div className="space-y-1">
              <p className="text-sm font-semibold text-foreground">{history.title}</p>
              <p className="text-xs text-muted-foreground">{formatDate(history.created_at)}</p>
            </div>
            <span className="text-xs font-semibold uppercase text-muted-foreground">View</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
