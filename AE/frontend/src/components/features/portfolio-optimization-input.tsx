"use client";
import React from "react";
import { useTranslations } from "next-intl";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Badge } from "@/components/ui/badge";
import { Text } from "@/components/ui/typography";
import {
  TrendingUp,
  BarChart3,
  LineChart,
  Settings,
  Loader2,
} from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { FormBuilder, FormLayoutConfig } from "@/lib/form-builder";
import { useFormAnalytics } from "@/lib/hooks/use-form-analytics";
import { Portfolio } from "@/lib/models/portfolio.model";
import { usePortfolioStore } from "@/lib/stores/portfolio.store";
import { getLogger } from "@/lib/logger";

const logger = getLogger("PortfolioOptimizationInput");

// Form schema with validation (remains unchanged)
const formSchema = z.object({
  exchange: z.string({
    required_error: "Please select a market exchange",
  }),
  portfolio_creation_date: z.date({
    required_error: "Please select a portfolio creation date",
  }),
  training_period_days: z.number().int().min(5).max(365),
  optimization_strategy: z.enum(["1", "2", "3", "4"]), // 1=maxReturn, 2=minRisk, 3=sharpeRatio, 4=customWeight
  number_of_assets: z.number().int().min(1).max(50),
});

export default function PortfolioOptimizationInput() {
  const t = useTranslations("portfolioOptimization.input");

  // Get state from portfolio store
  const { optimizeLoading, error } = usePortfolioStore();

  // Initialize form with default values
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      exchange: "BIST",
      portfolio_creation_date: new Date(),
      training_period_days: 30,
      optimization_strategy: "3", // Default to Sharpe Ratio
      number_of_assets: 5,
    },
  });

  // Track form interactions using analytics hook
  useFormAnalytics(form, {
    formId: "portfolio-optimization-form",
    trackFieldChanges: true,
    trackSubmissions: true,
    trackErrors: true,
  });

  const watchStrategy = form.watch("optimization_strategy");

  // Generate form configuration
  const formConfig: FormLayoutConfig = {
    fields: [
      {
        type: "select",
        name: "exchange",
        label: t("exchange.label"),
        description: t("exchange.description"),
        placeholder: t("exchange.placeholder"),
        options: [
          { value: "BIST", label: "BIST (Borsa Istanbul)" },
          { value: "NASDAQ", label: "NASDAQ (US)" },
          { value: "NYSE", label: "NYSE (US)" },
          { value: "LSE", label: "London Stock Exchange (UK)" },
        ],
      },
      {
        type: "date",
        name: "portfolio_creation_date",
        label: t("portfolioDate.label"),
        description: t("portfolioDate.description"),
        placeholder: t("portfolioDate.placeholder"),
        minDate: new Date("2010-01-01"),
        maxDate: new Date(),
      },
      {
        type: "radioCard",
        name: "optimization_strategy",
        label: t("strategy.label"),
        options: [
          {
            id: "1",
            name: t("strategies.maxReturn.name"),
            description: t("strategies.maxReturn.description"),
            icon: TrendingUp,
          },
          {
            id: "2",
            name: t("strategies.minRisk.name"),
            description: t("strategies.minRisk.description"),
            icon: BarChart3,
          },
          {
            id: "3",
            name: t("strategies.sharpeRatio.name"),
            description: t("strategies.sharpeRatio.description"),
            icon: LineChart,
          },
          {
            id: "4",
            name: t("strategies.customWeight.name"),
            description: t("strategies.customWeight.description"),
            icon: Settings,
          },
        ],
      },
      {
        type: "select",
        name: "training_period_days",
        label: t("trainingPeriod.label"),
        description: t("trainingPeriod.description", {
          days: form.watch("training_period_days"),
        }),
        placeholder: t("trainingPeriod.placeholder"),
        options: [
          { value: "30", label: "30 days" },
          { value: "60", label: "60 days" },
          { value: "90", label: "90 days (3 months)" },
          { value: "120", label: "120 days (4 months)" },
          { value: "180", label: "180 days (6 months)" },
          { value: "365", label: "365 days (1 year)" },
        ],
        onChangeHandler: (value) =>
          form.setValue("training_period_days", parseInt(value)),
      },
      {
        type: "number",
        name: "number_of_assets",
        label: t("numberOfAssets.label"),
        description: t("numberOfAssets.description"),
        min: 1,
        max: 50,
      },
    ],
    layout: {
      groups: [
        {
          fields: ["exchange", "portfolio_creation_date"],
          className: "grid items-start grid-cols-1 md:grid-cols-2 gap-4",
        },
        {
          fields: ["optimization_strategy"],
        },
        {
          fields: ["training_period_days", "number_of_assets"],
          className: "grid items-start grid-cols-1 md:grid-cols-2 gap-4",
        },
      ],
    },
  };

  // Form submission handler
  async function onSubmit(values: z.infer<typeof formSchema>) {
    logger.info("Starting portfolio optimization with form values", values);

    // Use the Portfolio model to optimize
    const optimizedPortfolio = await Portfolio.optimize({
      exchange: values.exchange,
      portfolio_creation_date: values.portfolio_creation_date,
      training_period_days: values.training_period_days,
      optimization_strategy: parseInt(values.optimization_strategy),
      number_of_assets: values.number_of_assets,
    });

    logger.info("Portfolio optimization successful:", optimizedPortfolio.name);
  }

  return (
    <SectionWrapper title={t("title")} subtitle={t("subtitle")} variant="card">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormBuilder config={formConfig} form={form} />

          {/* Custom Weights (Conditional) */}
          {watchStrategy === "4" && (
            <div className="border border-dashed border-primary/50 rounded-md p-4">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-medium">{t("customWeights.title")}</h4>
                <Badge>{t("customWeights.comingSoon")}</Badge>
              </div>
              <Text variant="muted">{t("customWeights.description")}</Text>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="p-3 rounded-md bg-destructive/10 text-destructive">
              {/* Now we can be confident we always have an error message */}
              {error.message || t("errorMessages.unknownError")}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full cursor-pointer"
            disabled={optimizeLoading}
          >
            {optimizeLoading && <Loader2 className="animate-spin" />}
            {t("optimizeButton")}
          </Button>
        </form>
      </Form>
    </SectionWrapper>
  );
}
