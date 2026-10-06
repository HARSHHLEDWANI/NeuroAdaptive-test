import { auth } from "@/auth";
import { NextResponse } from "next/server";

// Define all routes that require authentication
const protectedRoutes = ["/dashboard", "/courses"];
const legacyRoutes = ["/chat", "/profile", "/mission", "/quiz", "/read"];

export default auth((req) => {
    const isLoggedIn = !!req.auth;
    const pathname = req.nextUrl.pathname;

    if (pathname === "/api/chat" || pathname.startsWith("/api/chat/") || pathname === "/api/quiz" || pathname.startsWith("/api/quiz/")) {
        return NextResponse.json({ error: "Not found" }, { status: 404 });
    }
    // Check if the current path starts with any of the protected routes
    if (legacyRoutes.some(route => pathname === route || pathname.startsWith(`${route}/`))) {
        return NextResponse.redirect(new URL(isLoggedIn ? "/dashboard" : "/signin", req.url));
    }
    const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
    const isOnSignin = pathname.startsWith("/signin");

    if (isProtectedRoute && !isLoggedIn) {
        return NextResponse.redirect(new URL("/signin", req.url));
    }

    if (isOnSignin && isLoggedIn) {
        return NextResponse.redirect(new URL("/dashboard", req.url));
    }

    return NextResponse.next();
});

export const config = {
    // The matcher tells Next.js which routes this middleware should run on.
    // We include all protected paths and the signin page.
    matcher: [
        "/dashboard/:path*",
        "/profile/:path*",
        "/courses/:path*",
        "/chat/:path*", "/mission/:path*", "/quiz/:path*", "/read/:path*",
        "/api/chat/:path*", "/api/quiz/:path*",
        "/signin"
    ],
};