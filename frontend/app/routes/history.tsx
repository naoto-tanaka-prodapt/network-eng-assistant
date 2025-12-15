import { Link, useFetcher } from "react-router";
import type { Route } from "../+types/root";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table";

export async function clientLoader({ context }: Route.ClientLoaderArgs) {
  const res = await fetch(`/api/history`);
  const histories = await res.json();
  return { histories }
}

export default function JobBoards({ loaderData }: Route.ComponentProps) {
  const fetcher = useFetcher()

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <Table className="w-full table-fixed">
          <TableHeader>
            <TableRow className="bg-slate-50">
              <TableHead className="w-24 text-slate-600">symptom</TableHead>
              <TableHead className="w-64 text-slate-600">resolution</TableHead>
              <TableHead className="w-64 text-slate-600">guide</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loaderData.histories.map((history) => (
              <TableRow key={history.id} className="hover:bg-slate-50/80 transition">
                <TableCell className="py-4 whitespace-pre-wrap align-top">{history.symptom}</TableCell>
                <TableCell className="py-4 whitespace-pre-wrap align-top">{history.resolution}</TableCell>
                <TableCell className="py-4 whitespace-pre-wrap align-top">{history.guide}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
