import { useCallback, useContext, useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import { Handle, NodeResizer, Position } from 'reactflow';
import { PiCaretRightBold } from 'react-icons/pi';
import { NodeDefinition } from '../types.js';
import styles from './Node.module.css';
// import { Highlight, themes } from "prism-react-renderer";
import { CodeBlock } from '../CodeBlock/CodeBlock.js';
import { LayoutContext } from '../Visualizer/Visualizer.js';

// const useLoadPrismLanguage = () => {
//   const loadLanguage = useCallback(async (language: string) => {
//     (typeof global !== "undefined" ? global : window).Prism = Prism
//     await import(`prismjs/components/prism-${language}`);
//   }, []);

//   useEffect(() => {
//     loadLanguage('python')
//   }, [loadLanguage]);
// }

function DiagraphNode({ data: {
  node,
  inEdges,
  outEdges,
} }: {
  data: {
    node: NodeDefinition;
    inEdges: string[];
    outEdges: string[];
  }
}) {

  const layout = useContext(LayoutContext);
  // useLoadPrismLanguage();
  const [expanded, setExpanded] = useState(false);

  const handleClick = useCallback(() => {
    setExpanded(e => !e);
  }, []);

  const sections = useMemo<{ label: string; value?: string; language?: string; }[]>(() => (
    [
      { label: 'Function', value: node.fn, language: 'python' },
      { label: 'Prompt', value: node.prompt },
      { label: 'Result', value: node.result },
    ]
  ), [node.fn, node.prompt, node.result]);

  const getStyle = useCallback((i: number, total: number) => {
    const key = layout === 'LR' ? 'top' : 'left';
    return { [key]: `${getPosition(i, total) * 100}%` };
  }, [layout]);

  return (
    <div className={clsx(styles.node, { [styles.expanded]: expanded })}>
      <NodeResizer isVisible={expanded} minWidth={150} minHeight={50} />

      <header>
        <button onClick={handleClick}>
          <PiCaretRightBold className="nodrag" />
        </button>
        <label>{node.label}</label>
      </header>
      <main>
        {sections.map(({ label, value, language }) => (
          <section key={label}>
            <label>{label}</label>
            {value ? <CodeBlock code={value} language={language} /> : <div className={styles.empty}>--</div>}
          </section>
        ))}
      </main>
      {inEdges.map((edge, i) => (
        <Handle
          key={edge}
          type="target"
          position={layout === 'LR' ? Position.Left : Position.Top}
          id={edge}
          style={getStyle(i, inEdges.length)}
        // isConnectable={isConnectable}
        />

      ))}
      {outEdges.map((edge, i) => (
        <Handle
          key={edge}
          type="source"
          position={layout === 'LR' ? Position.Right : Position.Bottom}
          id={edge}
          style={getStyle(i, outEdges.length)}
        />
      ))}
    </div>
  );
}

export default DiagraphNode;

const getPosition = (i: number, total: number) => {
  if (total === 1) {
    return 0.5; // Special case to avoid division by zero
  }
  const blockSize = 1 / (total);
  return i * (blockSize) + blockSize / 2;
};
