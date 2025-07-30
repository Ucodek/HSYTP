export interface DataResponse<T> {
  success: boolean;
  data: T;
  metadata: ResponseMetadata;
  message?: string;
}

export interface ResponseMetadata {
  timestamp: string;
  version: string;
}

export interface ListMetadata extends ResponseMetadata {
  total: number;
  page?: number;
  page_size?: number;
  has_next?: boolean;
  has_previous?: boolean;
}

export interface ListResponse<T> {
  success: boolean;
  data: T[];
  metadata: ListMetadata;
  message?: string;
}

export interface TokenResponse {
  token_type: string; // usually "bearer"
  access_token: string;
  refresh_token?: string;
  access_expires_in?: number;
  refresh_expires_in?: number;
}

export interface ErrorInfo {
  code: string;
  message: string;
  field?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  details?: Record<string, any>;
}

export interface ErrorResponse {
  success: false;
  data: null;
  metadata: ResponseMetadata;
  message?: string;
  errors: ErrorInfo[];
}
