import dagre from '@dagrejs/dagre';
import { Props } from '../types';
import { Edge, useEdgesState, useNodesState, useReactFlow } from 'reactflow';
import { useCallback, useEffect, useState } from 'react';


export const useFlow = (props: Props) => {
  const { fitView } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [layout, setLayout] = useState<'TB' | 'LR'>('LR');

  const switchLayout = useCallback(
    () => {
      const rankdir = layout === 'TB' ? 'LR' : 'TB';
      const layouted = getLayoutedElements(props, rankdir);

      setNodes([...layouted.nodes]);
      setEdges([...layouted.edges]);
      setLayout(rankdir);

      window.requestAnimationFrame(() => {
        fitView();
      });
    },
    [nodes, edges]
  );

  useEffect(() => {
    switchLayout();
  }, []);
  return { nodes, edges, onNodesChange, onEdgesChange, switchLayout, layout };
}



const getLayoutedElements = ({ nodes: nodes, graph }: Props, rankdir: 'TB' | 'LR') => {
  const g = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir });

  nodes.forEach((node) => {
    g.setNode(node.id, { label: node.label, width: 150, height: 150 })
  });

  const inEdges: Record<string, Set<string>> = {};
  const outEdges: Record<string, Set<string>> = {};
  Object.entries(graph).forEach(([source, targets]) => {
    targets.forEach(target => {
      g.setEdge(source, target)
      if (!inEdges[target]) {
        inEdges[target] = new Set();
      }
      if (!outEdges[source]) {
        outEdges[source] = new Set();
      }
      inEdges[target].add(source);
      outEdges[source].add(target);
    });
  });

  dagre.layout(g);

  const edges: Edge[] = g.edges().map(({ v, w }) => ({
    id: `e${v}${w}`,
    source: v,
    sourceHandle: w,
    target: w,
    type: 'smoothstep',
    // animated: true,
  }));

  return {
    nodes: nodes.map((node) => {
      const { x, y } = g.node(node.id);

      return {
        id: node.id,
        type: 'node',
        data: {
          node,
          inEdges: [...(inEdges[node.id] || [])],
          outEdges: [...(outEdges[node.id] || [])],
        },
        position: { x, y },
      };
    }),
    edges,
  };
};
