import { useTranslations } from "next-intl";
import { SectionWrapper } from "@/components/layout/section-wrapper";
import { ProductCard } from "@/components/ui/product-card";
import { getEnabledProducts } from "@/data/products";

export default function ProductList() {
  const t = useTranslations("pages.home.featuredProducts");
  const tp = useTranslations("products");

  // Get enabled products from the centralized data source
  const products = getEnabledProducts();

  return (
    <SectionWrapper title={t("title")} wrapperClassName="py-8">
      {products.map((product) => {
        const Icon = product.icon;

        return (
          <ProductCard
            key={product.id}
            icon={<Icon size={24} />}
            title={tp(`${product.id}.title`)}
            description={tp(`${product.id}.description`)}
            ctaText={tp(`${product.id}.cta`)}
            link={product.href}
          />
        );
      })}
    </SectionWrapper>
  );
}
