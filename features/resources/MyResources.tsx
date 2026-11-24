"use client";

import { useQuery } from "@apollo/client/react";
import { Plus } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { QueryState } from "@/components/ui/query-state";
import { MyResourcesDocument } from "@/graphql/generated/graphql";

const TONE = {
  PENDING: "bg-surface-2 text-muted",
  APPROVED:
    "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300",
  REJECTED: "bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-300",
} as const;

/** The resources a person sent (lvn-backend ADR-0074), newest first, each with its state and, if rejected, why. */
export function MyResources() {
  const t = useTranslations("resources");
  const { data, loading, error, refetch } = useQuery(MyResourcesDocument, {
    fetchPolicy: "cache-and-network",
  });
  const list = data?.myResources ?? [];
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            {t("title")}
          </h1>
          <p className="text-sm text-muted">{t("lead")}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="secondary">
            <Link href="/resources">{t("browse")}</Link>
          </Button>
          <Button asChild className="gap-1.5">
            <Link href="/resources/new">
              <Plus className="size-4" aria-hidden />
              {t("add")}
            </Link>
          </Button>
        </div>
      </header>
      {!data ? (
        <QueryState loading={loading} error={error} onRetry={refetch} />
      ) : null}
      {data && !list.length ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-sm text-muted">
          {t("none")}
        </p>
      ) : null}
      <ul className="flex flex-col gap-3">
        {list.map((r) => (
          <li key={r.id}>
            <Link
              href={`/resources/${r.id}`}
              className="flex flex-col gap-1 rounded-2xl border border-border bg-surface p-4 hover:border-accent"
            >
              <span className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-semibold text-accent">
                  {t(`type.${r.type}`)}
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${TONE[r.status]}`}
                >
                  {t(`status.${r.status}`)}
                </span>
              </span>
              <span className="font-semibold">{r.title}</span>
              <span className="text-xs text-muted">{r.host}</span>
              {r.status === "REJECTED" && r.reason ? (
                <span className="text-sm text-red-700 dark:text-red-300">
                  {r.reason}
                </span>
              ) : null}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
