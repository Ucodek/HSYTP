import { getAccessToken } from "@/lib/storage";
// import { useAuthStore } from "@/lib/stores/auth.store";
import { Fragment } from "react";

export function AuthorizedView({ children }: { children: React.ReactNode }) {
  //   const { user } = useAuthStore((state) => ({ user: state.user }));
  const token = getAccessToken();

  if (!token) return null;
  return <Fragment>{children}</Fragment>;
}
