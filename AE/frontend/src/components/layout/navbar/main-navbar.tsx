import { Fragment } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";

import { getEnabledNavLinks } from "@/data/navigation";

import {
  NavigationMenu,
  NavigationMenuList,
  Button,
  ModeToggle,
  LanguageSwitcher,
  NotAuthorizedView,
  AuthorizedView,
} from "@/components";
import { NavigationMenuItemComponent } from "./navigation-components";
import { useAuthStore } from "@/lib/stores/auth.store";
import Auth from "@/lib/models/auth.model";
import { Loader2 } from "lucide-react";

export default function MainNavbar() {
  const ta = useTranslations("auth");

  // Get enabled navigation links from the centralized data source
  const navLinks = getEnabledNavLinks();

  const { logoutLoading } = useAuthStore();

  const handleLogout = async () => {
    // Perform logout logic here
    await Auth.logout();

    // Redirect to the login page
    window.location.href = "/login";
  };

  return (
    <Fragment>
      <NavigationMenu className="hidden lg:flex">
        <NavigationMenuList>
          {navLinks.map((link) => (
            <NavigationMenuItemComponent key={link.href} link={link} />
          ))}
        </NavigationMenuList>
      </NavigationMenu>

      <div className="hidden lg:flex items-center space-x-3">
        <LanguageSwitcher />
        <ModeToggle />
        <NotAuthorizedView>
          <Button variant="outline" asChild>
            <Link href="/login">{ta("login")}</Link>
          </Button>
          <Button asChild>
            <Link href="/signup">{ta("register")}</Link>
          </Button>
        </NotAuthorizedView>

        <AuthorizedView>
          <Button
            onClick={handleLogout}
            className="cursor-pointer"
            variant="outline"
            disabled={logoutLoading}
          >
            {logoutLoading && <Loader2 className="animate-spin" />}
            {ta("logout")}
          </Button>
        </AuthorizedView>
      </div>
    </Fragment>
  );
}
