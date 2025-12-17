import { Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router";
import "./app.css"

export default function App() {
  return (
    <html>
      <head>
        <title>Network Incident Helper</title>
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