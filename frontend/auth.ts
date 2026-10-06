import { backendUrl } from "@/lib/backend";
import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import { requireInternalToken } from "@/lib/internal-auth";

export const { handlers, signIn, signOut, auth } = NextAuth({
    providers: [
        Google({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }),
    ],
    pages: {
        signIn: "/signin",
        error: "/signin",
    },
    callbacks: {
        // FIXED: Removed the broken jwt/session callbacks that called the phantom endpoint.

        async signIn({ user }) {
            if (!user.email) return false;

            try {
                // Make sure to use the server-side environment variable if possible
                const apiOrigin = backendUrl();
                
                const response = await fetch(`${apiOrigin}/api/v1/auth/sync`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        // SECURITY: This runs on the Next.js server, so it's safe to use the secret here.
                        'x-internal-token': requireInternalToken()
                    },
                    body: JSON.stringify({
                        email: user.email,
                        full_name: user.name,
                    }),
                });

                if (!response.ok) {
                    console.error("Backend user synchronization failed", { status: response.status });
                    return false; // A session requires a persisted backend identity.
                }
                
                return true;

            } catch {
                console.error("Backend user synchronization unavailable");
                return false;
            }
        },
    },
});