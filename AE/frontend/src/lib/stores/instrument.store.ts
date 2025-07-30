/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";
import {
  InstrumentResponse,
  InstrumentWithLatestPriceResponse,
} from "../types/instrument";

type Actions = {
  updateInstruments: (data: InstrumentResponse[]) => void;
  updateInstrumentsWithLatestPrice: (
    data: InstrumentWithLatestPriceResponse[]
  ) => void;
  updateError: (error: any) => void;
  updateLoading: (key: keyof Loading, value: boolean) => void;
  resetData: () => void;
};

type Action = {
  type: keyof Actions;
  value: any;
};

type Loading = {
  listLoading: boolean;
  listWithLatestPriceLoading: boolean;
  // ... other loading states
};

type Global = {
  instruments: InstrumentResponse[];
  instrumentsWithLatestPrice: InstrumentWithLatestPriceResponse[];
  error: any;
  // ... other global states
} & Loading;

const initialLoadingState: Loading = {
  listLoading: false,
  listWithLatestPriceLoading: true,
  // ... other loading states
};

const instrumentReducer = (state: Global, action: Action) => {
  switch (action.type) {
    case "updateInstruments":
      return { ...state, instruments: action.value };
    case "updateInstrumentsWithLatestPrice":
      return { ...state, instrumentsWithLatestPrice: action.value };
    case "updateError":
      return { ...state, error: action.value };
    case "updateLoading":
      return { ...state, [action.value.key]: action.value.value };
    default:
      return state;
  }
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const useInstrumentStore = create<Global & Actions>((set, get) => ({
  instruments: [],
  instrumentsWithLatestPrice: [],
  error: null,
  ...initialLoadingState,

  updateInstruments: (data) => {
    return set((state) => {
      return instrumentReducer(state, {
        type: "updateInstruments",
        value: data,
      });
    });
  },

  updateInstrumentsWithLatestPrice: (data) => {
    return set((state) => {
      return instrumentReducer(state, {
        type: "updateInstrumentsWithLatestPrice",
        value: data,
      });
    });
  },

  updateError: (error) => {
    return set((state) => {
      return instrumentReducer(state, {
        type: "updateError",
        value: error,
      });
    });
  },

  updateLoading: (key, value) => {
    return set((state) => {
      return instrumentReducer(state, {
        type: "updateLoading",
        value: { key, value },
      });
    });
  },

  resetData: () =>
    set(() => ({
      instruments: [],
      instrumentsWithLatestPrice: [],
      error: null,
      ...initialLoadingState,
    })),
}));
