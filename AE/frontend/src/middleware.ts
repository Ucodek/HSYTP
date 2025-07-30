import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";
import { NextRequest, NextResponse } from "next/server";

// export default createMiddleware(routing);

const AUTH_PATHS = ["/login", "/signup"];

export default async function middleware(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;

  if (token) {
    // Check if the request path is in the AUTH_PATHS array
    const isAuthPath = AUTH_PATHS.some((path) =>
      req.nextUrl.pathname.startsWith(path)
    );
    if (isAuthPath) {
      // Redirect to home page if authenticated and on an auth path
      return NextResponse.redirect(new URL("/", req.url));
    }
  }

  // Continue with the default middleware behavior
  return createMiddleware(routing)(req);
}

export const config = {
  matcher: [
    // Enable a redirect to a matching locale at the root
    "/",

    // Set a cookie to remember the previous locale for
    // all requests that have a locale prefix
    "/(tr|en)/:path*",

    // Enable redirects that add missing locales
    // (e.g. `/pathnames` -> `/en/pathnames`)
    "/((?!_next|_vercel|.*\\..*).*)",
  ],
};
