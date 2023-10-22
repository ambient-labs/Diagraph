export interface NodeDefinition {
  id: string;
  label: string;
  prompt?: string;
  result?: string;
  fn?: string;
}

export interface Props {
  nodes: NodeDefinition[];
  graph: Record<string, string[]>;
  version: string;
}
