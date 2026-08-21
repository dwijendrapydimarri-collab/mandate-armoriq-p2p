import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  MarkerType,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { User, Cpu, Search, CreditCard, Shield, Database, Lock, AlertOctagon, CheckCircle2 } from 'lucide-react';
import { Decision, Delegation } from '../types';

interface AgentGraphProps {
  decisions: Decision[];
  delegations: Delegation[];
  governanceMode: 'on' | 'off';
  onSelectDecision?: (decision: Decision) => void;
}

// Custom Node Components
const CFONode = ({ data }: { data: any }) => (
  <div className="px-4 py-3 rounded-xl bg-slate-900 border-2 border-cyan-500/80 shadow-lg shadow-cyan-950/50 flex items-center gap-3 min-w-[170px]">
    <Handle type="source" position={Position.Bottom} className="!bg-cyan-400" />
    <div className="w-9 h-9 rounded-lg bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center">
      <User className="w-5 h-5 text-cyan-300" />
    </div>
    <div>
      <div className="text-[11px] font-mono text-cyan-400 font-bold uppercase tracking-wider">Named Human</div>
      <div className="text-xs font-semibold text-slate-100">{data.label}</div>
    </div>
  </div>
);

const AgentNode = ({ data }: { data: any }) => {
  const isController = data.role === 'controller';
  const isMatcher = data.role === 'matcher';
  const isDisburser = data.role === 'disburser';

  const borderColor = isController
    ? 'border-indigo-500'
    : isMatcher
    ? 'border-blue-500'
    : 'border-emerald-500';

  const iconBg = isController
    ? 'bg-indigo-500/20 text-indigo-300'
    : isMatcher
    ? 'bg-blue-500/20 text-blue-300'
    : 'bg-emerald-500/20 text-emerald-300';

  return (
    <div className={`px-4 py-3 rounded-xl bg-slate-900 border-2 ${borderColor} shadow-xl min-w-[190px]`}>
      <Handle type="target" position={Position.Top} className="!bg-slate-400" />
      <div className="flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg border flex items-center justify-center ${iconBg}`}>
          <Cpu className="w-5 h-5" />
        </div>
        <div>
          <div className="text-[10px] font-mono text-slate-400 font-semibold uppercase">{data.title}</div>
          <div className="text-xs font-bold text-slate-100">{data.label}</div>
        </div>
      </div>
      <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] font-mono text-slate-400 flex justify-between">
        <span>Cap: {data.capsCount} tools</span>
        <span className="text-slate-200 font-semibold">{data.ceiling}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-slate-400" />
    </div>
  );
};

const ArmorIQBoundaryNode = ({ data }: { data: any }) => {
  const hasBlock = data.hasRecentBlock;
  return (
    <div className={`px-4 py-2.5 rounded-lg border-2 ${hasBlock ? 'bg-rose-950/60 border-rose-500 animate-pulse' : 'bg-emerald-950/40 border-emerald-500/80'} shadow-lg text-center min-w-[240px]`}>
      <Handle type="target" position={Position.Top} className="!bg-emerald-400" />
      <div className="flex items-center justify-center gap-2">
        <Shield className={`w-4 h-4 ${hasBlock ? 'text-rose-400' : 'text-emerald-400'}`} />
        <span className="text-xs font-mono font-bold tracking-wider text-slate-100">
          ARMORIQ POLICY ENFORCER
        </span>
      </div>
      <div className="text-[10px] font-mono text-slate-400 mt-1">
        {hasBlock ? (
          <span className="text-rose-400 font-bold flex items-center justify-center gap-1">
            <AlertOctagon className="w-3 h-3" /> FRAUD STOPPED AT BOUNDARY
          </span>
        ) : (
          <span className="text-emerald-400">Cryptographic Pre-Commitment Active</span>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-emerald-400" />
    </div>
  );
};

const ToolNode = ({ data }: { data: any }) => {
  const isDangerous = data.tool === 'initiate_payment';
  return (
    <div className={`px-3 py-2 rounded-lg bg-slate-900/90 border ${isDangerous ? 'border-rose-500/60' : 'border-slate-700'} shadow text-left min-w-[160px]`}>
      <Handle type="target" position={Position.Top} className="!bg-slate-400" />
      <div className="flex items-center gap-2">
        {isDangerous ? (
          <CreditCard className="w-3.5 h-3.5 text-rose-400" />
        ) : (
          <Database className="w-3.5 h-3.5 text-slate-400" />
        )}
        <span className="text-[11px] font-mono font-semibold text-slate-200">{data.label}</span>
      </div>
      <div className="text-[9px] font-mono text-slate-500 mt-0.5">
        {isDangerous ? 'MOVES MONEY' : data.trust}
      </div>
    </div>
  );
};

const nodeTypes = {
  cfo: CFONode,
  agent: AgentNode,
  armoriq: ArmorIQBoundaryNode,
  tool: ToolNode,
};

export const AgentGraph: React.FC<AgentGraphProps> = ({
  decisions,
  delegations,
  governanceMode,
}) => {
  const lastDecision = decisions.length > 0 ? decisions[decisions.length - 1] : null;
  const hasRecentBlock = decisions.some((d) => d.verdict === 'BLOCK');

  // Nodes Layout
  const initialNodes: Node[] = useMemo(
    () => [
      // Level 1: Human
      {
        id: 'cfo',
        type: 'cfo',
        position: { x: 260, y: 15 },
        data: { label: 'CFO (Vikram Mehta)' },
      },
      // Level 2: Parent Controller Agent
      {
        id: 'controller',
        type: 'agent',
        position: { x: 250, y: 120 },
        data: {
          role: 'controller',
          title: 'Root Orchestrator',
          label: 'Controller Agent',
          capsCount: 3,
          ceiling: 'Total Mission: ₹3,00,000',
        },
      },
      // Level 3: Subagents
      {
        id: 'matcher',
        type: 'agent',
        position: { x: 70, y: 260 },
        data: {
          role: 'matcher',
          title: 'Read-Only Specialist',
          label: 'Matcher Agent',
          capsCount: 1,
          ceiling: 'Ceiling: ₹0 (No Spend)',
        },
      },
      {
        id: 'disburser',
        type: 'agent',
        position: { x: 440, y: 260 },
        data: {
          role: 'disburser',
          title: 'Payment Specialist',
          label: 'Disburser Agent',
          capsCount: 1,
          ceiling: 'Ceiling: ₹50,000 / inv',
        },
      },
      // Level 4: ArmorIQ Boundary
      {
        id: 'armoriq_boundary',
        type: 'armoriq',
        position: { x: 230, y: 400 },
        data: { hasRecentBlock },
      },
      // Level 5: MCP Tools
      {
        id: 'tool_fetch_invoices',
        type: 'tool',
        position: { x: 20, y: 520 },
        data: { label: 'fetch_invoices', tool: 'fetch_invoices', trust: 'UNTRUSTED READ' },
      },
      {
        id: 'tool_initiate_payment',
        type: 'tool',
        position: { x: 460, y: 520 },
        data: { label: 'initiate_payment', tool: 'initiate_payment', trust: 'DANGEROUS WRITE' },
      },
    ],
    [hasRecentBlock]
  );

  // Edges: STROKE WIDTH PROPORTIONAL TO BREADTH OF AUTHORITY
  // CFO -> Controller: width 8px
  // Controller -> Disburser: width 4px
  // Controller -> Matcher: width 2px
  const initialEdges: Edge[] = useMemo(
    () => [
      {
        id: 'e-cfo-controller',
        source: 'cfo',
        target: 'controller',
        style: { strokeWidth: 8, stroke: '#06b6d4' },
        animated: true,
        label: 'Full Spend Mandate',
        labelStyle: { fill: '#67e8f9', fontSize: 10, fontFamily: 'monospace' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' },
      },
      {
        id: 'e-controller-disburser',
        source: 'controller',
        target: 'disburser',
        style: { strokeWidth: 4, stroke: '#10b981' },
        animated: true,
        label: 'Disburse [initiate_payment]',
        labelStyle: { fill: '#34d399', fontSize: 9, fontFamily: 'monospace' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
      },
      {
        id: 'e-controller-matcher',
        source: 'controller',
        target: 'matcher',
        style: { strokeWidth: 2, stroke: '#3b82f6' },
        animated: true,
        label: 'Read [fetch_invoices]',
        labelStyle: { fill: '#93c5fd', fontSize: 9, fontFamily: 'monospace' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
      },
      // Matcher -> Tool fetch_invoices
      {
        id: 'e-matcher-tool',
        source: 'matcher',
        target: 'tool_fetch_invoices',
        style: { strokeWidth: 2, stroke: '#64748b' },
        animated: false,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
      },
      // Disburser -> ArmorIQ Boundary
      {
        id: 'e-disburser-boundary',
        source: 'disburser',
        target: 'armoriq_boundary',
        style: { strokeWidth: 4, stroke: '#10b981' },
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
      },
      // ArmorIQ Boundary -> initiate_payment
      // On blocked call, pulse STOPS DEAD at boundary!
      {
        id: 'e-boundary-payment',
        source: 'armoriq_boundary',
        target: 'tool_initiate_payment',
        style: {
          strokeWidth: 4,
          stroke: hasRecentBlock ? '#f43f5e' : '#10b981',
          strokeDasharray: hasRecentBlock ? '4 4' : undefined,
        },
        animated: !hasRecentBlock,
        label: hasRecentBlock ? 'BLOCKED AT BOUNDARY' : 'ALLOW ONLY',
        labelStyle: { fill: hasRecentBlock ? '#fb7185' : '#34d399', fontSize: 9, fontFamily: 'monospace', fontWeight: 'bold' },
        markerEnd: { type: MarkerType.ArrowClosed, color: hasRecentBlock ? '#f43f5e' : '#10b981' },
      },
    ],
    [hasRecentBlock]
  );

  return (
    <div className="w-full h-full bg-slate-950 relative rounded-xl border border-slate-800 overflow-hidden shadow-inner">
      <div className="absolute top-3 left-3 z-10 bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>ATTENUATION TOPOLOGY: Stroke width ∝ Delegated Authority</span>
        </div>
      </div>

      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-slate-950"
      >
        <Background color="#1e293b" gap={16} size={1} />
        <Controls className="!bg-slate-900 !border-slate-800 !text-slate-300" />
      </ReactFlow>
    </div>
  );
};
