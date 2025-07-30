import Link from "next/link";
import { ArrowRight } from "lucide-react";
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Heading, Text } from "@/components/ui/typography";
import React from "react";

export interface ProductCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  ctaText: string;
  link: string;
}

export const ProductCard = React.memo(function ProductCard({
  icon,
  title,
  description,
  ctaText,
  link,
}: ProductCardProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="h-12 w-12 mb-4 flex items-center justify-center bg-primary/10 rounded-md text-primary">
          {icon}
        </div>
        <CardTitle>
          <Heading level="h5" spacing="tight">
            {title}
          </Heading>
        </CardTitle>
        <CardDescription>
          <Text spacing="none" className="text-muted-foreground line-clamp-2">
            {description}
          </Text>
        </CardDescription>
      </CardHeader>

      <CardFooter className="mt-auto pt-0">
        <Button variant="link" asChild className="p-0 h-auto">
          <Link href={link} className="group">
            <Text weight="medium" spacing="none" className="flex items-center">
              {ctaText}
              <ArrowRight
                size={16}
                className="ml-1 transition-transform group-hover:translate-x-1"
              />
            </Text>
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
});
