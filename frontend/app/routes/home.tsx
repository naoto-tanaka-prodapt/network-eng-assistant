import { Link, NavLink } from "react-router";
import { Button } from "~/components/ui/button";
import type { Route } from "../+types/root";

export async function clientLoader({ context }: Route.ClientLoaderArgs) {
  const res = await fetch("/api/health")
  const helloText = await res.json();
  return {helloText}
}

export default function Home({ loaderData }: Route.ClientLoaderArgs) {
    return (
        <main className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center text-center">
            <h1 className="text-3xl font-bold">{loaderData.helloText.status}</h1>
        </main>
    )
}