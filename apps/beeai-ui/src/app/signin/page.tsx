/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// import { Bee } from "@carbon/icons-react";
// import { Button } from "@carbon/react";
import { redirect } from 'next/navigation';
import { AuthError } from 'next-auth';

import { providerMap, signIn } from '#auth.ts';
import Bee from '#svgs/bee.svg';

// import BannerImage from '#svgs/BeeAI-Banner.svg';
import classes from './signin.module.scss';

const SIGNIN_ERROR_URL = '/error';

export default async function SignInPage(props) {
  return (
    <div className={classes.bannerBackground}>
      {/* <BannerImage /> */}
      <div className={classes.loginWrapper}>
        <div className={classes.loginMain}>
          <span>Log in to </span>
          <span className={classes.bolded}>BeeAI</span>
        </div>
        <div className={classes.buttonList}>
          <form
            action={async (formData) => {
              'use server';
              try {
                await signIn('credentials', formData);
              } catch (error) {
                if (error instanceof AuthError) {
                  return redirect(`${SIGNIN_ERROR_URL}?error=${error.type}`);
                }
                throw error;
              }
            }}
          ></form>
          {Object.values(providerMap).map((provider) => (
            <form
              key={provider.id}
              action={async () => {
                'use server';

                try {
                  await signIn(provider.id, {
                    redirectTo: props.searchParams?.callbackUrl ?? '',
                  });
                } catch (error) {
                  // Signin can fail for a number of reasons, such as the user
                  // not existing, or the user not having the correct role.
                  // In some cases, you may want to redirect to a custom error
                  if (error instanceof AuthError) {
                    return redirect(`${SIGNIN_ERROR_URL}?error=${error.type}`);
                  }

                  // Otherwise if a redirects happens Next.js can handle it
                  // so you can just re-thrown the error and let Next.js handle it.
                  // Docs:
                  // https://nextjs.org/docs/app/api-reference/functions/redirect#server-component
                  throw error;
                }
              }}
            >
              <div className={classes.beeaiLogin}>
                <button type="submit" className="cds--btn cds--btn--md cds--layout--size-md cds--btn--primary">
                  <Bee className={classes.beeButton} />
                  <span>Continue with {provider.name}</span>
                </button>
              </div>
            </form>
          ))}
        </div>
      </div>
    </div>
  );
}
