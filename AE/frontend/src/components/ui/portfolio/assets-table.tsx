"use client";
import React from "react";
import { formatValue } from "@/lib/utils/formatters";
import { Asset } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { Text, Heading } from "@/components/ui/typography";

interface AssetsTableProps {
  assets: Asset[];
  locale: string;
  // Translation function from the parent component
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  t: any;
  showVolatility?: boolean;
  className?: string;
}

export function AssetsTable({
  assets,
  locale,
  t,
  showVolatility = false,
  className,
}: AssetsTableProps) {
  return (
    <div className={className}>
      <Table>
        <TableCaption className="sr-only">{t("assets.title")}</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>
              <Heading
                level="h6"
                spacing="none"
                className="text-muted-foreground"
              >
                {t("assets.symbol")}
              </Heading>
            </TableHead>
            <TableHead>
              <Heading
                level="h6"
                spacing="none"
                className="text-muted-foreground"
              >
                {t("assets.name")}
              </Heading>
            </TableHead>
            <TableHead className="text-right">
              <Heading
                level="h6"
                spacing="none"
                className="text-muted-foreground"
              >
                {t("assets.weight")}
              </Heading>
            </TableHead>
            <TableHead className="text-right">
              <Heading
                level="h6"
                spacing="none"
                className="text-muted-foreground"
              >
                {t("assets.expectedReturn")}
              </Heading>
            </TableHead>
            {showVolatility && (
              <TableHead className="text-right">
                <Heading
                  level="h6"
                  spacing="none"
                  className="text-muted-foreground"
                >
                  {t("assets.volatility")}
                </Heading>
              </TableHead>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {assets.map((asset) => (
            <TableRow key={asset.symbol}>
              <TableCell>
                <Text weight="medium" spacing="none">
                  {asset.symbol}
                </Text>
              </TableCell>
              <TableCell>
                <Text spacing="none">{asset.name}</Text>
              </TableCell>
              <TableCell className="text-right">
                <Text weight="medium" spacing="none">
                  {formatValue(locale, asset.weight, "percent")}
                </Text>
              </TableCell>
              <TableCell className="text-right">
                <Text weight="medium" spacing="none">
                  {formatValue(locale, asset.expected_return, "percent")}
                </Text>
              </TableCell>
              {showVolatility && asset.volatility !== undefined && (
                <TableCell className="text-right">
                  <Text weight="medium" spacing="none">
                    {formatValue(locale, asset.volatility, "percent")}
                  </Text>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
