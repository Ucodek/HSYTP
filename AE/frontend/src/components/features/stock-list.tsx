import { useTranslations, useLocale } from "next-intl";
import { StockCard } from "@/components/ui/stock-card";
import {
  MOCK_TOP_GAINERS,
  MOCK_TOP_LOSERS,
  MOCK_MOST_ACTIVE,
} from "@/lib/mock-data";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { formatDateTime } from "@/lib/utils/formatters";

type StockListProps = {
  type?: "gainers" | "losers" | "active";
};

export default function StockList({ type = "gainers" }: StockListProps) {
  const t = useTranslations("pages.home.topStocks");
  const tc = useTranslations("common");
  const locale = useLocale();

  // Get default title based on type
  const title = t(type);

  // Son güncellenme zamanını oluştur (gerçek uygulamada API'den gelecektir)
  const lastUpdated = new Date();
  const formattedLastUpdated = formatDateTime(
    locale,
    lastUpdated,
    "medium",
    "long"
  );

  // Organize stocks data by type
  const stocks = {
    gainers: MOCK_TOP_GAINERS,
    losers: MOCK_TOP_LOSERS,
    active: MOCK_MOST_ACTIVE,
  };

  // Define link routes for each stock type
  const links = {
    gainers: "/stocks/gainers",
    losers: "/stocks/losers",
    active: "/stocks/active",
  };

  return (
    <SectionWrapper
      title={title}
      subtitle={formattedLastUpdated}
      variant="card"
      moreText={tc("viewAll")}
      moreLink={links[type]}
    >
      {stocks[type].map((stock) => (
        <StockCard
          key={stock.symbol}
          stock={stock}
          href={`/stocks/${stock.symbol}`}
        />
      ))}
    </SectionWrapper>
  );
}
