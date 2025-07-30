import Link from "next/link";
import { Clock, ArrowRight } from "lucide-react";
import { useTranslations, useLocale } from "next-intl";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Text, Heading } from "@/components/ui/typography";
import { formatTimestamp } from "@/lib/utils/formatters";
import { NewsArticle } from "@/lib/types";

interface NewsCardProps {
  article: NewsArticle;
}

/**
 * Bir haber makalesini gösteren kart komponenti
 */
export function NewsCard({ article }: NewsCardProps) {
  // Komponent içindeki gerekli hook'lar
  const locale = useLocale();
  const tc = useTranslations("common");

  // Haber tarihini formatlama
  const formattedDate = formatTimestamp(locale, article.timestamp, "short");

  return (
    <Card className="shadow-none p-0">
      <Link
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="p-5 flex flex-col"
      >
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <Badge variant="secondary">{article.source}</Badge>

          <div className="flex items-center gap-2">
            <Clock size={16} className="text-muted-foreground" />
            <Text variant="muted" spacing="none">
              {formattedDate}
            </Text>
          </div>
        </div>

        <Heading level="h5" className="line-clamp-2">
          {article.title}
        </Heading>

        <Text spacing="relaxed" className="line-clamp-2 text-muted-foreground">
          {article.summary}
        </Text>

        <Text
          weight="medium"
          spacing="none"
          className="flex items-center gap-2"
        >
          {tc("news.readMore")}
          <ArrowRight size={16} aria-hidden="true" />
        </Text>
      </Link>
    </Card>
  );
}
