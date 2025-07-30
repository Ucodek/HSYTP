import Link from "next/link";
import { TrendingUp, TrendingDown } from "lucide-react";
import { useTranslations, useLocale } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { Text, Heading } from "@/components/ui/typography";
import { cn } from "@/lib/utils";
import { formatValue } from "@/lib/utils/formatters";
import { Stock } from "@/lib/types";
import { Fragment } from "react";
import { TREND_STYLES } from "@/lib/constants";

interface StockCardProps {
  stock: Stock;
  href?: string;
  className?: string;
}

/**
 * Bir hisse senedi bilgisini gösteren kart komponenti
 * Farklı bileşenler ve sayfalarda yeniden kullanılabilir
 */
export function StockCard({ stock, href, className }: StockCardProps) {
  const isPositive = stock.change > 0;
  const trendStyle = isPositive ? TREND_STYLES.positive : TREND_STYLES.negative;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  const locale = useLocale();
  const tc = useTranslations("common");

  const content = (
    <Fragment>
      {/* First row */}
      <div className="flex justify-between items-center gap-3">
        <div className="flex items-center gap-3">
          <Heading level="h5" spacing="none">
            {stock.symbol}
          </Heading>
          <Badge variant="outline">{stock.country}</Badge>
        </div>

        <Heading
          level="h4"
          spacing="none"
          className={cn("flex items-center gap-2", trendStyle.text)}
        >
          <TrendIcon size={16} />
          {formatValue(locale, stock.change_percent / 100, "percentWithSign")}
        </Heading>
      </div>

      {/* Second row */}
      <div className="flex justify-between items-center mt-1">
        <Text
          variant="muted"
          weight="medium"
          spacing="none"
          className="line-clamp-1"
        >
          {stock.name}
        </Text>

        <div className="flex items-center gap-3">
          <Text variant="muted" weight="medium" spacing="none">
            {tc("stocks.volume")}: {formatValue(locale, stock.volume, "volume")}
          </Text>

          <Heading level="h5" spacing="none" className={trendStyle.price}>
            {formatValue(locale, stock.price, "currency", stock.currency)}
          </Heading>
        </div>
      </div>
    </Fragment>
  );

  // Link ile sarmalamak isteğe bağlı
  if (href) {
    return (
      <Link
        href={href}
        className={cn(
          "block hover:bg-muted/50 dark:hover:bg-muted/50 transition-colors p-2 rounded-md",
          className
        )}
      >
        {content}
      </Link>
    );
  }

  // Link olmadan normal div olarak render
  return <div className={cn("p-2 rounded-md", className)}>{content}</div>;
}
