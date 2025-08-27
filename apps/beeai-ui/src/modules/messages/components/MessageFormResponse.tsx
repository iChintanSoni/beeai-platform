/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { useMemo } from 'react';
import { match } from 'ts-pattern';

import type { CheckboxField, DateField, FormField, MultiSelectField, TextField } from '#api/a2a/extensions/ui/form.ts';
import type { ValueOfField } from '#modules/form/types.ts';
import { isNotNull } from '#utils/helpers.ts';

import type { UIMessageForm } from '../types';

interface Props {
  form: UIMessageForm;
}

export function MessageFormResponse({ form }: Props) {
  const data: FieldWithValue[] = useMemo(() => {
    return form.request.fields
      .map((field) => {
        const value = form.response.values[field.id];
        return value && value.type === field.type ? ({ ...field, value: value.value } as FieldWithValue) : null;
      })
      .filter(isNotNull);
  }, [form.request.fields, form.response.values]);

  return (
    <>
      {data.map((field) => {
        const { id, label } = field;
        return (
          <p key={id}>
            {label}: <FormValueRenderer field={field} />
          </p>
        );
      })}
    </>
  );
}

function FormValueRenderer({ field }: { field: FieldWithValue }) {
  return (
    <>
      {match(field)
        .with({ type: 'text' }, { type: 'date' }, ({ value }) => value)
        .with({ type: 'checkbox' }, ({ value, content }) => (value ? (content ?? 'yes') : 'no'))
        .with({ type: 'multiselect' }, ({ value }) => value?.join(', '))
        .otherwise(() => null)}
    </>
  );
}

type FieldWithValueMapper<F extends FormField> = F & { value: ValueOfField<F>['value'] };
type FieldWithValue =
  | FieldWithValueMapper<TextField>
  | FieldWithValueMapper<DateField>
  | FieldWithValueMapper<CheckboxField>
  | FieldWithValueMapper<MultiSelectField>;
