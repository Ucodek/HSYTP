import { Calendar, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Text, Heading } from "@/components/ui/typography";
import { cn } from "@/lib/utils";
import {
  formatDate,
  formatTime,
  getImpactVariant,
  timestampToDate,
  formatValue,
} from "@/lib/utils/formatters";
import { useLocale, useTranslations } from "next-intl";
import { EconomicEvent } from "@/lib/types";

type EconomicEventCardProps = {
  event: EconomicEvent;
};

export const EconomicEventCard = function EconomicEventCard({
  event,
}: EconomicEventCardProps) {
  const locale = useLocale();
  const tc = useTranslations("common");
  const eventDate = timestampToDate(event.timestamp);

  const prev =
    event.previous_value !== null
      ? formatValue(locale, event.previous_value, "number") + event.unit
      : "—";

  const fcst =
    event.forecast_value !== null
      ? formatValue(locale, event.forecast_value, "number") + event.unit
      : "—";

  const act =
    event.actual_value !== null
      ? formatValue(locale, event.actual_value, "number") + event.unit
      : "—";

  // get the act value color according to the forecast value
  const actColor =
    event.actual_value !== null && event.forecast_value !== null
      ? event.actual_value > event.forecast_value
        ? "text-green-600 dark:text-green-500"
        : "text-red-600 dark:text-red-500"
      : "";

  return (
    <Card className="shadow-none border-border/60">
      <CardContent>
        <div className="flex items-start gap-2">
          <div className="flex-1">
            {/* Event metadata */}
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-muted-foreground" />
                <Text variant="muted" spacing="none">
                  {formatDate(locale, eventDate, "short")}
                </Text>
              </div>

              <Text variant="muted" spacing="none">
                •
              </Text>

              <div className="flex items-center gap-2">
                <Clock size={16} className="text-muted-foreground" />
                <Text variant="muted" spacing="none">
                  {formatTime(locale, eventDate, "short")}
                </Text>
              </div>

              <Text variant="muted" spacing="none">
                •
              </Text>

              <Badge variant="outline">{event.country}</Badge>
            </div>

            {/* Event title */}
            <Heading level="h5" className="line-clamp-1">
              {event.event}
            </Heading>

            {/* Values */}
            <div className="flex flex-wrap gap-4 mt-2">
              <div className="flex gap-2">
                <Text spacing="none" className="inline text">
                  {tc("economicEvents.previous")}:
                </Text>
                <Text weight="medium" spacing="none" className="inline">
                  {prev}
                </Text>
              </div>

              <div className="flex gap-2">
                <Text spacing="none" className="inline">
                  {tc("economicEvents.forecast")}:
                </Text>
                <Text
                  weight="medium"
                  spacing="none"
                  className="inline text-yellow-600 dark:text-yellow-500"
                >
                  {fcst}
                </Text>
              </div>

              <div className="flex gap-2">
                <Text spacing="none" className="inline">
                  {tc("economicEvents.actual")}:
                </Text>
                <Text
                  weight="medium"
                  spacing="none"
                  className={cn("inline", actColor)}
                >
                  {act}
                </Text>
              </div>
            </div>
          </div>

          {/* Impact badge */}
          <div className="flex justify-end items-start">
            <Badge variant={getImpactVariant(event.impact)}>
              {tc(`economicEvents.impact.${event.impact}`)}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
