import React from "react";
import { UseFormReturn } from "react-hook-form";
import {
  SelectField,
  NumberField,
  DateField,
  RadioCardField,
  TextField,
  EmailField,
  PasswordField,
} from "@/components/ui/form-fields";

// Define field types
export type FieldType =
  | "select"
  | "number"
  | "date"
  | "radioCard"
  | "email"
  | "text"
  | "password";

// Base field configuration
interface BaseFieldConfig {
  type: FieldType;
  name: string;
  label: string;
  description?: string;
  className?: string;
  required?: boolean;
}

// Specific field configurations
interface SelectFieldConfig extends BaseFieldConfig {
  type: "select";
  placeholder: string;
  options: { value: string; label: string }[];
  onChangeHandler?: (value: string) => void;
}

interface NumberFieldConfig extends BaseFieldConfig {
  type: "number";
  min?: number;
  max?: number;
  step?: number;
}

interface DateFieldConfig extends BaseFieldConfig {
  type: "date";
  placeholder: string;
  minDate?: Date;
  maxDate?: Date;
}

interface RadioCardFieldConfig extends BaseFieldConfig {
  type: "radioCard";
  options: {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
  }[];
}

interface TextFieldConfig extends BaseFieldConfig {
  type: "text" | "email" | "password";
  placeholder?: string;
  minLength?: number;
  maxLength?: number;
}

// Union type of all field configurations
export type FieldConfig =
  | SelectFieldConfig
  | NumberFieldConfig
  | DateFieldConfig
  | RadioCardFieldConfig
  | TextFieldConfig;

// Form layout configuration
export interface FormLayoutConfig {
  fields: FieldConfig[];
  layout?: {
    groups: {
      fields: string[]; // Field names to include in this group
      className?: string;
    }[];
  };
}

interface FormBuilderProps {
  config: FormLayoutConfig;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: UseFormReturn<any>;
}

export function FormBuilder({ config, form }: FormBuilderProps) {
  const { fields, layout } = config;

  // If layout is not specified, render all fields sequentially
  if (!layout) {
    return (
      <div className="space-y-6">
        {fields.map((field) => renderField(field, form))}
      </div>
    );
  }

  // Render fields according to the layout configuration
  return (
    <div className="space-y-6">
      {layout.groups.map((group, index) => (
        <div key={index} className={group.className}>
          {group.fields.map((fieldName) => {
            const fieldConfig = fields.find((f) => f.name === fieldName);
            if (!fieldConfig) return null;
            return renderField(fieldConfig, form);
          })}
        </div>
      ))}
    </div>
  );
}

// Helper function to render the appropriate field based on its type
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function renderField(config: FieldConfig, form: UseFormReturn<any>) {
  switch (config.type) {
    case "select":
      return (
        <SelectField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          placeholder={config.placeholder}
          options={config.options}
          form={form}
          className={config.className}
          onChangeHandler={config.onChangeHandler}
        />
      );
    case "number":
      return (
        <NumberField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          form={form}
          min={config.min}
          max={config.max}
          step={config.step}
          className={config.className}
        />
      );
    case "date":
      return (
        <DateField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          placeholder={config.placeholder}
          form={form}
          minDate={config.minDate}
          maxDate={config.maxDate}
          className={config.className}
        />
      );
    case "radioCard":
      return (
        <RadioCardField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          options={config.options}
          form={form}
          className={config.className}
        />
      );
    case "text":
      return (
        <TextField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          placeholder={config.placeholder}
          minLength={config.minLength}
          maxLength={config.maxLength}
          form={form}
          className={config.className}
        />
      );
    case "email":
      return (
        <EmailField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          placeholder={config.placeholder}
          minLength={config.minLength}
          maxLength={config.maxLength}
          form={form}
          className={config.className}
        />
      );
    case "password":
      return (
        <PasswordField
          key={config.name}
          name={config.name}
          label={config.label}
          description={config.description}
          placeholder={config.placeholder}
          minLength={config.minLength}
          maxLength={config.maxLength}
          form={form}
          className={config.className}
        />
      );
    default:
      return null;
  }
}
