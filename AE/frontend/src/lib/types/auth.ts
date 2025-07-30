import { DataResponse, TokenResponse } from "./response";

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface PasswordChangeData {
  current_password: string;
  password: string;
}

export type RegisterResponse = DataResponse<User>;

export type LoginResponse = DataResponse<TokenResponse>;

export type UserResponse = DataResponse<User>;
