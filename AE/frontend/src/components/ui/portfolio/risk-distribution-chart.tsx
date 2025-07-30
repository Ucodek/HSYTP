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
  Cell,
} from "recharts";
import { useLocale } from "next-intl";
import { formatValue } from "@/lib/utils/formatters";
import { RiskDistribution } from "@/lib/types"; // Import from centralized types

interface RiskDistributionChartProps {
  distribution: RiskDistribution[];
}

// Risk level colors - increasing warmth with risk
const getRiskColor = (score: number) => {
  if (score < 0.3) return "#4ade80"; // Low risk - green
  if (score < 0.6) return "#facc15"; // Medium risk - yellow
  return "#ef4444"; // High risk - red
};

export function RiskDistributionChart({
  distribution,
}: RiskDistributionChartProps) {
  const locale = useLocale();

  // Sort by risk score descending
  const sortedData = [...distribution].sort(
    (a, b) => b.risk_score - a.risk_score
  );

  // Custom tooltip for the chart
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;

      return (
        <div className="bg-background border rounded-md p-2 shadow-sm">
          <p className="font-medium">{data.symbol}</p>
          <p>Allocation: {formatValue(locale, data.percentage, "percent")}</p>
          <p>Risk Score: {formatValue(locale, data.risk_score, "percent")}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div
      className="h-[350px] mt-6"
      role="img"
      aria-label="Risk distribution bar chart showing risk by asset"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={sortedData}
          margin={{ top: 20, right: 10, left: 10, bottom: 30 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="symbol"
            tick={{ fontSize: 12 }}
            interval={0}
            height={40}
            tickMargin={10}
          />
          <YAxis
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            domain={[0, 1]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="risk_score" name="Risk Score" isAnimationActive={false}>
            {sortedData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getRiskColor(entry.risk_score)}
                aria-label={`${entry.symbol}: risk score ${(
                  entry.risk_score * 100
                ).toFixed(0)}%`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
