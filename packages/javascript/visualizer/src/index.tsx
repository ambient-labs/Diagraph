import React from 'react';
import ReactDOM from 'react-dom/client';
import { LayoutFlow } from './Visualizer/Visualizer.js';
import { ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import './index.css';
import { Props } from './types.js';

const style = (version: string) => `
.react-flow__attribution:before {
  content: 'Diagraph ${version} | Viz by ';
}
`;

function DiagraphViz(props: Props) {
  return (
    <React.StrictMode>
      <ReactFlowProvider>
        <style>{style(props.version)}</style>
        <LayoutFlow {...props} />
      </ReactFlowProvider>
    </React.StrictMode>
  )
}

// export type { Props, NodeDefinition } from './types.js';

export default function renderDiagraphVisualization(target: HTMLElement, props: Props) {
  const root = ReactDOM.createRoot(target)
  root.render(React.createElement(DiagraphViz, props, null));
};
