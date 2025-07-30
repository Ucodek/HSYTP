import React from "react";
import { useLocale, useTranslations } from "next-intl";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { formatDateTime } from "@/lib/utils/formatters";
import { StockCard } from "@/components/ui/stock-card";
import { MarketSummary } from "@/components/ui/market-summary";
import { MOCK_BIST100, MOCK_TURKISH_STOCKS } from "@/lib/mock-data";

export default function MarketOverview() {
  const locale = useLocale();
  const t = useTranslations("markets");
  const tPages = useTranslations("pages.market");

  // Last updated time (in real app, this would come from API)
  const lastUpdated = new Date();
  const formattedLastUpdated = formatDateTime(
    locale,
    lastUpdated,
    "medium",
    "short"
  );

  // Split stocks into gainers and losers using the mock data
  const gainers = MOCK_TURKISH_STOCKS.filter((stock) => stock.change > 0).sort(
    (a, b) => b.change_percent - a.change_percent
  );
  const losers = MOCK_TURKISH_STOCKS.filter((stock) => stock.change < 0).sort(
    (a, b) => a.change_percent - b.change_percent
  );

  return (
    <SectionWrapper
      title={tPages("title")}
      subtitle={`${t("lastUpdated")}: ${formattedLastUpdated}`}
      wrapperClassName="py-8"
      innerClassName="grid grid-cols-1 lg:grid-cols-3 gap-6"
      disableVariantInnerStyles
    >
      {/* Column 1: Market Summary (uses the imported mock data) */}
      <MarketSummary market={MOCK_BIST100} />

      {/* Column 2: Top Gainers */}
      <SectionWrapper title={t("topGainers")} variant="card">
        {gainers.map((stock) => (
          <StockCard
            key={stock.symbol}
            stock={stock}
            href={`/stocks/${stock.symbol}`}
          />
        ))}
      </SectionWrapper>

      {/* Column 3: Top Losers */}
      <SectionWrapper title={t("topLosers")} variant="card">
        {losers.map((stock) => (
          <StockCard
            key={stock.symbol}
            stock={stock}
            href={`/stocks/${stock.symbol}`}
          />
        ))}
      </SectionWrapper>
    </SectionWrapper>
  );
}
