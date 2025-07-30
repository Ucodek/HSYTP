import { useTranslations } from "next-intl";
import { ChevronDown, ChevronUp } from "lucide-react";
import {
  NavLinkId,
  NavLinkItem,
  getEnabledChildNavLinks,
} from "@/data/navigation";

import {
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuContent,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
  Button,
} from "@/components";
import { Text } from "@/components/ui/typography";

// Common navigation menu item component
const CommonNavigationMenuItem = ({
  link,
  title,
}: {
  link: NavLinkItem;
  title: string;
}) => {
  return (
    <NavigationMenuItem>
      <NavigationMenuLink
        href={link.href}
        className={navigationMenuTriggerStyle()}
      >
        <Text weight="medium" spacing="none">
          {title}
        </Text>
      </NavigationMenuLink>
    </NavigationMenuItem>
  );
};

export const DropdownNavigationMenuLink = ({
  link,
  title,
  description,
}: {
  link: { id: string; href: string };
  title: string;
  description: string;
}) => {
  return (
    <li key={link.href}>
      <NavigationMenuLink href={link.href}>
        <div className="p-2 space-y-1">
          <Text weight="medium" spacing="none">
            {title}
          </Text>
          <Text
            variant="muted"
            weight="normal"
            className="line-clamp-2"
            spacing="none"
          >
            {description}
          </Text>
        </div>
      </NavigationMenuLink>
    </li>
  );
};

export const NavigationMenuItemComponent = ({
  link,
}: {
  link: NavLinkItem;
}) => {
  const tn = useTranslations("navigation");

  // get enabled children links
  const enabledChildren = getEnabledChildNavLinks(link.id as NavLinkId);

  if (!enabledChildren || enabledChildren.length === 0) {
    return <CommonNavigationMenuItem link={link} title={tn(link.id)} />;
  }

  return (
    <NavigationMenuItem>
      <NavigationMenuTrigger aria-label={`${tn(link.id)} menu`}>
        <Text weight="medium" spacing="none">
          {tn(link.id)}
        </Text>
      </NavigationMenuTrigger>
      <NavigationMenuContent>
        <NavigationMenuDropdown items={enabledChildren} />
      </NavigationMenuContent>
    </NavigationMenuItem>
  );
};

interface NavigationMenuDropdownProps {
  items: NavLinkItem[];
  columns?: 1 | 2 | 3;
}

export const NavigationMenuDropdown = ({
  items,
  columns = 2,
}: NavigationMenuDropdownProps) => {
  const t = useTranslations(`navigation.children`);

  if (!items || items.length === 0) return null;

  const dic = {
    1: "grid w-[320px]",
    2: "grid w-[500px] grid-cols-2",
    3: "grid w-[600px] grid-cols-3",
  };

  let listClassName = dic[columns];

  if (items.length === 1) {
    listClassName = dic[1];
  }

  return (
    <ul className={listClassName}>
      {items.map((item) => (
        <DropdownNavigationMenuLink
          key={item.href}
          link={item}
          title={t(`${item.id}.title`)}
          description={t(`${item.id}.description`)}
        />
      ))}
    </ul>
  );
};

export const MobileNavigationMenuItemComponent = ({
  link,
  isOpen,
  onMenuItemClick,
}: {
  link: NavLinkItem;
  isOpen: boolean;
  onMenuItemClick: (href: string) => void;
}) => {
  const tn = useTranslations("navigation");

  // get enabled children links
  const enabledChildren = getEnabledChildNavLinks(link.id as NavLinkId);

  if (!enabledChildren || enabledChildren.length === 0) {
    return <CommonNavigationMenuItem link={link} title={tn(link.id)} />;
  }

  const Icon = isOpen ? ChevronUp : ChevronDown;

  return (
    <NavigationMenuItem>
      <Button
        variant="ghost"
        className={navigationMenuTriggerStyle()}
        onClick={() => onMenuItemClick(link.href)}
        aria-expanded={isOpen}
        aria-label={`${tn(link.id)} menu`}
      >
        <Text weight="medium" spacing="none" className="pl-0.75">
          {tn(link.id)}
        </Text>
        <Icon className="h-4 w-4 ml-2" />
      </Button>

      <MobileSubMenu items={enabledChildren} isOpen={isOpen} />
    </NavigationMenuItem>
  );
};

interface MobileSubMenuProps {
  items: NavLinkItem[];
  isOpen: boolean;
}

export const MobileSubMenu = ({ items, isOpen }: MobileSubMenuProps) => {
  const t = useTranslations(`navigation.children`);

  if (!isOpen) return null;

  return (
    <ul className="grid w-[320px] border-l border-border pl-4 my-4">
      {items.map((item) => (
        <DropdownNavigationMenuLink
          key={item.href}
          link={item}
          title={t(`${item.id}.title`)}
          description={t(`${item.id}.description`)}
        />
      ))}
    </ul>
  );
};
