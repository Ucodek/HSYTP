"use client";
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useLocale, useTranslations } from "next-intl";
import { formatValue } from "@/lib/utils/formatters";
import { BacktestingResults } from "@/lib/types"; // Import from centralized types

interface BacktestingChartProps {
  results: BacktestingResults;
}

export function BacktestingChart({ results }: BacktestingChartProps) {
  const locale = useLocale();
  const t = useTranslations("portfolioOptimization.output");

  // Transform data for the chart
  const data = [
    { name: t("backtesting.1year"), value: results["1_year_return"] },
    { name: t("backtesting.3year"), value: results["3_year_return"] },
    { name: t("backtesting.5year"), value: results["5_year_return"] },
  ];

  // Custom tooltip
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-md p-2 shadow-sm">
          <p className="font-medium">{payload[0].payload.name}</p>
          <p>Return: {formatValue(locale, payload[0].value, "percent")}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div
      className="h-[350px] mt-6"
      role="img"
      aria-label="Historical performance bar chart showing returns over different time periods"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12 }}
            height={40}
            tickMargin={10}
          />
          <YAxis
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            width={45}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="value"
            fill="#4f46e5"
            isAnimationActive={false}
            label={{
              position: "top",
              formatter: (value: number) => `${(value * 100).toFixed(1)}%`,
              fill: "#666",
              fontSize: 12,
            }}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
