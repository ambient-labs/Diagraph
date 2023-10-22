import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { DEFAULT_EDITOR_OPTIONS } from './config.js';
import monaco from './monaco.js';
import { LitElement, PropertyValueMap, css, html, unsafeCSS } from 'lit';
import styles from './code-editor.css?inline';
import { parseStyles } from '@internals/shared/parse-styles';
import { emit } from '@internals/shared/emit';
import { property, query, state } from 'lit/decorators.js';

export class CodeEditor extends LitElement {
  static styles = [
    parseStyles(styles),
  ];

  @query('slot')
  slotContainer: HTMLSlotElement;

  @property({ type: Object })
  options: Partial<monaco.editor.IEditorConstructionOptions> = {};

  @property()
  theme: string = 'vs-light';

  containerRef: Ref<HTMLDivElement> = createRef();

  // private get theme(dark = false) {
  //   return dark ? "vs-dark" : "vs-light";
  // }

  // constructor() {
  //   super();
  //   window
  //     .matchMedia("(prefers-color-scheme: dark)")
  //     .addEventListener("change", () => {
  //       monaco.editor.setTheme('vs-dark');
  //     });
  // }

  editor?: ReturnType<typeof monaco.editor.create>;

  public reset = () => {
    // https://github.com/Microsoft/monaco-editor/issues/1397
    // for cursor position
    const childNodes = this.slotContainer.assignedNodes({ flatten: true });
    this.value = childNodes.map((node) => node.textContent ? node.textContent : '').join('');
  }

  firstUpdated() {
    this.editor = monaco.editor.create(
      this.containerRef.value!,
      {
        ...DEFAULT_EDITOR_OPTIONS,
        ...this.options,
        // // value: this.value,
        // language: 'python',
        // theme: this.theme,
      },
    );

    this.editor.onDidBlurEditorWidget(() => {
      emit(this, 'blur');
    });

    this.editor.onDidFocusEditorWidget(() => {
      emit(this, 'focus');
    });
  }

  get value() {
    return this.editor!.getValue();
  }

  set value(value: string) {
    // https://github.com/Microsoft/monaco-editor/issues/1397
    // for cursor position
    this.editor!.getModel().setValue(value);
  }

  protected updated(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): void {
    if (_changedProperties.has('theme')) {
      this.editor!.updateOptions({
        theme: this.theme,
      });
    }
  }

  handleSlotchange(e) {
    this.reset();
  }

  render() {
    return html`
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/editor/editor.main.min.css">
      <main ${ref(this.containerRef)} />
      <slot @slotchange=${this.handleSlotchange}></slot>
    `;
  }
}
