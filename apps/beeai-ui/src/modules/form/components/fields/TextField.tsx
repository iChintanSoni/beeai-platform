/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { TextInput } from '@carbon/react';
import { useFormContext } from 'react-hook-form';

import type { TextField } from '#api/a2a/extensions/ui/form.ts';
import type { TextFieldValues } from '#modules/form/types.ts';

interface Props {
  field: TextField;
}

export function TextField({ field }: Props) {
  const { id, label, placeholder, required } = field;

  const { register } = useFormContext<TextFieldValues>();

  return <TextInput id={id} size="lg" labelText={label} placeholder={placeholder} {...register(id, { required })} />;
}
