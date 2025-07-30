import { getLogger } from "../logger";
import instrumentRepository from "../repositories/instrument.repository";
import { useInstrumentStore } from "../stores/instrument.store";
import apiErrorHandler from "../api/error-handler";
import {
  InstrumentListQuery,
  ListInstrumentResponse,
  ListInstrumentWithLatestPriceResponse,
} from "../types/instrument";

const logger = getLogger("InstrumentModel");

export class Instrument {
  /**
   * Fetch instrument list and update store
   */
  static async list(
    queries: InstrumentListQuery
  ): Promise<ListInstrumentResponse> {
    const { updateInstruments, updateError, updateLoading } =
      useInstrumentStore.getState();

    try {
      updateLoading("listLoading", true);
      updateError(null);
      const result = await instrumentRepository.list(queries);
      updateInstruments(result.data);
      return result;
    } catch (error) {
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error("Failed to fetch instrument list:", standardizedError);
      updateError(standardizedError);
      throw standardizedError;
    } finally {
      updateLoading("listLoading", false);
    }
  }

  /**
   * Fetch instrument list with latest prices and update store
   */
  static async listWithLatestPrice(
    queries: InstrumentListQuery
  ): Promise<ListInstrumentWithLatestPriceResponse> {
    const { updateInstrumentsWithLatestPrice, updateError, updateLoading } =
      useInstrumentStore.getState();

    try {
      updateLoading("listWithLatestPriceLoading", true);
      updateError(null);
      const result = await instrumentRepository.listWithLatestPrice(queries);
      updateInstrumentsWithLatestPrice(result.data);
      return result;
    } catch (error) {
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error(
        "Failed to fetch instrument list with latest prices:",
        standardizedError
      );
      updateError(standardizedError);
      throw standardizedError;
    } finally {
      updateLoading("listWithLatestPriceLoading", false);
    }
  }
}

export default Instrument;
