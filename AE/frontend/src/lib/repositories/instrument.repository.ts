import requests from "../requests";
import { getLogger } from "../logger";
import {
  InstrumentListQuery,
  ListInstrumentResponse,
  ListInstrumentWithLatestPriceResponse,
} from "../types/instrument";

const logger = getLogger("InstrumentRepository");

export const instrumentRepository = {
  /**
   * List instruments
   */
  list: async (
    queries: InstrumentListQuery
  ): Promise<ListInstrumentResponse> => {
    try {
      logger.debug("Fetching instrument list", queries);
      const result = await requests.instrument.list(queries);
      logger.info(`Fetched ${result.data.length} instruments`);
      return result;
    } catch (error) {
      logger.error("Failed to fetch instrument list:", error);
      throw error;
    }
  },
  /**
   * List instruments with latest prices
   */
  listWithLatestPrice: async (
    queries: InstrumentListQuery
  ): Promise<ListInstrumentWithLatestPriceResponse> => {
    try {
      logger.debug("Fetching instrument list with latest prices", queries);
      const result = await requests.instrument.listWithLatestPrice(queries);
      logger.info(
        `Fetched ${result.data.length} instruments with latest prices`
      );
      return result;
    } catch (error) {
      logger.error(
        "Failed to fetch instrument list with latest prices:",
        error
      );
      throw error;
    }
  },
};

export default instrumentRepository;
