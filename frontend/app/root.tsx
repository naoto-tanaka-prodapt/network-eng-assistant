import { Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router";
import "./app.css"
import { authMiddleware } from "./middleware";

export const clientMiddleware = [authMiddleware]

export default function App() {
  return (
    <html>
      <head>
        <title>Jobify</title>
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}