"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { IndexCard, IndexCardSkeleton } from "@/components/ui/index-card";
import { SectionWrapper } from "@/components/layout/section-wrapper";
// import { formatDateTime } from "@/lib/utils/formatters";
import { useInstrumentStore } from "@/lib/stores/instrument.store";
import Instrument from "@/lib/models/instrument.model";
import { InstrumentType } from "@/lib/types/instrument";

export default function MarketIndexList() {
  const t = useTranslations("pages.home.marketIndices");
  // const locale = useLocale();

  const { instrumentsWithLatestPrice, listWithLatestPriceLoading: isLoading } =
    useInstrumentStore();

  useEffect(() => {
    // Fetch initially
    Instrument.listWithLatestPrice({
      page: 1,
      page_size: 4,
      type: InstrumentType.INDEX,
    });
    // Set up interval to refetch every 15 minutes (900,000 ms)
    const interval = setInterval(() => {
      Instrument.listWithLatestPrice({
        page: 1,
        page_size: 4,
        type: InstrumentType.INDEX,
      });
    }, 1 * 60 * 1000); // 15 minutes
    return () => clearInterval(interval);
  }, []);

  // Son güncellenme zamanını oluştur (gerçek uygulamada API'den gelecektir)
  // const lastUpdated = new Date();
  // const formattedLastUpdated = formatDateTime(
  //   locale,
  //   lastUpdated,
  //   "medium",
  //   "long"
  // );

  const isEmpty = instrumentsWithLatestPrice.length === 0;

  return (
    <SectionWrapper
      title={t("title")}
      // subtitle={formattedLastUpdated}
      subtitle={t("subtitle")}
      wrapperClassName="py-8"
    >
      {isLoading && isEmpty &&
        [1, 2, 3, 4].map((index) => <IndexCardSkeleton key={index} />)}

      {!isLoading && instrumentsWithLatestPrice.map((index) => (
        <Link key={index.symbol} href={`/markets/${index.symbol}`}>
          <IndexCard index={index} />
        </Link>
      ))}
    </SectionWrapper>
  );
}
