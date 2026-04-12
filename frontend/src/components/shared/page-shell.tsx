import * as React from "react";

type PageShellProps = {
  title: string;
  children: React.ReactNode;
};

export function PageShell({ title, children }: PageShellProps) {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-4 p-3 sm:gap-6 sm:p-6">
      <header>
        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl">{title}</h1>
      </header>
      <section className="rounded-lg border border-slate-200 bg-white p-3 sm:p-4">{children}</section>
    </main>
  );
}
