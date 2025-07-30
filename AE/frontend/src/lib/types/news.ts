/**
 * Haberler, makaleler ve içeriklerle ilgili tip tanımlamaları
 */

/**
 * Haber makalesi veri tipi
 */
export interface NewsArticle {
  timestamp: number;
  title: string;
  source: string;
  url: string;
  summary: string;
  cover?: string;
}

/**
 * Blog/Makale/İçerik veri tipi
 */
export interface Post {
  timestamp: number;
  title: string;
  url: string;
  summary: string;
  cover?: string;
  category?: string;
}
