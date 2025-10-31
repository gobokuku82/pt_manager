import React from 'react';
import { Card } from './ui/Card';
import { ProgressBar } from './ui/ProgressBar';
import { Badge } from './ui/Badge';
import { CheckCircle2, Loader2, Clock } from 'lucide-react';
import type { ThreeLayerProgressData, ExecutionPlan, ExecutionStep } from '../types';

// Progress Stage Type
export type ProgressStage = "dispatch" | "analysis" | "executing" | "generating";

// Props Types
interface LegacyProgressProps {
  mode: "legacy";
  stage: ProgressStage;
  plan?: ExecutionPlan;
  steps?: ExecutionStep[];
  responsePhase?: "aggregation" | "response_generation";
  reusedTeams?: string[];
}

interface ThreeLayerProgressProps {
  mode: "three-layer";
  progressData: ThreeLayerProgressData;
}

type ProgressContainerProps = LegacyProgressProps | ThreeLayerProgressProps;

// Supervisor Phase Display
const SUPERVISOR_PHASES = {
  dispatching: { title: "요청 분석 중", emoji: "🔍" },
  planning: { title: "실행 계획 수립 중", emoji: "📋" },
  executing: { title: "작업 실행 중", emoji: "⚙️" },
  synthesizing: { title: "결과 종합 중", emoji: "🔄" },
  completed: { title: "완료", emoji: "✅" }
};

// Agent Icons
const AGENT_ICONS: Record<string, string> = {
  search: "🔍",
  analysis: "📊",
  document: "📄"
};

export const ProgressContainer: React.FC<ProgressContainerProps> = (props) => {
  if (props.mode === "three-layer") {
    return <ThreeLayerProgress progressData={props.progressData} />;
  }
  return <LegacyProgress {...props} />;
};

// Legacy Progress Component
const LegacyProgress: React.FC<LegacyProgressProps> = ({ stage, plan, steps, responsePhase }) => {
  const stageInfo = {
    dispatch: { title: "요청 접수", color: "bg-blue-100" },
    analysis: { title: "계획 수립", color: "bg-purple-100" },
    executing: { title: "작업 실행", color: "bg-green-100" },
    generating: { title: "답변 생성", color: "bg-yellow-100" }
  };

  const current = stageInfo[stage];

  return (
    <Card className="p-4">
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <h3 className="font-semibold text-lg">{current.title}</h3>
        </div>

        {plan && stage === "analysis" && (
          <div className="space-y-2">
            <Badge variant="outline">의도: {plan.intent}</Badge>
            <Badge variant="outline">신뢰도: {Math.round(plan.confidence * 100)}%</Badge>
          </div>
        )}

        {steps && steps.length > 0 && (
          <div className="space-y-2">
            {steps.map((step, idx) => (
              <div key={step.id} className="flex items-center gap-2 p-2 rounded border">
                {step.status === "completed" ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : step.status === "in_progress" ? (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                ) : (
                  <Clock className="h-4 w-4 text-gray-400" />
                )}
                <span className="text-sm flex-1">{step.task}</span>
                {step.status === "in_progress" && step.progress_percentage !== undefined && (
                  <span className="text-xs text-gray-500">{step.progress_percentage}%</span>
                )}
              </div>
            ))}
          </div>
        )}

        {responsePhase && (
          <div className="text-sm text-gray-600">
            {responsePhase === "aggregation" ? "결과 수집 중..." : "답변 생성 중..."}
          </div>
        )}
      </div>
    </Card>
  );
};

// Three Layer Progress Component
const ThreeLayerProgress: React.FC<{ progressData: ThreeLayerProgressData }> = ({ progressData }) => {
  const { supervisorPhase, supervisorProgress, activeAgents } = progressData;
  const phaseConfig = SUPERVISOR_PHASES[supervisorPhase];

  return (
    <Card className="p-4">
      <div className="space-y-4">
        {/* Layer 1: Supervisor Phase */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{phaseConfig.emoji}</span>
            <h3 className="font-semibold text-lg">{phaseConfig.title}</h3>
          </div>
          <ProgressBar value={supervisorProgress} showLabel />
        </div>

        {/* Layer 2 & 3: Active Agents and Their Steps */}
        {activeAgents.length > 0 && (
          <div className="space-y-3 mt-4">
            {activeAgents.map((agent) => (
              <div key={agent.agentName} className="border rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">{AGENT_ICONS[agent.agentType] || "🤖"}</span>
                  <span className="font-medium">{agent.agentName}</span>
                  <Badge variant={agent.status === "completed" ? "default" : "outline"}>
                    {agent.status}
                  </Badge>
                  {agent.isReused && <Badge variant="secondary">재사용</Badge>}
                </div>

                <ProgressBar value={agent.overallProgress} size="sm" className="mb-2" />

                {/* Agent Steps */}
                <div className="space-y-1 ml-6">
                  {agent.steps.map((step, idx) => (
                    <div key={step.id} className="flex items-center gap-2 text-sm">
                      {step.status === "completed" ? (
                        <CheckCircle2 className="h-3 w-3 text-green-600" />
                      ) : step.status === "in_progress" ? (
                        <Loader2 className="h-3 w-3 animate-spin text-blue-600" />
                      ) : (
                        <Clock className="h-3 w-3 text-gray-400" />
                      )}
                      <span className="text-gray-700">{step.name}</span>
                      {step.progress !== undefined && step.status === "in_progress" && (
                        <span className="text-xs text-gray-500">{step.progress}%</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};
