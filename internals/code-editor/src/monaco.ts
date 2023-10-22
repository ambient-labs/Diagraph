import * as monaco from 'monaco-editor';

// @ts-ignore
self.MonacoEnvironment = {
  getWorker(_workerId: string, label: string): Worker {
            return new Worker(
          new URL('monaco-editor/esm/vs/editor/editor.worker.js', import.meta.url),
          { type: 'module' },
        );

    // switch (label) {
    //   case 'json': {
    //     return new Worker(
    //       new URL(
    //         '../node_modules/monaco-editor/esm/vs/language/json/json.worker.js',
    //         import.meta.url,
    //       ),
    //       { type: 'module' },
    //     );
    //   }

    //   default: {
    //     return new Worker(
    //       new URL('../node_modules/monaco-editor/esm/vs/editor/editor.worker.js', import.meta.url),
    //       { type: 'module' },
    //     );
    //   }
    // }
  },
};
export default monaco;
