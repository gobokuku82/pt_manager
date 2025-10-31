import React, { useState } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from './ui/Card';
import { Badge } from './ui/Badge';
import { Alert, AlertDescription } from './ui/Alert';
import { ProgressBar } from './ui/ProgressBar';
import {
  AlertCircle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Info,
  FileText
} from 'lucide-react';
import type { AnswerSection, AnswerMetadata } from '../types';

interface AnswerDisplayProps {
  sections: AnswerSection[];
  metadata: AnswerMetadata;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ sections, metadata }) => {
  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">답변</h2>
          <div className="flex gap-2">
            <Badge variant="outline">
              의도: {metadata.intent_type}
            </Badge>
            <Badge variant={metadata.confidence > 0.7 ? 'default' : 'secondary'}>
              신뢰도: {Math.round(metadata.confidence * 100)}%
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {sections.map((section, idx) => (
            <AnswerSectionComponent key={idx} section={section} />
          ))}
        </div>
      </CardContent>

      {metadata.sources && metadata.sources.length > 0 && (
        <CardFooter>
          <div className="w-full">
            <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              참고 자료
            </h4>
            <ul className="text-sm text-gray-600 space-y-1">
              {metadata.sources.map((source, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-gray-400">•</span>
                  <span>{source}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardFooter>
      )}

      {/* Confidence Bar */}
      <div className="px-6 pb-4">
        <div className="text-xs text-gray-500 mb-1">신뢰도</div>
        <ProgressBar value={metadata.confidence * 100} size="sm" />
      </div>
    </Card>
  );
};

const AnswerSectionComponent: React.FC<{ section: AnswerSection }> = ({ section }) => {
  const [isExpanded, setIsExpanded] = useState(!section.expandable);

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      case 'low':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  const getIcon = () => {
    if (section.type === 'warning') return <AlertCircle className="h-5 w-5 text-yellow-600" />;
    if (section.type === 'checklist') return <CheckCircle className="h-5 w-5 text-green-600" />;
    return <Info className="h-5 w-5 text-blue-600" />;
  };

  const renderContent = () => {
    if (Array.isArray(section.content)) {
      if (section.type === 'checklist') {
        return (
          <ul className="space-y-2">
            {section.content.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        );
      }
      return (
        <ul className="space-y-2">
          {section.content.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-gray-400">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      );
    }
    return <p className="whitespace-pre-wrap">{section.content}</p>;
  };

  if (section.type === 'warning') {
    return (
      <Alert variant="warning">
        <AlertDescription>
          <div className="font-semibold mb-2">{section.title}</div>
          {renderContent()}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className={`rounded-lg border p-4 ${getPriorityColor(section.priority)}`}>
      <div
        className="flex items-start justify-between cursor-pointer"
        onClick={() => section.expandable && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start gap-3 flex-1">
          {getIcon()}
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2">{section.title}</h3>
            {isExpanded && (
              <div className="text-sm text-gray-700">{renderContent()}</div>
            )}
          </div>
        </div>
        {section.expandable && (
          <button className="ml-2 p-1">
            {isExpanded ? (
              <ChevronUp className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            )}
          </button>
        )}
      </div>
    </div>
  );
};
