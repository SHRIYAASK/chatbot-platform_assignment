import { useEffect, useId, useRef, useState } from "react";

let mermaidModulePromise;

function loadMermaid() {
  if (!mermaidModulePromise) {
    mermaidModulePromise = import("mermaid").then((mod) => {
      const mermaid = mod.default;
      mermaid.initialize({
        startOnLoad: false,
        theme: "neutral",
        securityLevel: "strict",
        fontFamily: "inherit",
      });
      return mermaid;
    });
  }
  return mermaidModulePromise;
}

export default function MermaidDiagram({ chart, title }) {
  const containerRef = useRef(null);
  const reactId = useId();
  const diagramId = `mermaid-${reactId.replace(/:/g, "")}`;
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      if (!chart?.trim() || !containerRef.current) {
        return;
      }

      try {
        const mermaid = await loadMermaid();
        if (cancelled) {
          return;
        }
        const { svg } = await mermaid.render(diagramId, chart.trim());
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
        setError(null);
      } catch (renderError) {
        if (!cancelled) {
          setError(renderError?.message || "Could not render diagram.");
        }
      }
    }

    render();

    return () => {
      cancelled = true;
    };
  }, [chart, diagramId]);

  return (
    <figure className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {title ? (
        <figcaption className="mb-3 text-sm font-semibold text-slate-800">{title}</figcaption>
      ) : null}
      {error ? (
        <pre className="overflow-x-auto text-xs text-red-600">{error}</pre>
      ) : (
        <div
          ref={containerRef}
          className="mermaid-diagram overflow-x-auto text-center text-slate-800 [&_svg]:max-w-full"
          aria-label={title || "Architecture diagram"}
        />
      )}
    </figure>
  );
}
