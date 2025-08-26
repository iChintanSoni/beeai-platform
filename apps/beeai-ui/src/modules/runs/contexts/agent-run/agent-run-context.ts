/**
 * Copyright 2025 © BeeAI a Series of LF Projects, LLC
 * SPDX-License-Identifier: Apache-2.0
 */
'use client';
import { createContext } from 'react';

import type { FormRender } from '#api/a2a/extensions/ui/form.ts';
import type { Agent } from '#modules/agents/api/types.ts';
import type { UIMessageForm } from '#modules/messages/types.ts';
import type { RunStats } from '#modules/runs/types.ts';

export const AgentRunContext = createContext<AgentRunContextValue | undefined>(undefined);

interface AgentRunContextValue {
  agent: Agent;
  isPending: boolean;
  input?: string;
  stats?: RunStats;
  formRender?: FormRender;
  run: (params: AgentRunParams) => Promise<void>;
  cancel: () => void;
  clear: () => void;
}

export interface AgentRunParams {
  input?: string;
  form?: UIMessageForm;
  taskId?: string;
}
