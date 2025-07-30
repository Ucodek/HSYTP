import { useTranslations } from "next-intl";
import { PostCard } from "@/components/ui/post-card";
import { MOCK_POSTS } from "@/lib/mock-data";
import { SectionWrapper } from "@/components/layout/section-wrapper";

export default function PostList() {
  const t = useTranslations("pages.home.insights");
  const tc = useTranslations("common");

  return (
    <SectionWrapper
      title={t("title")}
      moreText={tc("viewAll")}
      moreLink="/insights"
      wrapperClassName="py-8"
    >
      {MOCK_POSTS.map((post, index) => (
        <PostCard key={index} post={post} index={index} />
      ))}
    </SectionWrapper>
  );
}
