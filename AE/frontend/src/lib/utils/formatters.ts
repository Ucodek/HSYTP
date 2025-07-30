/* eslint-disable @typescript-eslint/no-explicit-any */

// Tarih biçimlendirme seçenekleri
export const DATE_FORMATS = {
  // Kısa tarih formatı (örn: Jan 15)
  short: {
    month: "short",
    day: "numeric",
  },

  // Orta uzunlukta tarih formatı (örn: Jan 15, 2023)
  medium: {
    month: "short",
    day: "numeric",
    year: "numeric",
  },

  // Uzun tarih formatı (örn: January 15, 2023)
  long: {
    month: "long",
    day: "numeric",
    year: "numeric",
  },
} as const;

// Saat biçimlendirme seçenekleri - tip güvenli olacak şekilde düzeltildi
export const TIME_FORMATS = {
  // Kısa saat formatı (örn: 14:30 veya 2:30 PM)
  short: (locale?: string) => ({
    hour: "2-digit" as const,
    minute: "2-digit" as const,
    hour12: locale === "en",
  }),

  // Uzun saat formatı (örn: 14:30:25 veya 2:30:25 PM)
  long: (locale?: string) => ({
    hour: "2-digit" as const,
    minute: "2-digit" as const,
    second: "2-digit" as const,
    hour12: locale === "en",
  }),
} as const;

// Sayı format seçenekleri için tip tanımlaması
interface NumberFormatOptions {
  [key: string]: any;
}

// Sayı biçimlendirme seçenekleri
export const NUMBER_FORMATS: Record<string, NumberFormatOptions> = {
  // Sayıları formatlamak için (1.234,56)
  number: {
    style: "decimal",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },

  numberWithSign: {
    style: "decimal",
    signDisplay: "always",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },

  // Yüzdeleri formatlamak için (%12,34)
  percent: {
    style: "percent",
    signDisplay: "never",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },

  // İşaretli yüzdeleri formatlamak için (+12,34)
  percentWithSign: {
    style: "percent",
    signDisplay: "always",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },

  // Tam sayıları formatlamak için (1.234)
  integer: {
    style: "decimal",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  },

  // Para birimleri için ($1,234.56)
  currency: (currency: string = "USD") => ({
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }),

  // Hacim değerleri için kısaltılmış format (1.2M)
  volume: {
    notation: "compact",
    compactDisplay: "short",
    maximumFractionDigits: 1,
    style: "decimal",
  },

  // Varsayılan format - number ile aynı
  default: {
    style: "decimal",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },
};

/**
 * Sayısal değerleri belirli bir formatta biçimlendirir
 * @param locale - Kullanılacak dil/bölge kodu (örn. "tr", "en")
 * @param value - Biçimlendirilecek sayı değeri
 * @param option - NUMBER_FORMATS'tan kullanılacak format türü
 * @param params - Fonksiyon tipindeki formatlayıcılar için parametreler (örn. para birimi)
 * @returns Biçimlendirilmiş sayı metni
 *
 * @example
 * formatValue("tr", 1234.56); // "1.234,56"
 * formatValue("en", 1234.56); // "1,234.56"
 * formatValue("tr", 0.123, "percent"); // "%12,3"
 * formatValue("tr", 1234, "currency", "TRY"); // "1.234,00 ₺"
 */
export const formatValue = (
  locale: string,
  value: number | null,
  option: string = "number",
  params?: any // Opsiyonel parametreler
): string => {
  if (value === null) return "—";

  try {
    // options değişkeni özel işlem gerektirebilecek formatlar için
    let options: any = NUMBER_FORMATS[option];

    // Eğer format türü bulunamadıysa varsayılan formatı kullan
    if (!options) {
      console.warn(`Unknown format option "${option}", using number instead`);
      options = NUMBER_FORMATS.number;
    }

    // Eğer fonksiyon formatlama seçeneği ise çağır ve sonucunu kullan
    if (typeof options === "function") {
      options = options(params);
    }

    const formatter = new Intl.NumberFormat(locale, options);
    return formatter.format(value);
  } catch (error) {
    console.error(`Formatting error with option "${option}":`, error);
    return `${value}`;
  }
};

// Tarih formatlama yardımcı fonksiyonu
export const formatDate = (
  locale: string,
  date: Date | null,
  format: keyof typeof DATE_FORMATS = "short"
): string => {
  if (date === null) return "—";

  try {
    const options = DATE_FORMATS[format];
    const formatter = new Intl.DateTimeFormat(locale, options);
    return formatter.format(date);
  } catch (error) {
    console.error(`Date formatting error with format "${format}":`, error);
    return date?.toLocaleDateString() || "—";
  }
};

// Saat formatlama yardımcı fonksiyonu - düzeltildi
export const formatTime = (
  locale: string,
  date: Date | null,
  format: keyof typeof TIME_FORMATS = "short"
): string => {
  if (date === null) return "—";

  try {
    const options = TIME_FORMATS[format](locale);
    const formatter = new Intl.DateTimeFormat(locale, options);
    return formatter.format(date);
  } catch (error) {
    console.error(`Time formatting error with format "${format}":`, error);
    return date?.toLocaleTimeString() || "—";
  }
};

// Tarih ve saat birleşik formatlama
export const formatDateTime = (
  locale: string,
  date: Date | null,
  dateFormat: keyof typeof DATE_FORMATS = "short",
  timeFormat: keyof typeof TIME_FORMATS = "short"
): string => {
  if (date === null) return "—";

  try {
    return `${formatDate(locale, date, dateFormat)} ${formatTime(
      locale,
      date,
      timeFormat
    )}`;
  } catch (error) {
    console.error("DateTime formatting error:", error);
    return date?.toLocaleString() || "—";
  }
};

export const formatDateTimeWithTZ = (
  locale: string,
  date: Date | null,
  dateFormat: keyof typeof DATE_FORMATS = "medium",
  timeFormat: keyof typeof TIME_FORMATS = "long"
): string => {
  if (date === null) return "—";
  try {
    const options: Intl.DateTimeFormatOptions = {
      ...DATE_FORMATS[dateFormat],
      ...TIME_FORMATS[timeFormat](locale),
      timeZoneName: "short",
    };
    const formatter = new Intl.DateTimeFormat(locale, options);
    return formatter.format(date);
  } catch (error) {
    console.error("DateTime with TZ formatting error:", error);
    return date?.toLocaleString() || "—";
  }
};

// Timestamp'i Date nesnesine dönüştürür ve formatlar
export const formatTimestamp = (
  locale: string,
  timestamp: number | null,
  dateFormat: keyof typeof DATE_FORMATS = "short",
  timeFormat: keyof typeof TIME_FORMATS = "short"
): string => {
  if (timestamp === null) return "—";

  const date = timestampToDate(timestamp);
  return formatDateTime(locale, date, dateFormat, timeFormat);
};

// Timestamp'i Date nesnesine dönüştürür
export const timestampToDate = (timestamp: number): Date => {
  return new Date(timestamp * 1000);
};

// Impact seviyesine göre uygun badge varyantını döndürür
export const getImpactVariant = (
  impact: string
): "default" | "secondary" | "destructive" | "outline" => {
  switch (impact) {
    case "high":
      return "destructive";
    case "medium":
      return "default";
    case "low":
    default:
      return "secondary";
  }
};
