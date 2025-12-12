import { NavLink, Link, Outlet } from "react-router";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
  navigationMenuTriggerStyle,
} from "~/components/ui/navigation-menu";
import { userContext } from "~/context";
import type { Route } from "../+types/root";

export async function clientLoader({ context }: Route.ClientLoaderArgs) {
  // const me = context.get(userContext)
  // const isAdmin = me && me.is_admin
  // return {isAdmin}
}

export default function DefaultLayout( {loaderData}: Route.ComponentProps ) { 
  return (
    <main>        
      <Outlet/>
    </main>
  );
}

 
