import { useTranslations } from "next-intl";
import { NewsCard } from "@/components/ui/news-card";
import { MOCK_NEWS } from "@/lib/mock-data";
import { SectionWrapper } from "@/components/layout/section-wrapper";

export default function NewsList() {
  const t = useTranslations("pages.home.news");
  const tc = useTranslations("common");

  return (
    <SectionWrapper
      title={t("title")}
      variant="card"
      moreText={tc("viewAll")}
      moreLink="/news"
    >
      {MOCK_NEWS.map((article, index) => (
        <NewsCard key={index} article={article} index={index} />
      ))}
    </SectionWrapper>
  );
}
