import { useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Layers, Server, Shield } from "lucide-react";
import Button from "../components/Button.jsx";
import MermaidDiagram from "../components/MermaidDiagram.jsx";
import {
  DEMO_STEPS,
  ELEVATOR_PITCH,
  PRODUCT_NAME,
  TAGLINE,
  TECH_STACK,
} from "../config/branding.js";
import {
  DIAGRAMS,
  FLOW_SECTIONS,
  HLD_SUMMARY,
  LLD_BACKEND,
  LLD_FRONTEND,
  TENANCY_BULLETS,
} from "../content/architectureContent.js";
import { useAuth } from "../../modules/authentication/context/AuthContext.jsx";

const githubUrl = import.meta.env.VITE_GITHUB_REPO_URL?.trim();
const apiBase = import.meta.env.VITE_API_URL?.trim();
const apiDocsUrl = apiBase ? `${apiBase.replace(/\/$/, "")}/docs` : null;

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const goToApp = useCallback(() => {
    navigate(isAuthenticated ? "/dashboard" : "/login");
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen text-slate-900">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5 sm:px-6">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold tracking-tight text-brand-700">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white shadow-sm">
              S
            </span>
            {PRODUCT_NAME}
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            {githubUrl ? (
              <a
                href={githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 rounded-xl px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
              >
                <span>GitHub</span>
              </a>
            ) : null}
            <Button type="button" size="sm" onClick={goToApp}>
              Try {PRODUCT_NAME}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden">
          <div
            className="pointer-events-none absolute -left-24 -top-24 h-72 w-72 rounded-full bg-brand-200/50 blur-3xl"
            aria-hidden="true"
          />
          <div
            className="pointer-events-none absolute -right-16 top-10 h-64 w-64 rounded-full bg-brand-400/20 blur-3xl"
            aria-hidden="true"
          />
          <div className="relative mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
            <p className="inline-flex rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-700">
              {TAGLINE}
            </p>
            <h1 className="mt-5 max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Build AI assistants with knowledge, memory, and voice
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-relaxed text-slate-600">{ELEVATOR_PITCH}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button type="button" size="lg" onClick={goToApp}>
                Try {PRODUCT_NAME}
              </Button>
              {apiDocsUrl ? (
                <a href={apiDocsUrl} target="_blank" rel="noopener noreferrer">
                  <Button type="button" variant="secondary" size="lg">
                    API docs
                  </Button>
                </a>
              ) : null}
            </div>
            <div className="mt-10 flex flex-wrap gap-2">
              {TECH_STACK.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-slate-200/80 bg-white/80 px-3 py-1 text-xs font-medium text-slate-700 shadow-sm"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200/80 bg-white/70 py-14">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <h2 className="flex items-center gap-2 text-2xl font-bold text-slate-900">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                <Layers className="h-5 w-5" />
              </span>
              High-level design
            </h2>
            <ul className="mt-4 list-disc space-y-2 pl-5 text-slate-600">
              {HLD_SUMMARY.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div className="mt-8 grid gap-6 lg:grid-cols-2">
              <MermaidDiagram title={DIAGRAMS.productJourney.title} chart={DIAGRAMS.productJourney.mermaid} />
              <MermaidDiagram title={DIAGRAMS.hld.title} chart={DIAGRAMS.hld.mermaid} />
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200/80 py-14">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <h2 className="flex items-center gap-2 text-2xl font-bold text-slate-900">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                <Server className="h-5 w-5" />
              </span>
              Low-level design
            </h2>
            <div className="mt-8 grid gap-8 lg:grid-cols-2">
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  Frontend modules
                </h3>
                <ul className="mt-3 space-y-2">
                  {LLD_FRONTEND.map((row) => (
                    <li key={row.module} className="card-surface p-3">
                      <span className="font-medium text-brand-700">{row.module}</span>
                      <span className="text-slate-600"> — {row.role}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  Backend modules
                </h3>
                <ul className="mt-3 space-y-2">
                  {LLD_BACKEND.map((row) => (
                    <li key={row.module} className="card-surface p-3">
                      <span className="font-medium text-brand-700">{row.module}</span>
                      <span className="text-slate-600"> — {row.role}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-8">
              <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                <Shield className="h-4 w-4" />
                Multi-tenancy
              </h3>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-slate-600">
                {TENANCY_BULLETS.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </div>
            <div className="mt-8">
              <MermaidDiagram title={DIAGRAMS.backendLayers.title} chart={DIAGRAMS.backendLayers.mermaid} />
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200/80 bg-white/70 py-14">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <h2 className="text-2xl font-bold text-slate-900">Feature flows</h2>
            <p className="mt-2 max-w-3xl text-slate-600">
              End-to-end sequences for authentication, chat with RAG, description rewrite, and voice.
            </p>
            <div className="mt-8 space-y-8">
              {FLOW_SECTIONS.map((section) => (
                <MermaidDiagram key={section.title} title={section.title} chart={section.mermaid} />
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200/80 py-14">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <h2 className="text-2xl font-bold text-slate-900">Live demo walkthrough</h2>
            <ol className="mt-8 grid gap-4 sm:grid-cols-2">
              {DEMO_STEPS.map((step, index) => (
                <li key={step.title} className="card-surface p-5">
                  <span className="text-xs font-bold text-brand-600">Step {index + 1}</span>
                  <h3 className="mt-1 font-semibold text-slate-900">{step.title}</h3>
                  <p className="mt-2 text-sm text-slate-600">{step.detail}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 bg-slate-900 py-10 text-slate-300">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-4 sm:flex-row sm:items-center sm:px-6">
          <div>
            <p className="text-lg font-semibold text-white">{PRODUCT_NAME}</p>
            <p className="mt-1 text-sm text-slate-400">{TAGLINE}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button type="button" variant="primary" size="md" onClick={goToApp}>
              Try {PRODUCT_NAME}
            </Button>
            {githubUrl ? (
              <a href={githubUrl} target="_blank" rel="noopener noreferrer">
                <Button type="button" variant="secondary" size="md">GitHub</Button>
              </a>
            ) : null}
          </div>
        </div>
      </footer>
    </div>
  );
}
