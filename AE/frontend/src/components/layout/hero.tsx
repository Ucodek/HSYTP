import Link from "next/link";
import Image from "next/image";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Heading } from "@/components/ui/typography";
import { cn } from "@/lib/utils";

type HeroProps = {
  title: string;
  subtitle?: string;
  buttonText?: string;
  buttonLink?: string;
  imageUrl?: string;
  altText?: string;
  className?: string;
  layout?: "default" | "reverse";
};

export default function Hero({
  title,
  subtitle,
  buttonText,
  buttonLink,
  imageUrl,
  altText,
  className,
  layout = "default",
}: HeroProps) {
  // Düzen sınıfları
  const layoutClasses = {
    default: "flex-col md:flex-row",
    reverse: "flex-col md:flex-row-reverse md:space-x-reverse",
  };

  // İçerik genişliği sınıfları
  const contentWidthClasses = {
    default: "w-full md:w-1/2",
    reverse: "w-full md:w-1/2",
  };

  return (
    <section
      className={cn(
        "relative pt-24 pb-12 md:py-28 bg-muted/50 overflow-hidden",
        className
      )}
    >
      {/* Decorations */}
      <DecorationComponent />

      <div className="container relative mx-auto px-4">
        <div
          className={cn(
            "flex items-center md:space-x-8",
            layoutClasses[layout]
          )}
        >
          {/* Text Content */}
          <div className={cn(contentWidthClasses[layout], "mb-10 md:mb-0")}>
            <Heading level="h1" spacing="relaxed" className="leading-tight">
              {title}
            </Heading>
            <Heading
              level="h4"
              spacing="relaxed"
              className="text-muted-foreground max-w-lg leading-relaxed"
            >
              {subtitle}
            </Heading>
            {buttonText && buttonLink && (
              <Button asChild size="lg" className="mt-6">
                <Link href={buttonLink} className="group">
                  {buttonText}
                  <ArrowRight
                    className="ml-2 h-6 w-6 transition-transform group-hover:translate-x-1"
                    aria-hidden="true"
                  />
                </Link>
              </Button>
            )}
          </div>

          {/* Image */}
          {imageUrl && altText && (
            <div className={contentWidthClasses[layout]}>
              <div className="relative h-64 sm:h-72 md:h-80 lg:h-96 rounded-lg overflow-hidden shadow-lg">
                <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-transparent z-10" />
                <Image
                  src={imageUrl}
                  alt={altText}
                  fill
                  className="object-cover"
                  priority
                />
                <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-background/20 to-transparent z-20" />
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

const DecorationComponent = () => {
  return (
    <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
      {/* Geometric Shapes */}
      <div className="absolute top-32 right-[15%] w-24 h-24 rounded-md bg-primary/5 rotate-45 backdrop-blur-sm"></div>
      <div className="absolute bottom-20 left-[10%] w-16 h-16 rounded-full border border-primary/20"></div>

      {/* Half-circle shape */}
      <div className="absolute top-[20%] -left-12 w-24 h-48 bg-primary/5 rounded-r-full"></div>

      {/* Abstract triangle */}
      <svg
        className="absolute bottom-[15%] right-[20%] w-32 h-32 text-primary/10"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M20 80L50 20L80 80L20 80Z" fill="currentColor" />
      </svg>

      {/* Dotted grid pattern */}
      <div className="absolute bottom-[10%] right-[25%] grid grid-cols-4 gap-4">
        {[...Array(16)].map((_, i) => (
          <div key={i} className="w-1.5 h-1.5 rounded-full bg-primary/20"></div>
        ))}
      </div>

      {/* Wavy line */}
      <svg
        className="absolute top-[30%] right-[5%] w-24 h-24 text-primary/15"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0 50C20 30 30 70 50 50C70 30 80 70 100 50"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>

      {/* Gradient blob */}
      <div className="absolute -bottom-20 left-[40%] w-64 h-64 rounded-full bg-gradient-to-br from-primary/5 via-secondary/5 to-transparent opacity-60 blur-2xl"></div>

      {/* Hexagon shape */}
      <svg
        className="absolute top-16 left-[30%] w-12 h-12 text-primary/10"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M50 0L93.3 25V75L50 100L6.7 75V25L50 0Z" fill="currentColor" />
      </svg>

      {/* Diagonal stripes */}
      <div className="absolute top-0 right-0 w-32 h-32 overflow-hidden opacity-20">
        <div className="absolute inset-0 -rotate-45 flex space-x-2">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-full w-px bg-primary"></div>
          ))}
        </div>
      </div>

      {/* Random floating squares */}
      <div className="absolute bottom-[30%] right-[40%] w-4 h-4 border border-primary/30 rotate-12"></div>
      <div className="absolute top-[15%] left-[55%] w-3 h-3 bg-primary/10 rotate-45"></div>
      <div className="absolute bottom-[15%] left-[15%] w-5 h-5 border-2 border-primary/10 rounded-sm"></div>
    </div>
  );
};
