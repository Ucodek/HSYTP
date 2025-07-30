import Link from "next/link";
import { ArrowLeft, FileX } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Heading, Text } from "@/components/ui/typography";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export default function NotFound() {
  const t = useTranslations("errors");

  return (
    <div className="container max-w-lg mx-auto flex flex-col items-center justify-center py-16 px-4">
      {/* Enhanced visual error indicator */}
      <div className="relative mb-6">
        <div className="absolute inset-0 bg-primary/5 rounded-full animate-pulse"></div>
        <div className="bg-background dark:bg-muted/10 w-20 h-20 rounded-full flex items-center justify-center z-10 relative border border-primary/20 shadow-sm">
          <FileX size={32} className="text-primary" strokeWidth={1.5} />
        </div>
        <div className="absolute -bottom-1 w-16 h-1.5 bg-primary/10 blur-md rounded-full mx-auto left-0 right-0"></div>
      </div>

      {/* Content Card with improved visual design */}
      <Card className="p-6 w-full border border-border/40 dark:border-border/30 shadow-md overflow-hidden relative">
        {/* Visual accent in the corner */}
        <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 dark:bg-primary/10 rounded-full -translate-y-12 translate-x-12"></div>

        <div className="relative z-10">
          {/* Title with professional styling */}
          <div className="flex flex-col items-center mb-4">
            <div className="text-5xl font-bold text-primary/80 mb-1">404</div>
            <Heading level="h1" className="text-xl">
              {t("notFound.title")}
            </Heading>
          </div>

          {/* Divider for visual structure */}
          <div className="w-16 h-px bg-border mx-auto mb-4"></div>

          {/* Descriptive text */}
          <Text variant="muted" className="mb-6 text-center">
            {t("notFound.description")}
          </Text>

          {/* Action button with hover effect */}
          <Button
            asChild
            variant="default"
            className={cn(
              "w-full transition-all hover:translate-y-[-2px]",
              "bg-gradient-to-r from-primary to-primary/90"
            )}
          >
            <Link href="/" className="flex items-center justify-center">
              <ArrowLeft size={16} className="mr-2" />
              {t("notFound.returnHome")}
            </Link>
          </Button>
        </div>
      </Card>

      {/* Additional context */}
      <Text variant="small" className="text-muted-foreground mt-4 text-center">
        {t("notFound.errorReference")}:{" "}
        <span className="font-mono">{t("notFound.errorCode")}</span>
      </Text>
    </div>
  );
}
