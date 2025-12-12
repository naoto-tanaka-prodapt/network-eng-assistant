import { Link, NavLink, Outlet } from "react-router";
import { cn } from "~/lib/utils";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    "text-sm font-semibold transition-colors hover:text-foreground",
    isActive ? "text-foreground" : "text-muted-foreground"
  );

export default function DefaultLayout() {
  return (
    <div className="min-h-screen bg-muted/20 text-foreground">
      <header className="border-b bg-background">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link
            to="/"
            className="text-base font-semibold tracking-tight text-foreground"
          >
            Network Engineering Assistant
          </Link>
          <nav className="flex items-center gap-4">
            <NavLink to="/" className={navLinkClass}>
              Workspace
            </NavLink>
            <a
              href="https://reactrouter.com/start/framework/installation"
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Framework Docs
            </a>
          </nav>
        </div>
      </header>
      <main className="min-h-[calc(100vh-64px)] bg-muted/20">
        <Outlet />
      </main>
    </div>
  );
}
