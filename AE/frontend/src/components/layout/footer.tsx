import Link from "next/link";
import {
  Mail,
  Phone,
  MapPin,
  Twitter,
  Linkedin,
  Facebook,
  Instagram,
  ExternalLink,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { Separator } from "@/components/ui/separator";
import Logo from "@/components/ui/logo";
import { Heading, Text } from "@/components/ui/typography";
import { getEnabledProducts } from "@/data/products";

export default function Footer() {
  const tf = useTranslations("footer");
  const tp = useTranslations("products");

  const currentYear = new Date().getFullYear();

  // Get products from centralized data source
  const productLinks = getEnabledProducts().map((product) => ({
    key: product.id,
    href: product.href,
  }));

  // Resource links with translations
  const resourceLinks = [
    { key: "marketNews", href: "/news" },
    { key: "economicCalendar", href: "/calendar" },
    { key: "learningCenter", href: "/learn" },
    { key: "helpCenter", href: "/help" },
    { key: "apiDocumentation", href: "/developers" },
  ];

  // Legal links with translations
  const legalLinks = [
    { key: "termsOfService", href: "/terms" },
    { key: "privacyPolicy", href: "/privacy" },
    { key: "cookiePolicy", href: "/cookies" },
    { key: "disclaimer", href: "/disclaimer" },
    { key: "sitemap", href: "/sitemap.xml", external: true },
  ];

  return (
    <footer className="bg-muted/50 border-t border-border">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and description */}
          <div className="col-span-1 md:col-span-1">
            <div className="mb-4">
              <Logo />
            </div>
            <Text variant="muted" spacing="relaxed">
              {tf("description")}
            </Text>
            <div className="flex space-x-4 mb-6">
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label={tf("socialLinks.twitter")}
              >
                <Twitter size={18} />
                <span className="sr-only">{tf("socialLinks.twitter")}</span>
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label={tf("socialLinks.linkedin")}
              >
                <Linkedin size={18} />
                <span className="sr-only">{tf("socialLinks.linkedin")}</span>
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label={tf("socialLinks.facebook")}
              >
                <Facebook size={18} />
                <span className="sr-only">{tf("socialLinks.facebook")}</span>
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label={tf("socialLinks.instagram")}
              >
                <Instagram size={18} />
                <span className="sr-only">{tf("socialLinks.instagram")}</span>
              </a>
            </div>
          </div>

          {/* Products links */}
          <div>
            <Heading
              level="h6"
              spacing="relaxed"
              className="uppercase tracking-wider"
            >
              {tf("sections.products")}
            </Heading>
            <ul className="space-y-2">
              {productLinks.map((item) => (
                <li key={item.key}>
                  <Link href={item.href} className="block">
                    <Text
                      variant="muted"
                      spacing="none"
                      className="hover:text-primary transition-colors"
                    >
                      {tp(`${item.key}.title`)}
                    </Text>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources links */}
          <div>
            <Heading
              level="h6"
              spacing="relaxed"
              className="uppercase tracking-wider"
            >
              {tf("sections.resources")}
            </Heading>
            <ul className="space-y-2">
              {resourceLinks.map((item) => (
                <li key={item.key}>
                  <Link href={item.href} className="block">
                    <Text
                      variant="muted"
                      spacing="none"
                      className="hover:text-primary transition-colors"
                    >
                      {tf(`resources.${item.key}`)}
                    </Text>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact information */}
          <div>
            <Heading
              level="h6"
              spacing="relaxed"
              className="uppercase tracking-wider"
            >
              {tf("sections.contact")}
            </Heading>
            <ul className="space-y-3">
              <li className="flex items-start">
                <Mail size={16} className="mt-0.5 mr-2 text-muted-foreground" />
                <Text variant="muted" spacing="none">
                  {tf("contact.email")}
                </Text>
              </li>
              <li className="flex items-start">
                <Phone
                  size={16}
                  className="mt-0.5 mr-2 text-muted-foreground"
                />
                <Text variant="muted" spacing="none">
                  {tf("contact.phone")}
                </Text>
              </li>
              <li className="flex items-start">
                <MapPin
                  size={16}
                  className="mt-0.5 mr-2 text-muted-foreground"
                />
                <Text variant="muted" spacing="none">
                  {tf("contact.address.line1")}
                  <br />
                  {tf("contact.address.line2")}
                </Text>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom section with legal links */}
        <Separator className="my-6" />

        <div className="flex flex-col md:flex-row justify-between items-center">
          <Text variant="muted" spacing="relaxed" className="mb-4 md:mb-0">
            © {currentYear} {tf("copyright")}
          </Text>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center">
            {legalLinks.map((item) => (
              <Link key={item.key} href={item.href} className="block">
                <Text
                  variant="muted"
                  spacing="none"
                  className="hover:text-primary transition-colors flex items-center"
                >
                  {tf(`legal.${item.key}`)}
                  {item.external && <ExternalLink size={10} className="ml-1" />}
                </Text>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
