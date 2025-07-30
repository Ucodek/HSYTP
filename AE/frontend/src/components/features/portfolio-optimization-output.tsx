"use client";
import React from "react";
import { useTranslations, useLocale } from "next-intl";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { Heading, Text } from "@/components/ui/typography";
import { Badge } from "@/components/ui/badge";
import { TREND_STYLES } from "@/lib/constants";
import { formatValue } from "@/lib/utils/formatters";
import { TrendingUp, TrendingDown } from "lucide-react";
import { OptimizationResult } from "@/lib/types";
import { MOCK_OPTIMIZATION_RESULT } from "@/lib/mock-data";

// Import our visualization components
import {
  AssetAllocationChart,
  RiskDistributionChart,
  BacktestingChart,
  MetricsCard,
  AssetsTable,
} from "@/components/ui/portfolio";

export default function PortfolioOptimizationOutput() {
  const t = useTranslations("portfolioOptimization.output");
  const locale = useLocale();
  // This could be fetched from your API in a real implementation
  const result: OptimizationResult = MOCK_OPTIMIZATION_RESULT;

  // Determine the strategy name based on the optimization_strategy value
  const getStrategyName = (strategyId: number) => {
    switch (strategyId) {
      case 1:
        return t("strategies.maxReturn");
      case 2:
        return t("strategies.minRisk");
      case 3:
        return t("strategies.sharpeRatio");
      case 4:
        return t("strategies.customWeight");
      default:
        return t("strategies.unknown");
    }
  };

  // Format portfolio metrics
  const expectedReturnFormatted = formatValue(
    locale,
    result.portfolio.expected_return,
    "percent"
  );
  const volatilityFormatted = formatValue(
    locale,
    result.portfolio.volatility,
    "percent"
  );
  const isPositive = result.portfolio.expected_return > 0;
  // const trendIcon = isPositive ? TrendingUp : TrendingDown;
  const trendStyle = isPositive ? TREND_STYLES.positive : TREND_STYLES.negative;

  const TrendIcon = isPositive ? TrendingUp : TrendingDown;

  return (
    <SectionWrapper title={t("title")} subtitle={t("subtitle")} variant="card">
      {/* Portfolio Summary Headline - Improved responsive layout */}
      <div>
        <div className="flex items-center flex-wrap gap-2">
          <Text weight="medium" spacing="none">
            {t("optimizedUsing")}
          </Text>
          <Badge variant="secondary">
            {getStrategyName(result.portfolio.optimization_strategy)}
          </Badge>
        </div>

        <div className="flex items-center flex-wrap gap-2 mt-2">
          <TrendIcon size={20} className={trendStyle.text} aria-hidden="true" />
          <Heading level="h3" spacing="none" className={trendStyle.text}>
            {expectedReturnFormatted} {t("expectedReturn")}
          </Heading>
          <Text variant="muted" spacing="none">
            ({volatilityFormatted} {t("volatility")})
          </Text>
        </div>
      </div>

      {/* Metrics Cards - More responsive grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          label={t("metrics.expectedReturn")}
          value={result.portfolio.expected_return}
          format="percent"
          locale={locale}
        />
        <MetricsCard
          label={t("metrics.volatility")}
          value={result.portfolio.volatility}
          format="percent"
          locale={locale}
        />
        <MetricsCard
          label={t("metrics.sharpeRatio")}
          value={result.portfolio.sharpe_ratio}
          format="number"
          locale={locale}
        />
        <MetricsCard
          label={t("metrics.sortinoRatio")}
          value={result.portfolio.sortino_ratio}
          format="number"
          locale={locale}
        />
      </div>

      <SectionWrapper
        title={t("assetAllocation.title")}
        subtitle={t("assetAllocation.description")}
        variant="card"
      >
        <AssetAllocationChart assets={result.assets} />
      </SectionWrapper>

      <SectionWrapper
        title={t("riskDistribution.title")}
        subtitle={t("riskDistribution.description")}
        variant="card"
      >
        <RiskDistributionChart distribution={result.risk_distribution} />
      </SectionWrapper>

      <SectionWrapper
        title={t("backtesting.title")}
        subtitle={t("backtesting.description")}
        variant="card"
      >
        <BacktestingChart results={result.backtesting_results} />
      </SectionWrapper>

      <SectionWrapper
        title={t("assets.title")}
        subtitle={t("assets.description")}
        variant="card"
      >
        <AssetsTable
          assets={result.assets}
          locale={locale}
          t={t}
          showVolatility={true}
        />
      </SectionWrapper>
    </SectionWrapper>
  );
}
