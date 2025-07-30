"use client";
import React from "react";
import { useTranslations } from "next-intl";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Loader2 } from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { FormBuilder, FormLayoutConfig } from "@/lib/form-builder";
import { useFormAnalytics } from "@/lib/hooks/use-form-analytics";
import { getLogger } from "@/lib/logger";
import { useAuthStore } from "@/lib/stores/auth.store";
import Auth from "@/lib/models/auth.model";
import { useRouter } from "next/navigation";

const logger = getLogger("LoginForm");

// Form schema with validation
const formSchema = z.object({
  username: z
    .string()
    .min(3, { message: "Username must be at least 3 characters" })
    .max(50, { message: "Username must be at most 50 characters" }),
  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters" })
    .max(100, { message: "Password must be at most 100 characters" }),
});

export default function LoginForm() {
  const t = useTranslations("loginForm");
  const router = useRouter();

  // Get state from auth store
  const { loginLoading, error } = useAuthStore();

  // Initialize form with default values
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  // Track form interactions using analytics hook
  useFormAnalytics(form, {
    formId: "login-form",
    trackFieldChanges: true,
    trackSubmissions: true,
    trackErrors: true,
  });

  // Generate form configuration
  const formConfig: FormLayoutConfig = {
    fields: [
      {
        type: "text",
        name: "username",
        label: t("username.label"),
        placeholder: t("username.placeholder"),
        required: true,
        minLength: 3,
        maxLength: 50,
      },
      {
        type: "password",
        name: "password",
        label: t("password.label"),
        placeholder: t("password.placeholder"),
        required: true,
        minLength: 8,
        maxLength: 100,
      },
    ],
    layout: {
      groups: [{ fields: ["username"] }, { fields: ["password"] }],
    },
  };

  // Form submission handler
  async function onSubmit(values: z.infer<typeof formSchema>) {
    logger.info("Starting login with form values", values);

    const tokenResponse = await Auth.login({
      username: values.username,
      password: values.password,
    });

    logger.info("Login successful", tokenResponse.access_token);
    router.push("/"); // Redirect to home or dashboard
  }

  return (
    <SectionWrapper title={t("title")} subtitle={t("subtitle")} variant="card">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormBuilder config={formConfig} form={form} />

          {/* Error message */}
          {error && (
            <div className="p-3 rounded-md bg-destructive/10 text-destructive">
              {error.message || t("errorMessages.unknownError")}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full cursor-pointer"
            disabled={loginLoading}
          >
            {loginLoading && <Loader2 className="animate-spin" />}
            {t("loginButton")}
          </Button>
        </form>
      </Form>
    </SectionWrapper>
  );
}
