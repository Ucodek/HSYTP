import { useLocale, useTranslations } from "next-intl";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { formatValue } from "@/lib/utils/formatters";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Heading, Text } from "@/components/ui/typography";
import { Badge } from "@/components/ui/badge";
import { TREND_STYLES } from "@/lib/constants";
import { ExtendedMarketIndex } from "@/lib/types";

interface MarketSummaryProps {
  market: ExtendedMarketIndex;
  className?: string;
}

export function MarketSummary({ market, className }: MarketSummaryProps) {
  const isPositive = market.change_percent >= 0;
  const trendStyle = isPositive ? TREND_STYLES.positive : TREND_STYLES.negative;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  const locale = useLocale();
  const t = useTranslations("markets");

  // Calculate positions for visualization
  // 1. 52-week range calculation
  const yearRange = market["52_w_high_price"] - market["52_w_low_price"];

  // 2. Day range calculation - where it sits within 52-week range
  const dayRangeStart =
    ((market.day_low_price - market["52_w_low_price"]) / yearRange) * 100;
  const dayRangeWidth =
    ((market.day_high_price - market.day_low_price) / yearRange) * 100;

  // 3. Current price calculation - where it sits within day range
  const dayWidth = market.day_high_price - market.day_low_price;
  const currentPricePos =
    ((market.last_price - market.day_low_price) / dayWidth) * 100;

  return (
    <SectionWrapper
      title={market.name}
      variant="card"
      disableVariantInnerStyles
      innerClassName={cn("space-y-4", className)}
    >
      {/* Current Price and Trend */}
      <div className="flex items-center justify-between">
        <div>
          <Text variant="muted" weight="medium" spacing="none">
            {market.symbol}
          </Text>
          <Heading level="h3" spacing="none" className={trendStyle.price}>
            {formatValue(
              locale,
              market.last_price,
              "currency",
              market.currency
            )}
          </Heading>
        </div>

        <div className="flex flex-col items-end">
          <Heading
            level="h4"
            spacing="none"
            className={cn("flex items-center gap-2", trendStyle.text)}
          >
            <TrendIcon size={16} />
            {formatValue(
              locale,
              market.change_percent / 100,
              "percentWithSign"
            )}
          </Heading>
          <Text
            variant="muted"
            weight="medium"
            spacing="none"
            className={trendStyle.text}
          >
            {formatValue(locale, market.change, "numberWithSign")}
          </Text>
        </div>
      </div>

      {/* Market Stats Grid */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-3 pt-3 border-t border-border">
        <div>
          <Text variant="muted" spacing="none">
            {t("previousClose")}
          </Text>
          <Text weight="medium" spacing="none">
            {formatValue(
              locale,
              market.previous_close,
              "currency",
              market.currency
            )}
          </Text>
        </div>

        <div>
          <Text variant="muted" spacing="none">
            {t("volume")}
          </Text>
          <Text weight="medium" spacing="none">
            {formatValue(locale, market.volume, "volume")}
          </Text>
        </div>

        <div>
          <Text variant="muted" spacing="none">
            {t("dayRange")}
          </Text>
          <Text weight="medium" spacing="none">
            {formatValue(
              locale,
              market.day_low_price,
              "currency",
              market.currency
            )}
            {" - "}
            {formatValue(
              locale,
              market.day_high_price,
              "currency",
              market.currency
            )}
          </Text>
        </div>

        <div>
          <Text variant="muted" spacing="none">
            {t("52wRange")}
          </Text>
          <Text weight="medium" spacing="none">
            {formatValue(
              locale,
              market["52_w_low_price"],
              "currency",
              market.currency
            )}
            {" - "}
            {formatValue(
              locale,
              market["52_w_high_price"],
              "currency",
              market.currency
            )}
          </Text>
        </div>
      </div>

      {/* Market Performance Visualization */}
      <div className="pt-3 border-t border-border">
        <Text variant="muted" spacing="none">
          {t("todaysPerformance")}
        </Text>

        {/* Visualization Bar */}
        <div className="h-2 bg-muted rounded-full mt-2">
          {/* 52 Week Range */}

          {/* Day Range */}
          <div
            className="bg-border h-2 rounded-full"
            style={{
              width: `${dayRangeWidth}%`,
              marginLeft: `${dayRangeStart}%`,
            }}
          >
            {/* Current Price */}
            <div
              className={cn("h-2 w-2 rounded-full", trendStyle.bg)}
              style={{
                marginLeft: `${currentPricePos}%`,
              }}
            />
          </div>
        </div>

        <div className="flex justify-between mt-1">
          <Text variant="muted" spacing="none">
            {formatValue(
              locale,
              market["52_w_low_price"],
              "currency",
              market.currency
            )}
          </Text>
          <Text variant="muted" spacing="none">
            {formatValue(
              locale,
              market["52_w_high_price"],
              "currency",
              market.currency
            )}
          </Text>
        </div>
      </div>

      {/* Country and Currency Info */}
      <div className="flex justify-between items-center pt-3 border-t border-border">
        <Badge variant="outline">{market.country}</Badge>
        <Badge variant="outline">{market.currency}</Badge>
      </div>
    </SectionWrapper>
  );
}
