import { cn } from "@/lib/utils";
import { type VariantProps, cva } from "class-variance-authority";

// Define heading variants that match your current design
export const headingVariants = cva(
  "font-semibold tracking-tight text-foreground",
  {
    variants: {
      level: {
        h1: "text-3xl md:text-4xl lg:text-5xl font-bold", // Hero title
        h2: "text-3xl font-semibold", // Page titles
        h3: "text-2xl font-semibold", // Major section headers
        h4: "text-xl font-semibold", // Component headers (our most common)
        h5: "text-lg font-medium", // Sub-sections
        h6: "text-base font-medium", // Minor headings
      },
      spacing: {
        default: "mb-2",
        none: "",
        tight: "mb-1",
        relaxed: "mb-4",
        large: "mb-6",
      },
    },
    defaultVariants: {
      level: "h4", // Most common in your components
      spacing: "default",
    },
  }
);

interface HeadingProps
  extends React.HTMLAttributes<HTMLHeadingElement>,
    VariantProps<typeof headingVariants> {
  as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
}

// More versatile heading component that better matches your existing code patterns
export function Heading({
  children,
  level,
  spacing,
  as,
  className,
  ...props
}: HeadingProps) {
  // Use specified level for both styling and element, or override with "as"
  const Component =
    as || (level as "h1" | "h2" | "h3" | "h4" | "h5" | "h6") || "h4";

  return (
    <Component
      className={cn(headingVariants({ level, spacing, className }))}
      {...props}
    >
      {children}
    </Component>
  );
}

// Text variants for body text, matching your current usage
export const textVariants = cva("", {
  variants: {
    variant: {
      default: "text-base text-foreground",
      large: "text-lg text-foreground",
      small: "text-sm text-foreground",
      muted: "text-sm text-muted-foreground",
    },
    weight: {
      normal: "font-normal",
      medium: "font-medium",
      semibold: "font-semibold",
    },
    spacing: {
      default: "mb-2",
      none: "",
      tight: "mb-1",
      relaxed: "mb-4",
    },
  },
  defaultVariants: {
    variant: "default",
    weight: "normal",
    spacing: "default",
  },
});

interface TextProps
  extends React.HTMLAttributes<HTMLParagraphElement>,
    VariantProps<typeof textVariants> {}

export function Text({
  children,
  variant,
  weight,
  spacing,
  className,
  ...props
}: TextProps) {
  return (
    <p
      className={cn(textVariants({ variant, weight, spacing, className }))}
      {...props}
    >
      {children}
    </p>
  );
}
