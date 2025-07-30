import { TrendingUp, TrendingDown } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Heading, Text } from "@/components/ui/typography";
import { cn } from "@/lib/utils";
import { formatDateTimeWithTZ, formatValue } from "@/lib/utils/formatters";
import { useLocale } from "next-intl";
import { TREND_STYLES } from "@/lib/constants";
import { InstrumentWithLatestPriceResponse } from "@/lib/types/instrument";

interface IndexCardProps {
  index: InstrumentWithLatestPriceResponse;
  className?: string;
}

export function IndexCard({ index, className }: IndexCardProps) {
  const price = index.price || 0;
  const change = index.change || 0;
  const changePercent = index.change_percent || 0;

  const isPositive = changePercent >= 0;
  const trendStyle = isPositive ? TREND_STYLES.positive : TREND_STYLES.negative;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  const locale = useLocale();

  const lastUpdated = new Date(index.market_timestamp!);
  const formattedLastUpdated = formatDateTimeWithTZ(
    locale,
    lastUpdated,
    "short",
    "short"
  );

  return (
    <Card
      className={cn(
        "p-4 border transition-all hover:shadow-md",
        trendStyle.hover,
        "border-border/40 dark:border-border/80",
        className
      )}
    >
      {/* Header - Name, Symbol, Country */}
      <div className="flex justify-between items-start">
        <div>
          <Heading level="h5" spacing="none" className="truncate max-w-[175px]">
            {index.name}
          </Heading>
          {/* Last Updated Time */}
          <Text
            variant="muted"
            weight="medium"
            spacing="none"
            className={trendStyle.text}
          >
            {formattedLastUpdated}
          </Text>
          <div className="flex items-center gap-3 mt-1">
            <Text variant="muted" weight="medium" spacing="none">
              {index.symbol}
            </Text>
            <Badge variant="outline">{index.country}</Badge>
          </div>
        </div>

        {/* Change Indicator */}
        <div className="flex flex-col items-end">
          <Heading
            level="h4"
            spacing="none"
            className={cn("flex items-center gap-2", trendStyle.text)}
          >
            <TrendIcon size={16} />
            {formatValue(locale, changePercent / 100, "percentWithSign")}
          </Heading>
          <Text
            variant="muted"
            weight="medium"
            spacing="none"
            className={trendStyle.text}
          >
            {formatValue(locale, change, "numberWithSign")}
          </Text>
        </div>
      </div>

      {/* Price Display */}
      <Heading level="h3" spacing="none" className={trendStyle.price}>
        {formatValue(locale, price, "currency", index.currency)}
      </Heading>
    </Card>
  );
}

export function IndexCardSkeleton({ className }: { className?: string }) {
  return (
    <Card
      className={cn(
        "p-4 border animate-pulse bg-muted/40 border-border/40 dark:border-border/80",
        className
      )}
    >
      <div className="flex justify-between items-start">
        <div>
          <div className="h-5 w-32 bg-muted rounded mb-2" />
          {/* Last Updated Time Skeleton */}
          <div className="h-4 w-28 bg-muted rounded mb-2" />
          <div className="flex items-center gap-3 mt-1">
            <div className="h-4 w-16 bg-muted rounded" />
            <div className="h-4 w-10 bg-muted rounded" />
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="h-5 w-20 bg-muted rounded" />
          <div className="h-4 w-12 bg-muted rounded" />
        </div>
      </div>
      <div className="h-8 w-32 bg-muted rounded mt-2" />
    </Card>
  );
}
