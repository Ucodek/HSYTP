import { useTranslations } from "next-intl";
import {
  Hero,
  EconomicEventList,
  MarketOverview,
  NewsList,
  PortfolioOptimizationInput,
  PortfolioOptimizationOutput,
  PostList,
} from "@/components";

export default function PortfolioOptimizationPage() {
  const t = useTranslations("pages.portfolioOptimization");

  return (
    <div>
      {/* 2. PRODUCT/TOOL SHORT DESCRIPTION */}
      <Hero title={t("hero.title")} subtitle={t("hero.subtitle")} />

      {/* 3. MARKET OVERVIEW */}
      <MarketOverview />

      {/* 4. Responsive Two Column Layout */}
      <section className="py-12 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 4.1. Left Column */}
            <div className="space-y-6">
              {/* 4.1.1. PORTFOLIO OPTIMIZATION INPUT AREA */}
              <PortfolioOptimizationInput />

              {/* 4.1.2. PORTFOLIO OPTIMIZATION OUTPUT AREA */}
              <PortfolioOptimizationOutput />
            </div>

            {/* 4.2. Right Column */}
            <div className="space-y-6">
              {/* 4.2.1. IMPORTANT ECONOMIC EVENTS */}
              <EconomicEventList />

              {/* 4.2.2. LATEST NEWS */}
              <NewsList />
            </div>
          </div>
        </div>
      </section>

      {/* 5. MINI CONTENTS, GUIDE-LIKE BLOGS */}
      <PostList />
    </div>
  );
}
