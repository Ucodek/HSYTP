/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";

type Actions = {
  updatePortfolio: (portfolio: any) => void;
  updateError: (error: any) => void;
  updateLoading: (key: keyof Loading, value: boolean) => void;
  resetData: () => void;
};

type Action = {
  type: keyof Actions;
  value: any;
};

type Loading = {
  optimizeLoading: boolean;
  // ... other loading states
};

type Global = {
  portfolio: any;
  error: any;
  // ... other global states
} & Loading;

const initialLoadingState: Loading = {
  optimizeLoading: false,
  // ... other loading states
};

const portfolioReducer = (state: Global, action: Action) => {
  switch (action.type) {
    case "updatePortfolio":
      return { ...state, portfolio: action.value };
    case "updateError":
      return { ...state, error: action.value };
    case "updateLoading":
      return { ...state, [action.value.key]: action.value.value };
    default:
      return state;
  }
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const usePortfolioStore = create<Global & Actions>((set, get) => ({
  portfolio: null,
  error: null,
  ...initialLoadingState,

  updatePortfolio: (portfolio: any) => {
    return set((state) => {
      return portfolioReducer(state, {
        type: "updatePortfolio",
        value: portfolio,
      });
    });
  },

  updateError: (error) => {
    return set((state) => {
      return portfolioReducer(state, {
        type: "updateError",
        value: error,
      });
    });
  },

  updateLoading: (key, value) => {
    return set((state) => {
      return portfolioReducer(state, {
        type: "updateLoading",
        value: { key, value },
      });
    });
  },

  resetData: () =>
    set(() => ({
      portfolio: null,
      error: null,
      ...initialLoadingState,
    })),
}));
