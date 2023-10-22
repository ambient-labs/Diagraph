import { CodeEditor } from './code-editor.js';

customElements.get('code-editor') || customElements.define('code-editor', CodeEditor);

declare global {
  interface HTMLElementTagNameMap {
    "code-editor": CodeEditor;
  }
}

