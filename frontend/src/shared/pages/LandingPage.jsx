import { useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/Button.jsx";
import { LANDING_FEATURES, PRODUCT_NAME, TAGLINE, GITHUB_REPO_URL } from "../config/branding.js";
import { useAuth } from "../../modules/authentication/context/AuthContext.jsx";

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const goToApp = useCallback(() => {
    navigate(isAuthenticated ? "/dashboard" : "/login");
  }, [isAuthenticated, navigate]);

  return (
    <div className="flex min-h-screen flex-col text-stone-900">
      <header className="px-4 py-8 sm:px-6">
        <Link
          to="/"
          className="mx-auto flex max-w-5xl items-center gap-2.5 text-[15px] font-medium tracking-[0.18em] text-stone-700"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-700 text-xs font-semibold text-[#f7f5f2]">
            S
          </span>
          {PRODUCT_NAME.toUpperCase()}
        </Link>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-4 pb-16 sm:px-6">
        <section className="max-w-2xl pt-4">
          <p className="text-sm tracking-wide text-stone-500">{TAGLINE}</p>
          <h1 className="mt-4 text-4xl font-light tracking-tight text-stone-900 sm:text-5xl">
            Features
          </h1>
        </section>

        <section className="mt-12 grid gap-4 sm:grid-cols-2">
          {LANDING_FEATURES.map((feature) => (
            <article
              key={feature.title}
              className="rounded-2xl border border-stone-200/80 bg-[#fcfbf9]/90 p-6"
            >
              <h2 className="text-base font-medium text-stone-900">{feature.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-stone-600">{feature.detail}</p>
            </article>
          ))}
        </section>

        <div className="mt-14 flex flex-col items-center gap-4">
          <Button type="button" size="lg" className="min-w-[12rem] rounded-full px-8" onClick={goToApp}>
            Try {PRODUCT_NAME}
          </Button>
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-stone-500 underline decoration-stone-300 underline-offset-4 transition hover:text-stone-800"
          >
            Code references on GitHub
          </a>
        </div>
      </main>
    </div>
  );
}
