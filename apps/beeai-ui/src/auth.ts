/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import NextAuth from 'next-auth';

import IBM from '#app/auth/providers/ibm.ts';

export const { handlers, signIn, signOut, auth } = NextAuth({
  debug: true,
  providers: [
    IBM({
      id: 'IBM',
      name: 'IBM',
      type: 'oidc',
      issuer: process.env.AUTH_IBM_ISSUER,
      authorization: process.env.AUTH_IBM_AUTHORIZATION,
      clientId: process.env.IBM_CLIENT_ID,
      clientSecret: process.env.IBM_CLIENT_SECRET,
      wellKnown: process.env.DISCOVERY_ENDPOINT,
      redirectProxyUrl: process.env.AUTH_REDIRECT_PROXY_URL,
      userinfo: process.env.AUTH_IBM_USERINFO,
      token: process.env.AUTH_IBM_TOKEN,
    }),
  ],
  basePath: '/auth',
  session: { strategy: 'jwt' },
  trustHost: true,
  redirectProxyUrl: process.env.AUTH_REDIRECT_PROXY_URL,
  callbacks: {
    authorized({ request, auth }) {
      const { pathname } = request.nextUrl;
      if (pathname === '/middleware-example') return !!auth;
      return true;
    },
    jwt({ token, trigger, session }) {
      if (trigger === 'update') token.name = session.user.name;
      return token;
    },
    async session({ session }) {
      // if (token?.accessToken) session['accessToken'] = token.accessToken;
      return session;
    },
  },
});
