import Link from "next/link";
import { cn } from "@/lib/utils";
import { Heading } from "@/components/ui/typography";

interface LogoProps {
  className?: string;
}

export default function Logo({ className }: LogoProps) {
  return (
    <Link href="/" className={cn("flex items-center", className)}>
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="text-foreground"
        aria-hidden="true"
      >
        <path
          d="M3 13.2L8.45 9L13.91 13.26L21 7.5"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M3 19.2L8.45 15L13.91 19.26L21 13.5"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <Heading level="h3" spacing="none" className="ml-2 leading-normal">
        StockTrack
      </Heading>
    </Link>
  );
}
