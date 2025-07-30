"use client";

import React from "react";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Text } from "@/components/ui/typography";
import { Calendar } from "@/components/ui/calendar";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { UseFormReturn } from "react-hook-form";

// Base enhanced form field component
interface EnhancedFieldProps {
  name: string;
  label: string;
  description?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: UseFormReturn<any>;
  className?: string;
}

// Dropdown select field
interface SelectFieldProps extends EnhancedFieldProps {
  placeholder: string;
  options: {
    value: string;
    label: string;
  }[];
  onChangeHandler?: (value: string) => void;
}

export function SelectField({
  name,
  label,
  description,
  form,
  placeholder,
  options,
  onChangeHandler,
  className,
}: SelectFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <Select
            onValueChange={(value) => {
              field.onChange(value);
              if (onChangeHandler) onChangeHandler(value);
            }}
            defaultValue={field.value?.toString()}
          >
            <FormControl>
              <SelectTrigger className="w-full cursor-pointer">
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {options.map((option) => (
                <SelectItem
                  key={option.value}
                  value={option.value}
                  className="cursor-pointer"
                >
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {description && <Text variant="muted">{description}</Text>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

// Number input field
interface NumberFieldProps extends EnhancedFieldProps {
  min?: number;
  max?: number;
  step?: number;
}

export function NumberField({
  name,
  label,
  description,
  form,
  min = 0,
  max = 100,
  step = 1,
  className,
}: NumberFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type="number"
              min={min}
              max={max}
              step={step}
              value={field.value}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                field.onChange(
                  !isNaN(value) ? Math.min(Math.max(value, min), max) : min
                );
              }}
            />
          </FormControl>
          {description && <Text variant="muted">{description}</Text>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

// Date picker field
interface DateFieldProps extends EnhancedFieldProps {
  placeholder: string;
  minDate?: Date;
  maxDate?: Date;
}

export function DateField({
  name,
  label,
  description,
  form,
  placeholder,
  minDate,
  maxDate,
  className,
}: DateFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <Popover>
            <PopoverTrigger asChild>
              <FormControl>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left cursor-pointer",
                    !field.value && "text-muted-foreground"
                  )}
                >
                  {field.value ? format(field.value, "PPP") : placeholder}
                  <CalendarIcon className="ml-auto h-4 w-4" />
                </Button>
              </FormControl>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={field.value}
                onSelect={field.onChange}
                disabled={(date) => {
                  if (minDate && date < minDate) return true;
                  if (maxDate && date > maxDate) return true;
                  return false;
                }}
                initialFocus
              />
            </PopoverContent>
          </Popover>
          {description && <Text variant="muted">{description}</Text>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

// Radio card field with icons for strategy selection
interface RadioCardOption {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
}

interface RadioCardFieldProps extends EnhancedFieldProps {
  options: RadioCardOption[];
}

export function RadioCardField({
  name,
  label,
  description,
  form,
  options,
  className,
}: RadioCardFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {options.map((option) => {
              const isSelected = field.value === option.id;
              const OptionIcon = option.icon;
              return (
                <div key={option.id}>
                  <input
                    type="radio"
                    id={`${name}-${option.id}`}
                    value={option.id}
                    checked={isSelected}
                    onChange={() => field.onChange(option.id)}
                    className="sr-only peer"
                  />
                  <label
                    htmlFor={`${name}-${option.id}`}
                    className={cn(
                      "flex flex-col p-3 rounded-md border cursor-pointer",
                      "hover:bg-accent",
                      isSelected
                        ? "border-primary bg-primary/5"
                        : "border-input"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <OptionIcon size={16} />
                      <Text weight="medium" spacing="none">
                        {option.name}
                      </Text>
                    </div>
                    <Text variant="muted" className="mt-1">
                      {option.description}
                    </Text>
                  </label>
                </div>
              );
            })}
          </div>
          {description && (
            <Text variant="muted" className="mt-2">
              {description}
            </Text>
          )}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

// Add support for conditional dependency
export function ConditionalField({
  condition,
  children,
}: {
  condition: boolean;
  children: React.ReactNode;
}) {
  if (!condition) return null;
  return <>{children}</>;
}

// Add support for field array (useful for custom weights in the future)
interface FieldArrayProps extends EnhancedFieldProps {
  defaultItems?: number;
  renderItem: (index: number, remove: () => void) => React.ReactNode;
  addButtonText?: string;
}

export function FieldArray({
  //   name,
  label,
  description,
  //   form,
  defaultItems = 2,
  renderItem,
  addButtonText = "Add Item",
  className,
}: FieldArrayProps) {
  const [items, setItems] = React.useState<number[]>(
    Array.from({ length: defaultItems }, (_, i) => i)
  );

  const addItem = () => {
    setItems((prev) => [...prev, prev.length > 0 ? Math.max(...prev) + 1 : 0]);
  };

  const removeItem = (index: number) => {
    setItems((prev) => prev.filter((i) => i !== index));
  };

  return (
    <FormItem className={className}>
      <FormLabel>{label}</FormLabel>
      <div className="space-y-2">
        {items.map((index) => (
          <div key={index}>{renderItem(index, () => removeItem(index))}</div>
        ))}
        <Button
          type="button"
          variant="outline"
          onClick={addItem}
          className="w-full"
        >
          {addButtonText}
        </Button>
      </div>
      {description && <Text variant="muted">{description}</Text>}
    </FormItem>
  );
}

// Text input field
interface TextFieldProps extends EnhancedFieldProps {
  placeholder?: string;
  minLength?: number;
  maxLength?: number;
}

export function TextField({
  name,
  label,
  description,
  form,
  placeholder,
  minLength,
  maxLength,
  className,
}: TextFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type="text"
              placeholder={placeholder}
              minLength={minLength}
              maxLength={maxLength}
              {...field}
            />
          </FormControl>
          {description && <Text variant="muted">{description}</Text>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

// Email input field
interface EmailFieldProps extends EnhancedFieldProps {
  placeholder?: string;
  minLength?: number;
  maxLength?: number;
}

export function EmailField({
  name,
  label,
  description,
  form,
  placeholder,
  minLength,
  maxLength,
  className,
}: EmailFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type="email"
              placeholder={placeholder}
              minLength={minLength}
              maxLength={maxLength}
              {...field}
            />
          </FormControl>
          {description && <Text variant="muted">{description}</Text>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

// Password input field
interface PasswordFieldProps extends EnhancedFieldProps {
  placeholder?: string;
  minLength?: number;
  maxLength?: number;
}

export function PasswordField({
  name,
  label,
  description,
  form,
  placeholder,
  minLength,
  maxLength,
  className,
}: PasswordFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type="password"
              placeholder={placeholder}
              minLength={minLength}
              maxLength={maxLength}
              {...field}
            />
          </FormControl>
          {description && <Text variant="muted">{description}</Text>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
