import { defineConfig } from 'vite';
import path from 'path';
import react from '@vitejs/plugin-react';
import { copy } from 'fs-extra';
import * as url from 'url';
const __dirname = url.fileURLToPath(new URL('.', import.meta.url));

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'process.env': {}
  },
  plugins: [react(),
  {
    name: 'postbuild-copy', // the name of your custom plugin. Could be anything.
    closeBundle: async () => {
      const src = path.resolve(__dirname, './dist');
      const target = path.resolve(__dirname, '../../python/diagraph/assets/dist');
      await copy(src, target);
    }
  },
  ],
  build: {
    target: 'esnext',
    minify: false,
    lib: {
      entry: './src/index.tsx',
      name: 'renderDiagraphVisualization',
      fileName: 'diagraph-visualizer',
      // format: 'umd',
    },
    rollupOptions: {
      // external: ['react', 'react-dom'],

      // input: './src/index.tsx',
      output: {
        // dir: 'dist',
        format: 'umd',
        // globals: {
        //   'react': 'React',
        //   'react-dom': 'ReactDOM',
        // },
        // entryFileNames: 'diagraph-visualizer.js',
      },
    },
  }
})
