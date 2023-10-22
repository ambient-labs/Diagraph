import monaco from "./monaco.js";

export const DEFAULT_EDITOR_OPTIONS: monaco.editor.IEditorConstructionOptions = {
  // autoIndent: "full",
  // automaticLayout: true,
  // contextmenu: true,
  // fontFamily: "monospace",
  // fontSize: 13,
  // lineHeight: 24,
  // hideCursorInOverviewRuler: true,
  // matchBrackets: "always",
  minimap: {
    enabled: false,
  },
  // readOnly: false,
  // scrollbar: {
  //   horizontalSliderSize: 4,
  //   verticalSliderSize: 18,
  // },

  lineNumbers: "on",
  roundedSelection: false,
  scrollBeyondLastLine: false,
  ariaLabel: "code editor",
  readOnly: false,
  // theme: "hc-black",
  // language: "javascript",
  //Resizes Based on Screen & Container Size.
  automaticLayout: false,
  padding: {
    top: 8
  }
};


