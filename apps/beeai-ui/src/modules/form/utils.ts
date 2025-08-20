/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { match } from 'ts-pattern';

import type { FormField } from '#api/a2a/extensions/ui/form.ts';
import { getFilePlatformUrl } from '#api/a2a/utils.ts';
import type { FileEntity } from '#modules/files/types.ts';

import type { FormValues } from './types';

export function getDefaultValues(fields: FormField[]) {
  const defaultValues: FormValues = Object.fromEntries(
    fields.map((field) =>
      match(field)
        .with(
          { type: 'text' },
          { type: 'date' },
          { type: 'multiselect' },
          { type: 'checkbox' },
          ({ id, default_value }) => [id, default_value],
        )
        .otherwise(({ id }) => [id, undefined]),
    ),
  );

  return defaultValues;
}

export function convertFileToFileFieldValue(file: FileEntity) {
  const { uploadFile, originalFile } = file;

  if (!uploadFile) {
    return;
  }

  const { id, filename } = uploadFile;
  const { type } = originalFile;

  const value = {
    uri: getFilePlatformUrl(id),
    name: filename,
    mime_type: type,
  };

  return value;
}
