/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import NextAuth, { type DefaultSession } from 'next-auth';

import IBM from '#app/auth/providers/ibm.ts';

declare module 'next-auth' {
  /**
   * Returned by `auth`, `useSession`, `getSession` and received as a prop on the `SessionProvider` React Context
   */
  interface Session {
    id_token: string & DefaultSession['user'];
  }
}

import type { JWT, JWTDecodeParams, JWTEncodeParams } from 'next-auth/jwt';

declare module 'next-auth/jwt' {
  /** Returned by the `jwt` callback and `auth`, when using JWT sessions */
  interface JWT {
    /** OpenID ID Token */
    id_token?: string;
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  debug: true,
  providers: [
    IBM({
      id: 'IBM',
      name: 'IBM',
      type: 'oidc',
      issuer: process.env.NEXTAUTH_IBM_ISSUER_URL,
      clientId: process.env.NEXTAUTH_IBM_CLIENT_ID,
      clientSecret: process.env.NEXTAUTH_IBM_CLIENT_SECRET,
      redirectProxyUrl: process.env.NEXTAUTH_REDIRECT_PROXY_URL,
      account(account) {
        const refresh_token_expires_at = Math.floor(Date.now() / 1000) + Number(account.refresh_token_expires_in);
        return {
          access_token: account.access_token,
          expires_at: account.expires_at,
          refresh_token: account.refresh_token,
          refresh_token_expires_at,
        };
      },
    }),
  ],
  basePath: '/auth',
  session: { strategy: 'jwt' },
  trustHost: true,
  redirectProxyUrl: process.env.AUTH_REDIRECT_PROXY_URL,
  useSecureCookies: true,
  jwt: {
    async encode(params: JWTEncodeParams<JWT>): Promise<string> {
      // return a custom encoded JWT string
      return params?.token?.['id_token'] || '';
    },
    async decode(params: JWTDecodeParams): Promise<JWT | null> {
      // return a `JWT` object, or `null` if decoding failed
      // likely need to base64 decode the id_token and extract the
      const jwt = { id_token: params.token || '' };
      return jwt;
    },
  },
  cookies: {
    sessionToken: {
      name: `beeai-platform`,
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: true,
      },
    },
  },
  callbacks: {
    authorized({ request, auth }) {
      const { pathname } = request.nextUrl;
      if (pathname === '/middleware-example') return !!auth;
      return true;
    },
    jwt({ token, account, trigger, session }) {
      if (trigger === 'update') {
        token.name = session.user.name;
        if (token['id_token'] && session) {
          if (!session['id_token']) {
            session['id_token'] = token['id_token'];
          }
        }
      }
      // pull the id token out of the account on signIn
      if (account) {
        token['id_token'] = account.id_token;
      }
      return token;
    },
    async session({ session, token }) {
      if (token?.id_token) session['id_token'] = token.id_token;
      return session;
    },
  },
});
