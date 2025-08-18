/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { Checkbox, DatePicker, DatePickerInput, FormGroup, TextInput } from '@carbon/react';
import type { CSSProperties } from 'react';
import { match } from 'ts-pattern';

import type { FormField } from '#api/a2a/extensions/ui/form.ts';

import classes from './FormField.module.scss';
import { MultiSelect } from './MultiSelect';

interface Props {
  field: FormField;
}

export function FormField({ field }: Props) {
  const { col_span } = field;

  return (
    <div className={classes.root} style={{ '--col-span': col_span } as CSSProperties}>
      <FieldRenderer field={field} />
    </div>
  );
}

function FieldRenderer({ field }: Props) {
  const { id, label, required } = field;

  return match(field)
    .with({ type: 'text' }, ({ placeholder, default_value }) => (
      <TextInput
        id={id}
        size="lg"
        labelText={label}
        placeholder={placeholder}
        required={required}
        defaultValue={default_value}
      />
    ))
    .with({ type: 'date' }, ({ placeholder, default_value }) => (
      <DatePicker datePickerType="single" value={default_value}>
        <DatePickerInput id={id} size="lg" labelText={label} placeholder={placeholder} />
      </DatePicker>
    ))
    .with({ type: 'multiselect' }, ({ label, options, default_value }) => (
      <FormGroup legendText={label}>
        <MultiSelect options={options} defaultValue={default_value} />
      </FormGroup>
    ))
    .with({ type: 'checkbox' }, ({ content, default_checked }) => (
      <FormGroup legendText={label}>
        <Checkbox id={id} labelText={content} required={required} defaultChecked={default_checked} />
      </FormGroup>
    ))
    .exhaustive();
}
