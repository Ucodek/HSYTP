/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";
import { TokenResponse } from "../types/response";
import { User } from "../types/auth";

type Actions = {
  // registerUser: (user: any) => void;
  loginUser: (tokens: TokenResponse) => void;
  updateUser: (user: User) => void;
  updateError: (error: any) => void;
  updateIsAuthenticated: (isAuthenticated: boolean) => void;
  updateLoading: (key: keyof Loading, value: boolean) => void;
  resetData: () => void;
};

type Action = {
  type: keyof Actions;
  value: any;
};

type Loading = {
  registerLoading: boolean;
  loginLoading: boolean;
  logoutLoading: boolean;
  // ... other loading states
};

type Global = {
  user: User | null;
  tokens: TokenResponse | null;
  error: any;
  isAuthenticated: boolean;
  // ... other global states
} & Loading;

const initialLoadingState: Loading = {
  registerLoading: false,
  loginLoading: false,
  logoutLoading: false,
  // ... other loading states
};

const authReducer = (state: Global, action: Action) => {
  switch (action.type) {
    // case "registerUser":
    //   return { ...state, user: action.value };
    case "loginUser":
      return { ...state, tokens: action.value };
    case "updateUser":
      return { ...state, user: action.value };
    case "updateError":
      return { ...state, error: action.value };
    case "updateIsAuthenticated":
      return { ...state, isAuthenticated: action.value };
    case "updateLoading":
      return { ...state, [action.value.key]: action.value.value };
    default:
      return state;
  }
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const useAuthStore = create<Global & Actions>((set, get) => ({
  user: null,
  tokens: null,
  error: null,
  isAuthenticated: false,
  ...initialLoadingState,

  // registerUser: (user: any) => {
  //   return set((state) => {
  //     return authReducer(state, {
  //       type: "registerUser",
  //       value: user,
  //     });
  //   });
  // },

  loginUser: (tokens: TokenResponse) => {
    return set((state) => {
      return authReducer(state, {
        type: "loginUser",
        value: tokens,
      });
    });
  },

  updateUser: (user: User) => {
    return set((state) => {
      return authReducer(state, {
        type: "updateUser",
        value: user,
      });
    });
  },

  updateError: (error) => {
    return set((state) => {
      return authReducer(state, {
        type: "updateError",
        value: error,
      });
    });
  },

  updateIsAuthenticated: (isAuthenticated: boolean) => {
    return set((state) => {
      return authReducer(state, {
        type: "updateIsAuthenticated",
        value: isAuthenticated,
      });
    });
  },

  updateLoading: (key, value) => {
    return set((state) => {
      return authReducer(state, {
        type: "updateLoading",
        value: { key, value },
      });
    });
  },

  resetData: () =>
    set(() => ({
      user: null,
      tokens: null,
      error: null,
      isAuthenticated: false,
      ...initialLoadingState,
    })),
}));
