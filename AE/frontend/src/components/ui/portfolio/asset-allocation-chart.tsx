"use client";
import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { useLocale } from "next-intl";
import { formatValue } from "@/lib/utils/formatters";
import { Asset } from "@/lib/types"; // Import from centralized types

interface AssetAllocationChartProps {
  assets: Asset[];
}

// Chart colors
const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#82ca9d",
];

export function AssetAllocationChart({ assets }: AssetAllocationChartProps) {
  const locale = useLocale();

  // Transform data for the chart
  const data = assets.map((asset, index) => ({
    name: asset.symbol,
    value: asset.weight,
    color: COLORS[index % COLORS.length],
  }));

  // Custom tooltip for the chart
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const asset = assets.find((a) => a.symbol === data.name);
      if (!asset) return null;

      return (
        <div className="bg-background border rounded-md p-2 shadow-sm">
          <p className="font-medium">
            {asset.name} ({asset.symbol})
          </p>
          <p>Weight: {formatValue(locale, asset.weight, "percent")}</p>
          <p>
            Expected Return:{" "}
            {formatValue(locale, asset.expected_return, "percent")}
          </p>
          <p>Volatility: {formatValue(locale, asset.volatility, "percent")}</p>
        </div>
      );
    }
    return null;
  };

  // Custom rendering function for labels that handles overflow
  const renderCustomizedLabel = ({
    name,
    percent,
  }: {
    name: string;
    percent: number;
  }) => {
    return `${name} ${(percent * 100).toFixed(0)}%`;
  };

  return (
    <div
      className="h-[350px] mt-6"
      role="img"
      aria-label="Asset allocation pie chart showing portfolio distribution"
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            label={renderCustomizedLabel}
            isAnimationActive={false} // Helps with initial accessibility
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color}
                aria-label={`${entry.name}: ${(entry.value * 100).toFixed(0)}%`}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend layout="horizontal" verticalAlign="bottom" align="center" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
