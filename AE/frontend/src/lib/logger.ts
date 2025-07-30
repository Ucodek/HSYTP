/**
 * Log level enumeration
 */
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 4, // Disable all logging
}

/**
 * Logger configuration
 */
export interface LoggerConfig {
  level: LogLevel;
  enabledCategories?: string[];
  disabledCategories?: string[];
}

/**
 * Default configuration based on environment
 */
const defaultConfig: LoggerConfig = {
  level:
    process.env.NODE_ENV === "development" ? LogLevel.DEBUG : LogLevel.WARN,
  enabledCategories: [], // Empty means all enabled
  disabledCategories: [],
};

/**
 * Generic Logger
 * Provides consistent, configurable logging across the application
 */
export class Logger {
  private config: LoggerConfig;
  private category: string;

  /**
   * Create a new logger instance
   * @param category - Category name for this logger instance
   */
  constructor(category: string) {
    this.category = category;
    this.config = { ...defaultConfig };
  }

  /**
   * Configure the logger
   * @param config - New configuration options
   */
  configure(config: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Check if logging is enabled for the current category and level
   */
  private isEnabled(level: LogLevel): boolean {
    // If level is lower than the configured level, don't log
    if (level < this.config.level) {
      return false;
    }

    // Check if category is explicitly disabled
    if (
      this.config.disabledCategories &&
      this.config.disabledCategories.includes(this.category)
    ) {
      return false;
    }

    // Check if we have a whitelist and the category is not in it
    if (
      this.config.enabledCategories &&
      this.config.enabledCategories.length > 0 &&
      !this.config.enabledCategories.includes(this.category)
    ) {
      return false;
    }

    return true;
  }

  /**
   * Format log entry with timestamp, level, and category
   */
  private formatLogEntry(level: string, message: string): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] [${this.category}] ${message}`;
  }

  /**
   * Log a debug message
   */
  debug(message: string, ...args: (never | unknown)[]): void {
    if (this.isEnabled(LogLevel.DEBUG)) {
      console.debug(this.formatLogEntry("DEBUG", message), ...args);
    }
  }

  /**
   * Log an info message
   */
  info(message: string, ...args: (never | unknown)[]): void {
    if (this.isEnabled(LogLevel.INFO)) {
      console.info(this.formatLogEntry("INFO", message), ...args);
    }
  }

  /**
   * Log a warning message
   */
  warn(message: string, ...args: (never | unknown)[]): void {
    if (this.isEnabled(LogLevel.WARN)) {
      console.warn(this.formatLogEntry("WARN", message), ...args);
    }
  }

  /**
   * Log an error message
   */
  error(message: string, ...args: (never | unknown)[]): void {
    if (this.isEnabled(LogLevel.ERROR)) {
      console.error(this.formatLogEntry("ERROR", message), ...args);
    }
  }
}

/**
 * Shared logger configuration across instances
 */
let globalConfig: LoggerConfig = { ...defaultConfig };

/**
 * Cache of logger instances
 */
const loggerInstances: Record<string, Logger> = {};

/**
 * Get a logger for the specified category
 */
export function getLogger(category: string): Logger {
  if (!loggerInstances[category]) {
    const logger = new Logger(category);
    logger.configure(globalConfig);
    loggerInstances[category] = logger;
  }
  return loggerInstances[category];
}

/**
 * Configure all loggers
 */
export function configureLogger(config: Partial<LoggerConfig>): void {
  globalConfig = { ...globalConfig, ...config };

  // Update all existing instances
  Object.values(loggerInstances).forEach((logger) => {
    logger.configure(globalConfig);
  });
}

const loggerModule = {
  getLogger,
  configureLogger,
  LogLevel,
};

export default loggerModule;
