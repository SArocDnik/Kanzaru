import ReactFlow, {
  Background,
  Controls,
  type Node,
  type Edge,
  Position,
} from "reactflow"
import "reactflow/dist/style.css"
import type { RelationshipData } from "../types"

const EDGE_COLORS: Record<string, string> = {
  family: "#f59e0b",
  romantic: "#ec4899",
  friendship: "#10b981",
  rivalry: "#ef4444",
  master_servant: "#8b5cf6",
  other: "#6b7280",
}

function buildLayout(nodes: { id: number; name: string }[]) {
  const radius = Math.max(150, nodes.length * 30)
  const cx = 300
  const cy = 200
  return nodes.map((n, i) => {
    const angle = (2 * Math.PI * i) / Math.max(nodes.length, 1)
    return {
      id: String(n.id),
      data: { label: n.name },
      position: { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    }
  })
}

export default function CharacterGraph({ data }: { data: RelationshipData }) {
  if (!data.nodes || data.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        No character data. Analyze chapters first.
      </div>
    )
  }

  const nodes: Node[] = buildLayout(data.nodes)
  const edges: Edge[] = data.edges.map((e, i) => ({
    id: `e${i}`,
    source: String(e.source),
    target: String(e.target),
    label: e.rel_type,
    style: { stroke: EDGE_COLORS[e.rel_type] ?? "#6b7280", strokeWidth: 2 },
    labelStyle: { fontSize: 11, fill: "#374151" },
  }))

  return (
    <div className="w-full h-96 bg-white rounded-lg shadow-sm border border-slate-200">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
