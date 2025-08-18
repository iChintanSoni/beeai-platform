/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { Button } from '@carbon/react';
import { type CSSProperties, useCallback } from 'react';
import { FormProvider, useForm } from 'react-hook-form';

import type { UIFormPart } from '#modules/messages/types.ts';

import type { FormValues } from '../types';
import { getDefaultValues } from '../utils';
import { FormField } from './FormField';
import classes from './FormRenderer.module.scss';

interface Props {
  formPart: UIFormPart;
}

export function FormRenderer({ formPart }: Props) {
  const { id, title, description, columns, submit_label = 'Submit', fields } = formPart;

  const defaultValues = getDefaultValues(fields);

  const form = useForm<FormValues>({ defaultValues });

  const onSubmit = useCallback((values: FormValues) => {
    // TODO: Temporary for testing purposes
    console.log(values);
  }, []);

  return (
    <FormProvider {...form}>
      <form id={id} className={classes.root} onSubmit={form.handleSubmit(onSubmit)}>
        {title && <h2 className={classes.heading}>{title}</h2>}

        {description && <p>{description}</p>}

        <div className={classes.fields} style={{ '--grid-columns': columns } as CSSProperties}>
          {fields.map((field) => (
            <FormField key={field.id} field={field} />
          ))}
        </div>

        <div className={classes.submit}>
          <Button type="submit" size="md">
            {submit_label}
          </Button>
        </div>
      </form>
    </FormProvider>
  );
}
