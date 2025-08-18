/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { OperationalTag } from '@carbon/react';
import clsx from 'clsx';

import type { MultiSelectField } from '#api/a2a/extensions/ui/form.ts';

import classes from './MultiSelect.module.scss';

interface Props {
  options: MultiSelectField['options'];
  defaultValue?: MultiSelectField['default_value'];
}

export function MultiSelect({ options, defaultValue }: Props) {
  return (
    <ul className={classes.root}>
      {options.map(({ id, label }) => {
        // TODO: Temporary for testing purposes
        const isSelected = defaultValue?.includes(id);

        return (
          <li key={id}>
            <OperationalTag
              text={label}
              size="lg"
              className={clsx(classes.option, { [classes.isSelected]: isSelected })}
            />
          </li>
        );
      })}
    </ul>
  );
}
