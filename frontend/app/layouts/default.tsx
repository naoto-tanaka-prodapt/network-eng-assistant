import { Link, Outlet } from "react-router";

export default function DefaultLayout() {
  return (
    <div className="min-h-screen bg-muted/20 text-foreground">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link
            to="/"
            className="text-base font-semibold tracking-tight text-foreground"
          >
            Network Incident Helper
          </Link>
          <Link
            to="/history"
            className="text-base font-semibold tracking-tight text-foreground"
          >
            history
          </Link>
        </div>
      </header>
      <main className="min-h-[calc(100vh-64px)] bg-muted/20">
        <Outlet />
      </main>
    </div>
  );
}
