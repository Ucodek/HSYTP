import Link from "next/link";
import { ArrowRight, Clock } from "lucide-react";
import { useTranslations, useLocale } from "next-intl";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Text, Heading } from "@/components/ui/typography";
import { timestampToDate, formatDate } from "@/lib/utils/formatters";
import { Post, BadgeVariant } from "@/lib/types";

// Post Card props
interface PostCardProps {
  post: Post;
  index: number;
  variant?: BadgeVariant;
}

/**
 * Bir blog yazısı veya makaleyi gösteren kart bileşeni
 */
export function PostCard({ post, index, variant }: PostCardProps) {
  const tc = useTranslations("common");
  const locale = useLocale();

  // Badge varyantını belirle - variant props'tan gel veya index'e göre hesapla
  const getBadgeVariant = (): BadgeVariant => {
    if (variant) return variant;

    const variants: BadgeVariant[] = [
      "default",
      "secondary",
      "outline",
      "destructive",
    ];
    return variants[index % variants.length];
  };

  // Tarihi formatlama
  const formattedDate = formatDate(
    locale,
    timestampToDate(post.timestamp),
    "medium"
  );

  return (
    <Card className="shadow-none p-0">
      <Link href={post.url} className="p-5 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-3">
          <Badge variant={getBadgeVariant()}>
            {post.category || "General"}
          </Badge>

          <div className="flex items-center gap-2">
            <Clock size={16} className="text-muted-foreground" />
            <Text variant="muted" spacing="none">
              {formattedDate}
            </Text>
          </div>
        </div>

        <Heading level="h5" className="line-clamp-1">
          {post.title}
        </Heading>

        <Text spacing="relaxed" className="line-clamp-2 text-muted-foreground">
          {post.summary}
        </Text>

        <Text
          weight="medium"
          spacing="none"
          className="flex items-center gap-2"
        >
          {tc("insights.readArticle")}
          <ArrowRight size={16} aria-hidden="true" />
        </Text>
      </Link>
    </Card>
  );
}
