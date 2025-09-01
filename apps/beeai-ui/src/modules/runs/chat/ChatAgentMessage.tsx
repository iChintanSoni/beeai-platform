/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { useRef, useState } from 'react';
import { useFocusWithin, useHover } from 'react-aria';

import { Spinner } from '#components/Spinner/Spinner.tsx';
import { MessageFiles } from '#modules/files/components/MessageFiles.tsx';
import { MessageAuth } from '#modules/form/components/MessageAuth.tsx';
import { MessageForm } from '#modules/form/components/MessageForm.tsx';
import { MessageActions } from '#modules/messages/components/MessageActions.tsx';
import { MessageContent } from '#modules/messages/components/MessageContent.tsx';
import { MessageError } from '#modules/messages/components/MessageError.tsx';
import type { UIAgentMessage } from '#modules/messages/types.ts';
import { checkMessageContent, checkMessageStatus } from '#modules/messages/utils.ts';
import { MessageSources } from '#modules/sources/components/MessageSources.tsx';
import { MessageTrajectories } from '#modules/trajectories/components/MessageTrajectories.tsx';

import classes from './ChatAgentMessage.module.scss';

interface Props {
  message: UIAgentMessage;
}

export function ChatAgentMessage({ message }: Props) {
  const contentRef = useRef<HTMLDivElement>(null);

  const [isFocusWithin, setFocusWithin] = useState(false);

  const { hoverProps, isHovered } = useHover({});
  const { focusWithinProps } = useFocusWithin({ onFocusWithinChange: setFocusWithin });

  const hasContent = checkMessageContent(message);
  const { isInProgress } = checkMessageStatus(message);
  const isPending = isInProgress && !hasContent;
  const showActions = !isPending && (isHovered || isFocusWithin);

  return (
    <div {...hoverProps} {...focusWithinProps} className={classes.root}>
      {isPending ? (
        <Spinner center />
      ) : (
        <>
          <div className={classes.content} ref={contentRef}>
            <MessageContent message={message} />
          </div>

          <MessageError message={message} />
        </>
      )}

      <MessageFiles message={message} />

      <MessageSources message={message} />

      <MessageTrajectories message={message} />

      <MessageForm message={message} />

      <MessageAuth message={message} />

      <MessageActions message={message} className={classes.actions} contentRef={contentRef} isVisible={showActions} />
    </div>
  );
}
