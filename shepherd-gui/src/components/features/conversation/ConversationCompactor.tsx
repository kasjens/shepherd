"use client";

/**
 * Conversation Compactor Component - Phase 5
 * 
 * React component for monitoring token usage and managing conversation compacting.
 * Provides real-time token usage display, compacting controls, and warning notifications.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { AlertTriangle, Settings, Zap, Clock, BarChart3, CheckCircle } from 'lucide-react';
import { useConversationStore } from '@/stores/conversation-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';

// Types for conversation compacting
interface TokenUsage {
  conversation_id: string;
  current_tokens: number;
  threshold: number;
  usage_percentage: number;
  needs_compacting: boolean;
  workflow_count: number;
  last_updated: string;
  warning_level: 'none' | 'warning' | 'critical';
}

interface CompactingResult {
  success: boolean;
  conversation_id: string;
  strategy_used: string;
  original_token_count: number;
  compacted_token_count: number;
  reduction_percentage: number;
  segments_processed: number;
  preserved_artifacts_count: number;
  compacting_summary: string;
  timestamp: string;
  error?: string;
}

type CompactingStrategy = 'auto' | 'milestone' | 'selective' | 'aggressive' | 'conservative';

interface CompactDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tokenUsage: TokenUsage | null;
  onCompact: (strategy: CompactingStrategy) => Promise<void>;
  isCompacting: boolean;
}

const CompactDialog: React.FC<CompactDialogProps> = ({
  open,
  onOpenChange,
  tokenUsage,
  onCompact,
  isCompacting
}) => {
  const [selectedStrategy, setSelectedStrategy] = useState<CompactingStrategy>('auto');

  const strategyDescriptions = {
    auto: 'Automatically balance preservation and compression based on content importance',
    milestone: 'Preserve recent content and high-importance milestones',
    selective: 'User-guided preservation with custom rules',
    aggressive: 'Maximum compression, keep only critical content',
    conservative: 'Minimal compression, preserve most content'
  };

  const handleCompact = async () => {
    await onCompact(selectedStrategy);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Compact Conversation
          </DialogTitle>
          <DialogDescription>
            Your conversation is approaching the context limit. Choose a compacting strategy to reduce memory usage while preserving important information.
          </DialogDescription>
        </DialogHeader>

        {tokenUsage && (
          <div className="space-y-4">
            {/* Current Usage Display */}
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Token Usage</span>
                    <span>{tokenUsage.current_tokens.toLocaleString()} / {tokenUsage.threshold.toLocaleString()}</span>
                  </div>
                  <Progress 
                    value={tokenUsage.usage_percentage} 
                    className={`h-2 ${tokenUsage.warning_level === 'critical' ? 'bg-red-100' : 
                      tokenUsage.warning_level === 'warning' ? 'bg-yellow-100' : 'bg-green-100'}`}
                  />
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">
                      {tokenUsage.workflow_count} workflows
                    </span>
                    <Badge variant={tokenUsage.warning_level === 'critical' ? 'destructive' : 
                      tokenUsage.warning_level === 'warning' ? 'secondary' : 'default'}>
                      {tokenUsage.usage_percentage.toFixed(1)}% used
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Strategy Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Compacting Strategy</label>
              <Select value={selectedStrategy} onValueChange={(value: CompactingStrategy) => setSelectedStrategy(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select compacting strategy" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto (Recommended)</SelectItem>
                  <SelectItem value="milestone">Milestone</SelectItem>
                  <SelectItem value="selective">Selective</SelectItem>
                  <SelectItem value="aggressive">Aggressive</SelectItem>
                  <SelectItem value="conservative">Conservative</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                {strategyDescriptions[selectedStrategy]}
              </p>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isCompacting}>
            Cancel
          </Button>
          <Button onClick={handleCompact} disabled={isCompacting}>
            {isCompacting ? (
              <>
                <Clock className="mr-2 h-4 w-4 animate-spin" />
                Compacting...
              </>
            ) : (
              <>
                <Zap className="mr-2 h-4 w-4" />
                Compact Conversation
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

interface CompactingResultDisplayProps {
  result: CompactingResult | null;
  onDismiss: () => void;
}

const CompactingResultDisplay: React.FC<CompactingResultDisplayProps> = ({ result, onDismiss }) => {
  if (!result) return null;

  return (
    <Alert className={result.success ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
      <div className="flex items-start gap-3">
        {result.success ? (
          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
        ) : (
          <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
        )}
        <div className="flex-1 space-y-1">
          <div className="font-medium">
            {result.success ? 'Compacting Completed' : 'Compacting Failed'}
          </div>
          <AlertDescription>
            {result.success ? (
              <>
                Reduced conversation size by {result.reduction_percentage.toFixed(1)}% 
                ({result.original_token_count.toLocaleString()} → {result.compacted_token_count.toLocaleString()} tokens).
                Processed {result.segments_processed} segments and preserved {result.preserved_artifacts_count} critical artifacts.
              </>
            ) : (
              <>Error: {result.error}</>
            )}
          </AlertDescription>
          {result.success && (
            <p className="text-xs text-muted-foreground mt-1">
              {result.compacting_summary}
            </p>
          )}
        </div>
        <Button variant="ghost" size="sm" onClick={onDismiss}>
          ×
        </Button>
      </div>
    </Alert>
  );
};

export const ConversationCompactor: React.FC = () => {
  const { currentConversation } = useConversationStore();
  
  // Component state
  const [tokenUsage, setTokenUsage] = useState<TokenUsage | null>(null);
  const [showCompactDialog, setShowCompactDialog] = useState(false);
  const [isCompacting, setIsCompacting] = useState(false);
  const [compactingResult, setCompactingResult] = useState<CompactingResult | null>(null);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch token usage
  const fetchTokenUsage = useCallback(async () => {
    if (!currentConversation?.id) return;

    try {
      const response = await fetch(`/api/conversations/${currentConversation.id}/token-usage`);
      if (response.ok) {
        const usage: TokenUsage = await response.json();
        setTokenUsage(usage);

        // Auto-show compact dialog if critical
        if (usage.warning_level === 'critical' && !showCompactDialog) {
          setShowCompactDialog(true);
        }
      }
    } catch (error) {
      console.error('Failed to fetch token usage:', error);
    }
  }, [currentConversation?.id, showCompactDialog]);

  // Handle conversation compacting
  const handleCompact = async (strategy: CompactingStrategy) => {
    if (!currentConversation?.id) return;

    setIsCompacting(true);
    try {
      const response = await fetch(`/api/conversations/${currentConversation.id}/compact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: currentConversation.id,
          strategy: strategy
        })
      });

      if (response.ok) {
        const result: CompactingResult = await response.json();
        setCompactingResult(result);
        
        // Refresh token usage after compacting
        setTimeout(fetchTokenUsage, 1000);
      } else {
        throw new Error('Compacting request failed');
      }
    } catch (error) {
      console.error('Compacting failed:', error);
      setCompactingResult({
        success: false,
        conversation_id: currentConversation.id,
        strategy_used: strategy,
        original_token_count: 0,
        compacted_token_count: 0,
        reduction_percentage: 0,
        segments_processed: 0,
        preserved_artifacts_count: 0,
        compacting_summary: '',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsCompacting(false);
    }
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!currentConversation?.id) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/conversation/${currentConversation.id}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      setWsConnection(ws);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        switch (message.type) {
          case 'context_warning':
          case 'auto_compact_suggestion':
            // Update token usage and show warning
            fetchTokenUsage();
            if (message.data.usage_percentage > 90) {
              setShowCompactDialog(true);
            }
            break;
          case 'compacting_completed':
          case 'auto_compact_completed':
            // Update result and refresh usage
            setCompactingResult(message.data);
            fetchTokenUsage();
            break;
          case 'status_update':
            // Update token usage from status
            if (message.data.token_usage) {
              setTokenUsage(message.data.token_usage);
            }
            break;
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      setWsConnection(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [currentConversation?.id, fetchTokenUsage]);

  // Initial token usage fetch
  useEffect(() => {
    fetchTokenUsage();
  }, [fetchTokenUsage]);

  // Auto-refresh token usage every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchTokenUsage, 30000);
    return () => clearInterval(interval);
  }, [fetchTokenUsage]);

  if (!currentConversation || !tokenUsage) {
    return null;
  }

  const getWarningColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  const getWarningIcon = (level: string) => {
    switch (level) {
      case 'critical': return <AlertTriangle className="h-4 w-4" />;
      case 'warning': return <AlertTriangle className="h-4 w-4" />;
      default: return <BarChart3 className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Compacting Result Display */}
      {compactingResult && (
        <CompactingResultDisplay
          result={compactingResult}
          onDismiss={() => setCompactingResult(null)}
        />
      )}

      {/* Token Usage Card */}
      <Card className={`border ${getWarningColor(tokenUsage.warning_level)}`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getWarningIcon(tokenUsage.warning_level)}
              <span>Context Usage</span>
            </div>
            <div className="flex items-center gap-2">
              {isConnected && (
                <Badge variant="outline" className="text-xs">
                  Live
                </Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCompactDialog(true)}
                disabled={isCompacting}
              >
                <Settings className="mr-1 h-3 w-3" />
                Compact
              </Button>
            </div>
          </CardTitle>
          <CardDescription>
            Monitor conversation memory usage and manage compacting
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Usage Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Tokens Used</span>
              <span className="font-mono">
                {tokenUsage.current_tokens.toLocaleString()} / {tokenUsage.threshold.toLocaleString()}
              </span>
            </div>
            <Progress 
              value={tokenUsage.usage_percentage} 
              className="h-2"
            />
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">
                {tokenUsage.workflow_count} workflows • Updated {new Date(tokenUsage.last_updated).toLocaleTimeString()}
              </span>
              <Badge 
                variant={tokenUsage.warning_level === 'critical' ? 'destructive' : 
                  tokenUsage.warning_level === 'warning' ? 'secondary' : 'default'}
              >
                {tokenUsage.usage_percentage.toFixed(1)}%
              </Badge>
            </div>
          </div>

          {/* Warning Message */}
          {tokenUsage.needs_compacting && (
            <Alert className="border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Context usage is high. Consider compacting to free up memory and improve performance.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Compact Dialog */}
      <CompactDialog
        open={showCompactDialog}
        onOpenChange={setShowCompactDialog}
        tokenUsage={tokenUsage}
        onCompact={handleCompact}
        isCompacting={isCompacting}
      />
    </div>
  );
};