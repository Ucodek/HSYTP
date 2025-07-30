import { useTranslations } from "next-intl";

import {
  Hero,
  ProductList,
  SearchBar,
  MarketIndexList,
  EconomicEventList,
  NewsList,
  StockList,
  PostList,
} from "@/components";

export default function Home() {
  const t = useTranslations("pages.home");

  return (
    <div>
      {/* 2. Hero */}
      <Hero
        title={t("hero.title")}
        subtitle={t("hero.subtitle")}
        buttonText={t("hero.buttonText")}
        buttonLink="/login"
        imageUrl="https://images.pexels.com/photos/936722/pexels-photo-936722.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
        altText="Hero Image"
      />
      {/* 3. Products/Tools */}
      <ProductList />
      {/* 4. Search Bar */}
      <section className="py-12 bg-muted/50">
        <div className="container max-w-2xl mx-auto px-4">
          <SearchBar className="bg-background rounded-md" />
        </div>
      </section>
      {/* 5. Stock Market Indices */}
      <MarketIndexList />

      {/* 6. Responsive Two Column Layout */}
      <section className="py-12 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 6.1. Left Column */}
            <div className="space-y-6">
              {/* 6.1.1. Important Economic Events */}
              <EconomicEventList />

              {/* 6.1.2. Latest News */}
              <NewsList />
            </div>

            {/* 6.2. Right Column */}
            <div className="space-y-6">
              {/* 6.2.1. Top Gainer Stocks */}
              <StockList />

              {/* 6.2.2. Top Loser Stocks */}
              <StockList type="losers" />
            </div>
          </div>
        </div>
      </section>

      {/* 7. Mini Contents */}
      <PostList />
    </div>
  );
}
