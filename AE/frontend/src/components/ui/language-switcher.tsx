"use client";

import { useLocale } from "next-intl";
import { usePathname, useRouter } from "next/navigation";
import { Check, Globe } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const [open, setOpen] = useState(false);
  
  const handleLanguageChange = (selectedLocale: string) => {
    if (selectedLocale === locale) return;
    
    // Strip the locale prefix from the current pathname if it exists
    const pathnameWithoutLocale = pathname ? pathname.replace(`/${locale}`, '') : '';
    
    // Construct the new path with the selected locale
    const newPath = `/${selectedLocale}${pathnameWithoutLocale}`;
    
    router.push(newPath);
    setOpen(false); // Close dropdown after selection
  };
  
  // Define language options
  const languages = [
    { code: 'en', label: 'English' },
    { code: 'tr', label: 'Türkçe' }
  ];
  
  return (
    <DropdownMenu open={open} onOpenChange={setOpen} modal={false}>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="cursor-pointer">
          <Globe className="h-3.5 w-3.5" strokeWidth={1} />
          <span className="uppercase">{locale}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-36" forceMount>
        {languages.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            className={cn(
              "flex justify-between cursor-pointer",
              locale === lang.code && "font-medium"
            )}
          >
            <span>{lang.label}</span>
            {locale === lang.code && (
              <Check className="h-4 w-4" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
