"use client";

import { useState, useEffect, useRef } from "react";
import { Search, X, TrendingUp, BarChart3, Activity } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MOCK_SEARCH_ITEMS, type SearchItem } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { Text } from "./typography";
import { formatValue } from "@/lib/utils/formatters";

interface SearchBarProps {
  placeholder?: string;
  namespace?: string;
  onSearch?: (query: string) => void;
  onSelect?: (item: SearchItem) => void;
  className?: string;
}

export default function SearchBar({
  placeholder,
  namespace = "common.search",
  onSearch,
  onSelect,
  className = "",
}: SearchBarProps) {
  const t = useTranslations(namespace);
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [suggestions, setSuggestions] = useState<SearchItem[]>([]);
  const [activeSuggestion, setActiveSuggestion] = useState(-1);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Use the translated placeholder or default to the translation
  const searchPlaceholder = placeholder || t("placeholder");

  const locale = useLocale();

  // Update suggestions when query changes
  useEffect(() => {
    if (query.trim() === "") {
      setSuggestions([]);
      setShowSuggestions(false);
    } else {
      const filtered = MOCK_SEARCH_ITEMS.filter(
        (item) =>
          item.symbol.toLowerCase().includes(query.toLowerCase()) ||
          item.name.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 4);

      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
      setActiveSuggestion(-1);
    }
  }, [query]);

  useEffect(() => {
    // Close suggestions when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      if (onSearch) onSearch(query);
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Navigation with arrow keys
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveSuggestion((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveSuggestion((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === "Enter" && activeSuggestion >= 0) {
      e.preventDefault();
      selectSuggestion(suggestions[activeSuggestion]);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  const clearSearch = () => {
    setQuery("");
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const selectSuggestion = (item: SearchItem) => {
    setQuery(item.symbol);
    setShowSuggestions(false);
    if (onSelect) onSelect(item);
  };

  const getIconForType = (type: SearchItem["type"]) => {
    switch (type) {
      case "stock":
        return <BarChart3 size={16} className="text-primary" />;
      case "index":
        return <Activity size={16} className="text-green-600" />;
      case "crypto":
        return <TrendingUp size={16} className="text-purple-600" />;
      case "etf":
        return <BarChart3 size={16} className="text-amber-600" />;
    }
  };

  const getChangeColor = (change?: number) => {
    if (!change) return "text-muted-foreground";
    return change > 0 ? "text-green-600" : "text-red-600";
  };

  return (
    <div className={cn("relative w-full", className)} ref={searchRef}>
      <form onSubmit={handleSearch} className="relative flex">
        <div
          className={cn(
            "flex items-center flex-grow border rounded-l-md overflow-hidden transition-all",
            isFocused
              ? "border-primary ring-2 ring-primary/10"
              : "border-input hover:border-input/80"
          )}
        >
          <Search
            size={18}
            className="text-muted-foreground ml-3 mr-1 flex-shrink-0"
          />

          <Input
            ref={inputRef}
            id="search-input"
            type="text"
            className="w-full border-0 shadow-none focus-visible:ring-0"
            placeholder={searchPlaceholder}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              setIsFocused(true);
              if (query.trim() !== "" && suggestions.length > 0) {
                setShowSuggestions(true);
              }
            }}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            autoComplete="off"
          />

          {query && (
            <Button
              type="button"
              variant="ghost"
              // size="sm"
              className="h-auto px-2 mr-1"
              onClick={clearSearch}
              aria-label={t("clear")}
            >
              <X size={16} />
            </Button>
          )}
        </div>

        <Button
          type="submit"
          className="rounded-l-none"
          disabled={!query.trim()}
        >
          {t("button")}
        </Button>
      </form>

      {/* Autocomplete dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-background border border-border rounded-md shadow-lg max-h-64 overflow-y-auto">
          <ul className="py-1 text-base">
            {suggestions.map((item, index) => (
              <li
                key={item.id}
                className={cn(
                  "px-3 py-2 cursor-pointer flex items-center justify-between",
                  index === activeSuggestion
                    ? "bg-accent text-accent-foreground"
                    : "hover:bg-accent/50"
                )}
                onMouseDown={() => selectSuggestion(item)}
                onMouseEnter={() => setActiveSuggestion(index)}
              >
                <div className="flex items-center">
                  <span className="w-5 h-5 flex items-center justify-center mr-2">
                    {getIconForType(item.type)}
                  </span>
                  <div>
                    <Text
                      weight="medium"
                      spacing="none"
                      className="line-clamp-1"
                    >
                      {item.symbol}
                    </Text>
                    <Text
                      variant="muted"
                      spacing="none"
                      className="line-clamp-1"
                    >
                      {item.name}
                    </Text>
                  </div>
                </div>
                {item.price && (
                  <div className="text-right">
                    <Text weight="medium" spacing="none">
                      {formatValue(locale, item.price, "currency")}
                    </Text>
                    {item.change && (
                      <Text
                        spacing="none"
                        className={getChangeColor(item.change)}
                      >
                        {formatValue(
                          locale,
                          item.change / 100,
                          "percentWithSign"
                        )}
                      </Text>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
