/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { z } from 'zod';

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

const dateField = baseField.extend({
  type: z.literal('date'),
  placeholder: z.string().optional(),
  default_value: z.string().optional(),
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

const checkboxField = baseField.extend({
  type: z.literal('checkbox'),
  content: z.string(),
  default_checked: z.boolean().optional(),
});

const fieldSchema = z.discriminatedUnion('type', [textField, dateField, multiSelectField, checkboxField]);

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
      z.object({ type: textField.shape.type, value: z.string() }),
      z.object({ type: dateField.shape.type, value: z.string() }),
      z.object({ type: multiSelectField.shape.type, value: z.array(z.string()) }),
      z.object({ type: checkboxField.shape.type, value: z.boolean() }),
    ]),
  ),
});

const schema = z.discriminatedUnion('type', [renderSchema, responseSchema]);

export type TextField = z.infer<typeof textField>;
export type DateField = z.infer<typeof dateField>;
export type MultiSelectField = z.infer<typeof multiSelectField>;
export type CheckboxField = z.infer<typeof checkboxField>;

export type FormField = z.infer<typeof fieldSchema>;

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
    },
    {
      id: 'departure',
      type: 'date',
      label: 'Departure',
      placeholder: 'mm/dd/yyyy',
      col_span: 1,
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
      default_checked: true,
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
    },
  ],
};

// TODO: Temporary for testing purposes
export const formExtensionResponseExample: FormResponse = {
  type: 'response',
  id: 'form-id',
  values: {
    location: { type: 'text', value: 'Japan' },
    departure: { type: 'date', value: '10/01/2025' },
    return: { type: 'date', value: '10/15/2025' },
    flexible: { type: 'checkbox', value: true },
    interests: { type: 'multiselect', value: ['cuisine', 'nightlife', 'photography'] },
  },
};
