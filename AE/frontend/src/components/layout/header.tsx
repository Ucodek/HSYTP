"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";

import { Button, Logo } from "@/components";

import MainNavbar from "./navbar/main-navbar";
import MobileNavbar from "./navbar/mobile-navbar";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 w-full bg-background border-b border-border shadow-sm z-40">
      <div className="container mx-auto px-4 flex items-center justify-between h-16">
        <Logo />
        
        <MainNavbar />

        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden p-0"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
          aria-expanded={isMenuOpen}
        >
          {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </Button>
      </div>

      {isMenuOpen && <MobileNavbar />}
    </header>
  );
}