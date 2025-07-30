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

const logger = getLogger("RegisterForm");

// Form schema with validation
const formSchema = z
  .object({
    email: z.string().email({ message: "Please enter a valid email address" }),
    username: z
      .string()
      .min(3, { message: "Username must be at least 3 characters" })
      .max(50, { message: "Username must be at most 50 characters" }),
    full_name: z.string().optional(),
    password: z
      .string()
      .min(8, { message: "Password must be at least 8 characters" })
      .max(100, { message: "Password must be at most 100 characters" })
      .refine((val) => /[0-9]/.test(val), {
        message: "Password must contain at least one digit",
      })
      .refine((val) => /[A-Z]/.test(val), {
        message: "Password must contain at least one uppercase letter",
      })
      .refine((val) => /[!@#$%^&*(),.?":{}|<>]/.test(val), {
        message: "Password must contain at least one special character",
      }),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export default function RegisterForm() {
  const t = useTranslations("registerForm");
  const router = useRouter();

  // Get state from portfolio store
  const { registerLoading, error } = useAuthStore();

  // Initialize form with default values
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      username: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  });

  // Track form interactions using analytics hook
  useFormAnalytics(form, {
    formId: "register-form",
    trackFieldChanges: true,
    trackSubmissions: true,
    trackErrors: true,
  });

  // Generate form configuration
  const formConfig: FormLayoutConfig = {
    fields: [
      {
        type: "email",
        name: "email",
        label: t("email.label"),
        placeholder: t("email.placeholder"),
        required: true,
      },
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
        type: "text",
        name: "full_name",
        label: t("fullName.label"),
        placeholder: t("fullName.placeholder"),
        required: false,
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
      {
        type: "password",
        name: "confirm_password",
        label: t("confirmPassword.label"),
        placeholder: t("confirmPassword.placeholder"),
        required: true,
      },
    ],
    layout: {
      groups: [
        {
          fields: ["email", "username"],
          className: "grid items-start grid-cols-1 md:grid-cols-2 gap-4",
        },
        { fields: ["full_name"] },
        {
          fields: ["password", "confirm_password"],
          className: "grid items-start grid-cols-1 md:grid-cols-2 gap-4",
        },
      ],
    },
  };

  // Form submission handler
  async function onSubmit(values: z.infer<typeof formSchema>) {
    logger.info("Starting registration with form values", values);

    const registeredUser = await Auth.register({
      email: values.email,
      username: values.username,
      full_name: values.full_name,
      password: values.password,
    });

    router.push("/login");

    logger.info("Registration successful:", registeredUser.email);
  }

  return (
    <SectionWrapper title={t("title")} subtitle={t("subtitle")} variant="card">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormBuilder config={formConfig} form={form} />

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
            disabled={registerLoading}
          >
            {registerLoading && <Loader2 className="animate-spin" />}
            {t("registerButton")}
          </Button>
        </form>
      </Form>
    </SectionWrapper>
  );
}
