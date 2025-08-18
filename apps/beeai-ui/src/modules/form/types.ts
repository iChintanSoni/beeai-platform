/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type {
  CheckboxFieldValue,
  DateFieldValue,
  FileFieldValue,
  FormResponse,
  MultiSelectFieldValue,
  TextFieldValue,
} from '#api/a2a/extensions/ui/form.ts';

export type FormValues = Record<string, FormResponse['values'][number]['value']>;

export type TextFieldValues = Record<string, TextFieldValue['value']>;
export type DateFieldValues = Record<string, DateFieldValue['value']>;
export type FileFieldValues = Record<string, FileFieldValue['value']>;
export type MultiSelectFieldValues = Record<string, MultiSelectFieldValue['value']>;
export type CheckboxFieldValues = Record<string, CheckboxFieldValue['value']>;
