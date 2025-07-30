import React from "react";
import { Text } from "@/components/ui/typography";
import { formatValue } from "@/lib/utils/formatters";

type FormatType = "percent" | "number" | "currency";

interface MetricsCardProps {
  label: string;
  value: number;
  format: FormatType;
  locale: string;
  currency?: string;
  className?: string;
}

export function MetricsCard({
  label,
  value,
  format,
  locale,
  currency = "USD",
  className,
}: MetricsCardProps) {
  let formattedValue: string;

  switch (format) {
    case "percent":
      formattedValue = formatValue(locale, value, "percent");
      break;
    case "currency":
      formattedValue = formatValue(locale, value, "currency", currency);
      break;
    default:
      formattedValue = formatValue(locale, value, "number");
  }

  return (
    <div className={`bg-muted/40 p-4 rounded-md ${className}`}>
      <Text variant="muted" spacing="none">
        {label}
      </Text>
      <Text weight="medium" className="text-lg mt-1">
        {formattedValue}
      </Text>
    </div>
  );
}
