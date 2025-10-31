import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { ProgressContainer } from './components/ProgressContainer';
import { AnswerDisplay } from './components/AnswerDisplay';
import { Card } from './components/ui/Card';
import { WebSocketClient, WSMessage } from './lib/websocket';
import type { ThreeLayerProgressData, AnswerSection, AnswerMetadata } from './types';

interface Message {
  id: string;
  type: 'user' | 'bot' | 'progress';
  content: string;
  timestamp: Date;
  progressData?: ThreeLayerProgressData;
  structuredData?: {
    sections: AnswerSection[];
    metadata: AnswerMetadata;
  };
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: '안녕하세요! AI Assistant입니다. 무엇을 도와드릴까요?',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const wsRef = useRef<WebSocketClient | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/chat/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: '새 대화' }),
        });
        const data = await response.json();
        setSessionId(data.id);
        console.log('Session created:', data.id);
      } catch (error) {
        console.error('Failed to create session:', error);
      }
    };
    initSession();
  }, []);

  // Initialize WebSocket
  useEffect(() => {
    if (!sessionId) return;

    const handleMessage = (message: WSMessage) => {
      console.log('Received:', message.type);

      switch (message.type) {
        case 'plan_ready':
          // Update progress with plan
          break;

        case 'supervisor_phase_change':
          // Update 3-layer progress
          setMessages((prev) =>
            prev.map((msg) =>
              msg.type === 'progress' && msg.progressData
                ? {
                    ...msg,
                    progressData: {
                      ...msg.progressData,
                      supervisorPhase: message.supervisorPhase,
                      supervisorProgress: message.supervisorProgress || 0,
                    },
                  }
                : msg
            )
          );
          break;

        case 'agent_steps_initialized':
          // Add new agent to progress
          setMessages((prev) =>
            prev.map((msg) =>
              msg.type === 'progress' && msg.progressData
                ? {
                    ...msg,
                    progressData: {
                      ...msg.progressData,
                      activeAgents: [
                        ...msg.progressData.activeAgents,
                        {
                          agentName: message.agentName,
                          agentType: message.agentType,
                          steps: message.steps,
                          currentStepIndex: 0,
                          totalSteps: message.steps.length,
                          overallProgress: 0,
                          status: 'running',
                        },
                      ],
                    },
                  }
                : msg
            )
          );
          break;

        case 'final_response':
          // Remove progress and add bot response
          setMessages((prev) => prev.filter((m) => m.type !== 'progress'));
          const botMessage: Message = {
            id: Date.now().toString(),
            type: 'bot',
            content: message.response?.answer || message.response?.content || '응답을 받지 못했습니다.',
            structuredData: message.response?.structured_data,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, botMessage]);
          setIsProcessing(false);
          break;

        case 'error':
          console.error('Server error:', message.error);
          setIsProcessing(false);
          break;
      }
    };

    const wsUrl = `ws://localhost:8000/api/v1/chat/ws/${sessionId}`;
    wsRef.current = new WebSocketClient(wsUrl, handleMessage);
    wsRef.current.connect();

    return () => {
      wsRef.current?.disconnect();
    };
  }, [sessionId]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim() || !wsRef.current || isProcessing) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    // Add progress message
    const progressMessage: Message = {
      id: `progress-${Date.now()}`,
      type: 'progress',
      content: '',
      timestamp: new Date(),
      progressData: {
        supervisorPhase: 'dispatching',
        supervisorProgress: 0,
        activeAgents: [],
      },
    };

    setMessages((prev) => [...prev, userMessage, progressMessage]);
    setInputValue('');
    setIsProcessing(true);

    // Send via WebSocket
    wsRef.current.send({
      type: 'query',
      query: inputValue,
      enable_checkpointing: true,
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
          <p className="text-sm text-gray-600">Multi-Agent Framework</p>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div key={message.id}>
              {message.type === 'progress' && message.progressData && (
                <div className="flex justify-start">
                  <div className="flex gap-3 max-w-3xl">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                      <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <ProgressContainer mode="three-layer" progressData={message.progressData} />
                    </div>
                  </div>
                </div>
              )}

              {message.type === 'user' && (
                <div className="flex justify-end">
                  <div className="flex gap-3 max-w-3xl">
                    <Card className="p-3 bg-blue-600 text-white">
                      <p className="text-sm">{message.content}</p>
                    </Card>
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                      <User className="h-4 w-4 text-gray-700" />
                    </div>
                  </div>
                </div>
              )}

              {message.type === 'bot' && (
                <div className="flex justify-start">
                  <div className="flex gap-3 max-w-3xl">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                      <Bot className="h-6 w-6 text-white" />
                    </div>
                    {message.structuredData ? (
                      <AnswerDisplay
                        sections={message.structuredData.sections}
                        metadata={message.structuredData.metadata}
                      />
                    ) : (
                      <Card className="p-3">
                        <p className="text-sm">{message.content}</p>
                      </Card>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="bg-white border-t shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="메시지를 입력하세요..."
              disabled={isProcessing}
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <button
              onClick={handleSend}
              disabled={isProcessing || !inputValue.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="h-4 w-4" />
              전송
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
