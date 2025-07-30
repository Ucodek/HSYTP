import React from "react";
import { Heading, Text } from "../ui/typography";
import { Button } from "../ui/button";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

const BASE_STYLES = {
  wrapper: "p-4 flex-col space-y-4",
  inner: "bg-background",
} as const;

const VARIANT_STYLES = {
  container: {
    wrapper: "container mx-auto",
    inner: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
  },
  card: {
    wrapper:
      "p-6 rounded-xl bg-background border border-border/80 dark:shadow-sm dark:shadow-border/20",
    inner: "space-y-4",
  },
} as const;

interface SectionWrapperProps {
  title?: string;
  subtitle?: string;
  moreText?: string;
  moreLink?: string;
  variant?: "container" | "card";
  wrapperClassName?: string;
  innerClassName?: string;
  disableVariantInnerStyles?: boolean;
  children: React.ReactNode;
}

export const SectionWrapper = React.memo(function SectionWrapper({
  title,
  subtitle,
  moreText,
  moreLink,
  variant = "container",
  wrapperClassName,
  innerClassName,
  disableVariantInnerStyles = false,
  children,
}: SectionWrapperProps) {
  const hasHeader = title || subtitle || (moreText && moreLink);

  // Önemli değişiklik: VARIANT_STYLES'ı asla doğrudan değiştirmeyin
  // Bunun yerine, variantInnerStyle değişkenini kullanın
  const variantInnerStyle = disableVariantInnerStyles
    ? ""
    : VARIANT_STYLES[variant].inner;

  return (
    <section
      className={cn(
        BASE_STYLES.wrapper,
        wrapperClassName,
        VARIANT_STYLES[variant].wrapper
      )}
    >
      {hasHeader && (
        <SectionHeader
          title={title}
          subtitle={subtitle}
          moreText={moreText}
          moreLink={moreLink}
        />
      )}
      <div
        className={cn(
          BASE_STYLES.inner,
          innerClassName,
          variantInnerStyle // Değiştirilmiş kısım burada
        )}
      >
        {children}
      </div>
    </section>
  );
});

const SectionHeader = React.memo(function SectionHeader({
  title,
  subtitle,
  moreText,
  moreLink,
}: {
  title?: string;
  subtitle?: string;
  moreText?: string;
  moreLink?: string;
}) {
  return (
    <div className="flex items-start justify-between">
      <div>
        {title && (
          <Heading level="h3" spacing="none">
            {title}
          </Heading>
        )}

        {subtitle && (
          <Text variant="muted" className="mt-1">
            {subtitle}
          </Text>
        )}
      </div>

      {moreText && moreLink && (
        <Button variant="link" className="gap-1 p-0" asChild>
          <Link href={moreLink} passHref>
            {moreText}
            <ChevronRight size={16} />
          </Link>
        </Button>
      )}
    </div>
  );
});
