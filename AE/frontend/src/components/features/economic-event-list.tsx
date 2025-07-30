import { useTranslations } from "next-intl";
import { EconomicEventCard } from "@/components/ui/economic-event-card";
import { MOCK_ECONOMIC_EVENTS } from "@/lib/mock-data";
import { SectionWrapper } from "@/components/layout/section-wrapper";

export default function EconomicEventList() {
  const t = useTranslations("pages.home.economicEvents");
  const tc = useTranslations("common");

  return (
    <SectionWrapper
      title={t("title")}
      variant="card"
      moreText={tc("viewAll")}
      moreLink="/events"
    >
      {MOCK_ECONOMIC_EVENTS.map((event, index) => (
        <EconomicEventCard key={index} event={event} />
      ))}
    </SectionWrapper>
  );
}
