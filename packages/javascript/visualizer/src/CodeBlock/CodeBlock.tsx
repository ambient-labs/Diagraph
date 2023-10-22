import clsx from 'clsx';
import styles from './CodeBlock.module.css';
import { Prism, Highlight, themes } from "prism-react-renderer";
import { useCallback, useEffect } from 'react';

export function CodeBlock({ code = '', language = 'text', }: { code?: string, language?: string }) {
  const loadTheLanguages = useCallback(async () => {
    (typeof global !== "undefined" ? global : window).Prism = Prism
    const loadLanguages = await import('https://esm.sh/prismjs/components/index.js');
    console.log(loadLanguages)
    loadLanguages.default(['python']);
  }, []);
  useEffect(() => {
    loadTheLanguages();
  }, [loadTheLanguages]);
  return (
    <Highlight
      theme={themes.github}
      code={code}
      language={language}
    >
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
        <pre style={style} className={clsx(styles.codeBlock, "nodrag")} >
          {tokens.map((line, i) => (
            <div key={i} {...getLineProps({ line })}>
              <span className={styles.lineNumber}>{i + 1}</span>
              {line.map((token, key) => (
                <span key={key} {...getTokenProps({ token })} />
              ))}
            </div>
          ))}
        </pre>
      )}

    </Highlight>
  );
};

