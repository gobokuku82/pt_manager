"use client"

import React from "react"
import { Card } from "@/components/ui/card"
import { ProgressBar } from "@/components/ui/progress-bar"
import type { ExecutionStep, ExecutionPlan } from "@/types/execution"

export type ProgressStage = "dispatch" | "analysis" | "executing" | "generating"

export interface ProgressContainerProps {
  stage: ProgressStage
  plan?: ExecutionPlan
  steps?: ExecutionStep[]
  responsePhase?: "aggregation" | "response_generation"
  reusedTeams?: string[]  // 🆕 Option A: 재사용된 팀 리스트
}

// Stage 설정
const STAGE_CONFIG = {
  dispatch: {
    index: 0,
    title: "출동 중",
    spinner: "/animation/spinner/1_execution-plan_spinner.gif"
  },
  analysis: {
    index: 1,
    title: "분석 중",
    spinner: "/animation/spinner/2_execution-progress_spinner.gif"
  },
  executing: {
    index: 2,
    title: "실행 중",
    spinner: "/animation/spinner/3_execution-progress_spinner.gif"
  },
  generating: {
    index: 3,
    title: "답변 작성 중",
    spinner: "/animation/spinner/4_response-generating_spinner.gif"
  }
} as const

export function ProgressContainer({
  stage,
  plan,
  steps = [],
  responsePhase = "aggregation",
  reusedTeams = []  // 🆕 Option A: 재사용된 팀 리스트
}: ProgressContainerProps) {
  const currentStage = STAGE_CONFIG[stage]
  const allStages = Object.values(STAGE_CONFIG)

  // 전체 프로세스 진행률 계산
  const calculateOverallProgress = (): number => {
    switch (stage) {
      case "dispatch":
        return 10  // 출동 중: 10%

      case "analysis":
        // 분석 중: 25-40%
        if (plan && !plan.isLoading && plan.execution_steps && plan.execution_steps.length > 0) {
          return 40  // plan_ready 완료
        }
        return 25  // 분석 시작

      case "executing":
        // 실행 중: 40-75%
        const totalSteps = steps.length
        const completedSteps = steps.filter(s => s.status === "completed").length
        if (totalSteps > 0) {
          const executionProgress = (completedSteps / totalSteps) * 35  // 35% 범위
          return 40 + executionProgress
        }
        return 40

      case "generating":
        // 답변 작성 중: 75-95%
        if (responsePhase === "response_generation") {
          return 90  // 최종 답변 생성 중
        }
        return 80  // 정보 정리 중

      default:
        return 0
    }
  }

  const overallProgress = calculateOverallProgress()

  return (
    <div className="flex justify-start mb-2">
      <div className="flex items-start gap-3 max-w-5xl w-full">
        <Card className="p-3 bg-card border flex-1">
          {/* 전체 프로세스 진행률 */}
          <div className="mb-3 p-2 bg-primary/5 rounded-lg border border-primary/20">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-primary">전체 진행률</span>
              <span className="text-xs font-bold text-primary">{Math.round(overallProgress)}%</span>
            </div>
            <ProgressBar
              value={overallProgress}
              size="md"
              variant="default"
              showLabel={false}
            />
          </div>

          {/* 상단: 4-Stage Spinner Bar */}
          <div className="grid grid-cols-4 mb-2">
            {allStages.map((s, idx) => (
              <div key={idx} className="flex flex-col items-center justify-start">
                {/* 스피너 */}
                <div
                  className={`
                    w-full aspect-square transition-all duration-150 ease-in-out
                    ${
                      idx === currentStage.index
                        ? "opacity-100 grayscale-0 scale-110"
                        : "opacity-40 grayscale scale-90"
                    }
                  `}
                >
                  <img
                    src={s.spinner}
                    alt={s.title}
                    className="w-full h-full object-contain"
                  />
                </div>

                {/* 스테이지 레이블 */}
                <div
                  className={`
                    font-bold transition-all duration-150 leading-none
                    ${
                      idx === currentStage.index
                        ? "text-2xl text-foreground opacity-100 scale-110 -mt-4"
                        : "text-base text-muted-foreground opacity-40 scale-75 -mt-3"
                    }
                  `}
                  style={{ fontFamily: "'Hi Melody', cursive" }}
                >
                  {s.title}
                </div>
              </div>
            ))}
          </div>

          {/* 하단: Content Area (Stage별 변경) */}
          <div className="min-h-[120px]">
            {stage === "dispatch" && <DispatchContent />}
            {stage === "analysis" && <AnalysisContent plan={plan} />}
            {stage === "executing" && <ExecutingContent steps={steps} reusedTeams={reusedTeams} />}
            {stage === "generating" && <GeneratingContent phase={responsePhase} />}
          </div>
        </Card>
      </div>
    </div>
  )
}

// ============================================================================
// Stage 1: Dispatch Content
// ============================================================================
function DispatchContent() {
  return (
    <div className="text-center py-4">
      <div className="animate-pulse">
        <div className="text-base font-semibold">질문을 접수했습니다</div>
        <div className="text-sm text-muted-foreground mt-1">
          잠시만 기다려주세요...
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Stage 2: Analysis Content
// ============================================================================
function AnalysisContent({ plan }: { plan?: ExecutionPlan }) {
  return (
    <div className="space-y-3">
      <div className="text-center">
        <div className="text-base font-semibold">질문을 분석하고 있습니다</div>
      </div>

      {/* plan_ready 신호 수신 후 표시 */}
      {plan && !plan.isLoading && plan.execution_steps && plan.execution_steps.length > 0 && (
        <div className="space-y-2">
          {/* 의도 분석 결과 */}
          <div className="p-3 bg-secondary/30 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">분석 완료</span>
              <span className="text-sm text-muted-foreground">{plan.intent}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">신뢰도:</span>
              <ProgressBar
                value={(plan.confidence || 0) * 100}
                size="sm"
                variant="default"
              />
              <span className="text-xs font-medium">
                {((plan.confidence || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* 작업 계획 */}
          <div className="space-y-2">
            <div className="font-medium">작업 계획:</div>
            {plan.execution_steps.map((step, idx) => (
              <div
                key={step.step_id || idx}
                className="flex items-center gap-3 p-2 bg-muted/50 rounded"
              >
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-medium">
                  {idx + 1}
                </div>
                <div className="text-sm">{step.task || step.description}</div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              곧 작업을 시작합니다...
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Stage 3: Executing Content
// ============================================================================
function ExecutingContent({ steps, reusedTeams = [] }: { steps: ExecutionStep[]; reusedTeams?: string[] }) {
  // 🆕 Option A: 재사용된 팀을 가상 Step으로 변환
  const reusedSteps: ExecutionStep[] = reusedTeams.map((teamName, idx) => ({
    step_id: `reused-${teamName}-${idx}`,
    task: `${teamName.charAt(0).toUpperCase() + teamName.slice(1)} Team`,
    description: `${teamName} 데이터 재사용`,
    status: "completed" as const,
    agent: teamName,
    isReused: true  // 🆕 재사용 플래그
  }))

  // 🆕 실제 실행 steps와 재사용 steps를 병합
  const allSteps = [...reusedSteps, ...steps]

  const totalSteps = allSteps.length
  const completedSteps = allSteps.filter((s) => s.status === "completed").length
  const failedSteps = allSteps.filter((s) => s.status === "failed").length
  const overallProgress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0

  return (
    <div className="space-y-3">
      {/* 전체 진행률 */}
      <div className="p-3 bg-secondary/20 rounded-lg border border-border">
        <div className="flex items-center justify-between mb-2">
          <span className="font-semibold text-base">전체 작업 진행률</span>
          <span className="text-sm font-medium text-primary">
            {completedSteps}/{totalSteps} 완료
          </span>
        </div>
        <ProgressBar
          value={overallProgress}
          size="lg"
          variant={failedSteps > 0 ? "warning" : "default"}
          showLabel={true}
        />
      </div>

      {/* 에이전트 카드들 (동적 1~N개) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {allSteps.map((step) => (
          <AgentCard key={step.step_id} step={step} />
        ))}
      </div>

      {/* 실패한 작업이 있을 경우 */}
      {failedSteps > 0 && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-xs text-red-700 dark:text-red-400">
            {failedSteps}개의 작업이 실패했습니다. 일부 정보가 누락될 수 있습니다.
          </p>
        </div>
      )}
    </div>
  )
}

// Agent Card Component
function AgentCard({ step }: { step: ExecutionStep }) {
  const statusConfig = {
    pending: {
      icon: "○",
      color: "text-muted-foreground",
      bg: "bg-muted",
      borderColor: "border-muted-foreground/20"
    },
    in_progress: {
      icon: "●",
      color: "text-primary",
      bg: "bg-primary/10",
      borderColor: "border-primary"
    },
    completed: {
      icon: "✓",
      color: "text-green-600",
      bg: "bg-green-50 dark:bg-green-900/20",
      borderColor: "border-green-200 dark:border-green-800"
    },
    failed: {
      icon: "✗",
      color: "text-red-600",
      bg: "bg-red-50 dark:bg-red-900/20",
      borderColor: "border-red-200 dark:border-red-800"
    },
    skipped: {
      icon: "⊘",
      color: "text-yellow-600",
      bg: "bg-yellow-50 dark:bg-yellow-900/20",
      borderColor: "border-yellow-200 dark:border-yellow-800"
    }
  }

  const config = statusConfig[step.status] || statusConfig.pending

  return (
    <div className={`p-3 rounded-lg border ${config.bg} ${config.borderColor}`}>
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-xl ${config.color}`}>{config.icon}</span>
        <span className="font-medium text-sm">{step.task}</span>
        {/* 🆕 Option A: 재사용 배지 */}
        {step.isReused && (
          <span className="ml-auto px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
            ♻️ 재사용
          </span>
        )}
      </div>
      <div className="text-xs text-muted-foreground mb-2">{step.description}</div>

      {/* 진행 중일 때 진행률 BAR 표시 */}
      {step.status === "in_progress" && step.progress !== undefined && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">진행률</span>
            <span className="font-medium text-primary">{Math.round(step.progress)}%</span>
          </div>
          <ProgressBar
            value={step.progress}
            size="md"
            variant="default"
            showLabel={false}
          />
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Stage 4: Generating Content
// ============================================================================
function GeneratingContent({ phase }: { phase?: "aggregation" | "response_generation" }) {
  // AgentCard 스타일과 동일한 상태 설정
  const statusConfig = {
    pending: {
      icon: "○",
      color: "text-muted-foreground",
      bg: "bg-muted",
      borderColor: "border-muted-foreground/20"
    },
    in_progress: {
      icon: "●",
      color: "text-primary",
      bg: "bg-primary/10",
      borderColor: "border-primary"
    },
    completed: {
      icon: "✓",
      color: "text-green-600",
      bg: "bg-green-50 dark:bg-green-900/20",
      borderColor: "border-green-200 dark:border-green-800"
    }
  }

  const steps: Array<{ id: string; label: string; status: "pending" | "in_progress" | "completed" }> = [
    { id: "collect", label: "데이터 수집 완료", status: "completed" },
    {
      id: "organize",
      label: "정보 정리 중",
      status: phase === "aggregation" ? "in_progress" : "completed"
    },
    {
      id: "generate",
      label: "최종 답변 생성 중",
      status: phase === "response_generation" ? "in_progress" : "pending"
    }
  ]

  return (
    <div className="space-y-3">
      {/* AgentCard 스타일의 3단계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        {steps.map((step) => {
          const config = statusConfig[step.status]
          return (
            <div
              key={step.id}
              className={`p-2 rounded-lg border ${config.bg} ${config.borderColor}`}
            >
              <div className="flex items-center gap-2">
                <span className={`text-lg ${config.color}`}>{config.icon}</span>
                <span className="font-medium text-xs">{step.label}</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* 안내 메시지 */}
      <div className="text-center text-xs text-muted-foreground pt-2 border-t border-border">
        잠시만 기다려주세요. 최적의 답변을 준비하고 있습니다.
      </div>
    </div>
  )
}
