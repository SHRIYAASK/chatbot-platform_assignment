import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import "./MarkdownRenderer.css";

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <button type="button" className="md-copy-btn" onClick={handleCopy} aria-label="Copy code">
      {copied ? "Copied" : "Copy code"}
    </button>
  );
}

function CodeBlock({ className, children }) {
  const languageMatch = /language-([\w-]+)/.exec(className || "");
  const language = languageMatch?.[1];
  const code = String(children).replace(/\n$/, "");

  return (
    <div className="md-code-block group">
      <div className="md-code-header">
        {language ? <span className="md-code-lang">{language}</span> : <span />}
        <CopyButton text={code} />
      </div>
      <pre>
        <code className={className}>{children}</code>
      </pre>
    </div>
  );
}

export default function MarkdownRenderer({ content }) {
  const components = useMemo(
    () => ({
      pre({ children }) {
        return <>{children}</>;
      },
      code({ className, children, ...props }) {
        if (className && /language-/.test(className)) {
          return <CodeBlock className={className}>{children}</CodeBlock>;
        }

        return (
          <code className="md-inline-code" {...props}>
            {children}
          </code>
        );
      },
      table({ children }) {
        return (
          <div className="md-table-wrapper">
            <table>{children}</table>
          </div>
        );
      },
      a({ href, children, ...props }) {
        const isExternal = href?.startsWith("http");

        return (
          <a
            href={href}
            {...props}
            target={isExternal ? "_blank" : undefined}
            rel={isExternal ? "noopener noreferrer" : undefined}
          >
            {children}
          </a>
        );
      },
    }),
    [],
  );

  if (!content?.trim()) {
    return null;
  }

  return (
    <div className="markdown-renderer">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
