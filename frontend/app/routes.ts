import { layout, prefix, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  layout("layouts/default.tsx", [
    route("/", "routes/home.tsx"),
    route("/history", "routes/history.tsx"),
    route("/history/:id", "routes/history-detail.tsx")
  ])
] satisfies RouteConfig;
