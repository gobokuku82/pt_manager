// Execution Step Types
export interface ExecutionStep {
  id: string
  task: string
  description: string
  team: string
  status: "pending" | "in_progress" | "completed" | "failed" | "skipped" | "cancelled"
  progress_percentage?: number
  result?: any
  error?: string
  started_at?: string
  completed_at?: string
}

// Execution Plan Types
export interface ExecutionPlan {
  intent: string
  confidence: number
  execution_steps: ExecutionStep[]
  execution_strategy: string
  estimated_total_time: number
  keywords: string[]
  isLoading?: boolean
}

// Progress Stage
export type ProgressStage = "dispatch" | "analysis" | "executing" | "generating"

// Agent Progress (3-Layer System)
export interface AgentStepProgress {
  id: string
  name: string
  status: "pending" | "in_progress" | "completed" | "failed"
  progress?: number
}

export interface AgentProgress {
  agentName: string
  agentType: string
  steps: AgentStepProgress[]
  currentStepIndex: number
  totalSteps: number
  overallProgress: number
  status: "idle" | "running" | "completed" | "failed"
  isReused?: boolean
}

export type SupervisorPhase = "dispatching" | "planning" | "executing" | "synthesizing" | "completed"

export interface ThreeLayerProgressData {
  supervisorPhase: SupervisorPhase
  supervisorProgress: number
  activeAgents: AgentProgress[]
}

// Answer Display Types
export interface AnswerSection {
  title: string
  content: string | string[]
  icon?: string
  priority?: "high" | "medium" | "low"
  expandable?: boolean
  type?: "text" | "checklist" | "warning"
}

export interface AnswerMetadata {
  confidence: number
  sources: string[]
  intent_type: string
}
