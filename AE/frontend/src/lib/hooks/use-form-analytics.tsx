import { useEffect } from "react";
import { FieldValues, UseFormReturn } from "react-hook-form";

type FormAnalyticsConfig = {
  formId: string;
  trackFieldChanges?: boolean;
  trackSubmissions?: boolean;
  trackErrors?: boolean;
};

/**
 * A hook to track form interactions for analytics purposes
 */
export function useFormAnalytics<T extends FieldValues>(
  form: UseFormReturn<T>,
  config: FormAnalyticsConfig
) {
  // Track field changes
  useEffect(() => {
    if (!config.trackFieldChanges) return;

    const subscription = form.watch((value, { name, type }) => {
      if (name && type === "change") {
        // You could send this to your analytics service
        console.log(`[Analytics] Field changed: ${name}`, value);
      }
    });

    return () => subscription.unsubscribe();
  }, [form, config.trackFieldChanges]);

  // Track submissions
  useEffect(() => {
    if (!config.trackSubmissions) return;

    const originalSubmit = form.handleSubmit;

    form.handleSubmit = (onValid, onInvalid) => {
      return originalSubmit((data) => {
        // You could send this to your analytics service
        console.log(`[Analytics] Form submitted: ${config.formId}`, data);
        return onValid(data);
      }, onInvalid);
    };
  }, [form, config.formId, config.trackSubmissions]);

  // Track form errors
  useEffect(() => {
    if (!config.trackErrors) return;

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const subscription = form.watch((value, { name, type }) => {
      if (Object.keys(form.formState.errors).length > 0) {
        // You could send this to your analytics service when errors change
        console.log(
          `[Analytics] Form errors: ${config.formId}`,
          form.formState.errors
        );
      }
    });

    return () => subscription.unsubscribe();
  }, [form, config.formId, config.trackErrors]);
}
