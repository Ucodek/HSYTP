import Link from "next/link";
import { useTranslations } from "next-intl";
import { useState } from "react";

import { getEnabledNavLinks } from "@/data/navigation";

import {
  NavigationMenu,
  NavigationMenuList,
  Separator,
  Button,
  ModeToggle,
  LanguageSwitcher,
  NotAuthorizedView,
  AuthorizedView,
} from "@/components";
import { MobileNavigationMenuItemComponent } from "./navigation-components";
import { useAuthStore } from "@/lib/stores/auth.store";
import Auth from "@/lib/models/auth.model";
import { Loader2 } from "lucide-react";

export default function MobileNavbar() {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const ta = useTranslations("auth");

  // Get enabled navigation links from the centralized data source
  const navLinks = getEnabledNavLinks();

  const handleMenuItemClick = (href: string) => {
    setOpenMenu((prevMenu) => (prevMenu === href ? null : href));
  };

  const { logoutLoading } = useAuthStore();

  const handleLogout = async () => {
    // Perform logout logic here
    await Auth.logout();

    // Redirect to the login page
    window.location.href = "/login";
  };

  return (
    <div className="lg:hidden container mx-auto bg-background px-4 pb-3 border-b border-border">
      <NavigationMenu orientation="vertical">
        <NavigationMenuList className="flex-col space-y-1  py-2 items-start">
          {navLinks.map((link) => (
            <MobileNavigationMenuItemComponent
              key={link.href}
              link={link}
              isOpen={openMenu === link.href}
              onMenuItemClick={handleMenuItemClick}
            />
          ))}
        </NavigationMenuList>
      </NavigationMenu>

      <Separator className="my-2" />

      <div className="py-2 flex items-center space-x-3">
        <LanguageSwitcher />
        <ModeToggle />

        <NotAuthorizedView>
          <Button variant="outline" asChild className="flex-1">
            <Link href="/login">{ta("login")}</Link>
          </Button>
          <Button asChild className="flex-1">
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
    </div>
  );
}
