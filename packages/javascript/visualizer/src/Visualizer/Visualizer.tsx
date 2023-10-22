import ReactFlow, {
  Background,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import styles from './Visualizer.module.css';

// import { initialNodes, initialEdges } from '../node-edges.js';
import DiagraphNode from '../Node/Node.js';
import { useFlow as useFlow } from './use-flow.js';
import { Props } from '../types.js';
import { BiFullscreen, BiExitFullscreen } from 'react-icons/bi';
import React, { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { FaGripHorizontal, FaGripLinesVertical } from 'react-icons/fa';

const nodeTypes = { node: DiagraphNode };

const useFullScreen = () => {
  const ref = useRef<HTMLDivElement>(null);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const listenFullScreen = useCallback(() => {
    setIsFullScreen(!!document.fullscreenElement);
  }, [setIsFullScreen]);

  const goFullScreen = useCallback(() => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      if (!ref.current) {
        throw new Error('No ref found');
      }
      ref.current.requestFullscreen();
    }
  }, [ref]);

  useEffect(() => {
    document.documentElement.addEventListener('fullscreenchange', listenFullScreen);
    return () => {
      document.documentElement.removeEventListener('fullscreenchange', listenFullScreen);
    }
  }, []);

  console.log(isFullScreen)

  return {
    containerRef: ref,
    goFullScreen,
    isFullScreen,
  }
};

export const LayoutContext = React.createContext<'LR' | 'TB'>('TB');
export const LayoutFlow = (props: Props) => {
  const { nodes, edges, onNodesChange, onEdgesChange, switchLayout, layout } = useFlow(props);

  const { isFullScreen, containerRef, goFullScreen } = useFullScreen();
  console.log('up')

  return (
    <div className={styles.container} ref={containerRef}>
      <LayoutContext.Provider value={layout}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          zoomOnScroll={false}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background color="#ccc" variant={BackgroundVariant.Dots} />
          <Panel position="top-right">
            <div className={styles.buttonGroup}>
              <button title={`${isFullScreen ? 'Exit' : "Go"} Full Screen`} onClick={goFullScreen}>{isFullScreen ? <BiExitFullscreen /> : <BiFullscreen />}</button>
              <button onClick={switchLayout}>{layout === 'LR' ? <FaGripLinesVertical /> : <FaGripHorizontal />}</button>
            </div>
          </Panel>
        </ReactFlow>
      </LayoutContext.Provider>
    </div>
  );
};
