/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { z } from 'zod';

import { getFileContentUrl } from '#modules/files/utils.ts';

import type { A2AUiExtension } from '../types';

const URI = 'https://a2a-extensions.beeai.dev/ui/form/v1';

const baseField = z.object({
  id: z.string().nonempty(),
  label: z.string().nonempty(),
  required: z.boolean().optional(),
  col_span: z.number().int().min(1).max(4).optional(),
});

const textField = baseField.extend({
  type: z.literal('text'),
  placeholder: z.string().optional(),
  default_value: z.string().optional(),
});

const textFieldValue = z.object({
  type: textField.shape.type,
  value: z.string().optional(),
});

const dateField = baseField.extend({
  type: z.literal('date'),
  placeholder: z.string().optional(),
  default_value: z.string().optional(),
});

const dateFieldValue = z.object({
  type: dateField.shape.type,
  value: z.string().optional(),
});

const fileField = baseField.extend({
  type: z.literal('file'),
  accept: z.array(z.string()),
});

const fileFieldValue = z.object({
  type: fileField.shape.type,
  value: z
    .array(
      z.object({
        uri: z.string(),
        name: z.string().optional(),
        mime_type: z.string().optional(),
      }),
    )
    .optional(),
});

const multiSelectField = baseField.extend({
  type: z.literal('multiselect'),
  options: z
    .array(
      z.object({
        id: z.string().nonempty(),
        label: z.string().nonempty(),
      }),
    )
    .nonempty(),
  default_value: z.array(z.string()).optional(),
});

const multiSelectFieldValue = z.object({
  type: multiSelectField.shape.type,
  value: z.array(z.string()).optional(),
});

const checkboxField = baseField.extend({
  type: z.literal('checkbox'),
  content: z.string(),
  default_value: z.boolean().optional(),
});

const checkboxFieldValue = z.object({
  type: checkboxField.shape.type,
  value: z.boolean().optional(),
});

const fieldSchema = z.discriminatedUnion('type', [textField, dateField, fileField, multiSelectField, checkboxField]);

const renderSchema = z.object({
  type: z.literal('render'),
  id: z.string().nonempty(),
  title: z.string().optional(),
  description: z.string().optional(),
  columns: z.number().int().min(1).max(4).optional(),
  submit_label: z.string().optional(),
  fields: z.array(fieldSchema).nonempty(),
});

const responseSchema = z.object({
  type: z.literal('response'),
  id: z.string().nonempty(),
  values: z.record(
    z.discriminatedUnion('type', [
      textFieldValue,
      dateFieldValue,
      fileFieldValue,
      multiSelectFieldValue,
      checkboxFieldValue,
    ]),
  ),
});

const schema = z.discriminatedUnion('type', [renderSchema, responseSchema]);

export type TextField = z.infer<typeof textField>;
export type DateField = z.infer<typeof dateField>;
export type FileField = z.infer<typeof fileField>;
export type MultiSelectField = z.infer<typeof multiSelectField>;
export type CheckboxField = z.infer<typeof checkboxField>;

export type FormField = z.infer<typeof fieldSchema>;

export type TextFieldValue = z.infer<typeof textFieldValue>;
export type DateFieldValue = z.infer<typeof dateFieldValue>;
export type FileFieldValue = z.infer<typeof fileFieldValue>;
export type MultiSelectFieldValue = z.infer<typeof multiSelectFieldValue>;
export type CheckboxFieldValue = z.infer<typeof checkboxFieldValue>;

export type FormRender = z.infer<typeof renderSchema>;
export type FormResponse = z.infer<typeof responseSchema>;
export type FormMetadata = z.infer<typeof schema>;

export const formExtension: A2AUiExtension<typeof URI, FormMetadata> = {
  getMessageMetadataSchema: () => z.object({ [URI]: schema }).partial(),
  getUri: () => URI,
};

// TODO: Temporary for testing purposes
export const formExtensionRenderExample: FormRender = {
  type: 'render',
  id: 'form-id',
  title: 'Let’s go on an adventure',
  description: 'Tell me where and whether you are flexible.',
  columns: 2,
  submit_label: 'Continue',
  fields: [
    {
      id: 'location',
      type: 'text',
      label: 'Location',
      placeholder: 'e.g., Japan',
      required: true,
      default_value: 'Japan',
    },
    {
      id: 'departure',
      type: 'date',
      label: 'Departure',
      placeholder: 'mm/dd/yyyy',
      col_span: 1,
      default_value: '12/01/2025',
    },
    {
      id: 'return',
      type: 'date',
      label: 'Return',
      placeholder: 'mm/dd/yyyy',
      col_span: 1,
    },
    {
      id: 'flexible',
      type: 'checkbox',
      label: 'Do you have flexibility with your travel dates?',
      content: 'Yes, I’m flexible',
      default_value: true,
    },
    {
      id: 'notes',
      type: 'file',
      label: 'Upload notes',
      accept: ['text/plain'],
    },
    {
      id: 'interests',
      type: 'multiselect',
      label: 'Interests',
      options: [
        { id: 'cuisine', label: 'Cuisine' },
        { id: 'nature', label: 'Nature' },
        { id: 'nightlife', label: 'Nightlife' },
        { id: 'photography', label: 'Photography' },
        { id: 'volunteering', label: 'Volunteering' },
        { id: 'business', label: 'Business' },
      ],
      default_value: ['cuisine', 'nature'],
    },
  ],
};

// TODO: Temporary for testing purposes
export const formExtensionResponseExample: FormResponse = {
  type: 'response',
  id: 'form-id',
  values: {
    location: {
      type: 'text',
      value: 'Japan',
    },
    departure: {
      type: 'date',
      value: '10/01/2025',
    },
    return: {
      type: 'date',
      value: '10/15/2025',
    },
    flexible: {
      type: 'checkbox',
      value: true,
    },
    notes: {
      type: 'file',
      value: [
        {
          uri: getFileContentUrl({ id: '21be044d-8052-46ef-b1ed-d93fa2cba31e' }),
          name: 'test.txt',
          mime_type: 'text/plain',
        },
      ],
    },
    interests: {
      type: 'multiselect',
      value: ['cuisine', 'nightlife', 'photography'],
    },
  },
};
