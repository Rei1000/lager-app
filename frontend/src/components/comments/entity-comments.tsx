"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { createComment, listCommentsForEntity } from "@/lib/api-client";
import type { CommentDto } from "@/lib/types";

type EntityCommentsProps = {
  entityType: string;
  entityId: string;
  title?: string;
};

export function EntityComments({ entityType, entityId, title = "Kommentare" }: EntityCommentsProps) {
  const [comments, setComments] = useState<CommentDto[]>([]);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    setError(null);
    setLoading(true);
    void listCommentsForEntity({ entity_type: entityType, entity_id: entityId })
      .then((items) => {
        if (active) {
          setComments(items);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Kommentare konnten nicht geladen werden.");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [entityId, entityType]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = text.trim();
    if (!normalized) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const created = await createComment({
        entity_type: entityType,
        entity_id: entityId,
        text: normalized,
      });
      setComments((current) => [created, ...current]);
      setText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kommentar konnte nicht gespeichert werden.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="grid gap-2 rounded border border-slate-200 p-3 text-sm sm:p-4">
      <h3 className="font-medium">{title}</h3>
      <form className="grid gap-2" onSubmit={handleSubmit}>
        <textarea
          className="min-h-24 rounded border border-slate-200 px-3 py-2 text-base"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Kommentar eingeben"
        />
        <Button className="w-full sm:w-auto" type="submit" disabled={saving}>
          {saving ? "Speichert..." : "Kommentar speichern"}
        </Button>
      </form>
      {error ? <p className="text-red-600">{error}</p> : null}
      {loading ? <p>Lade Kommentare...</p> : null}
      {!loading && comments.length === 0 ? <p>Keine Kommentare vorhanden.</p> : null}
      <ul className="grid gap-2">
        {comments.map((item) => (
          <li key={item.id} className="rounded border border-slate-200 p-3">
            <p className="leading-relaxed">{item.text}</p>
            <p className="text-xs text-slate-600">
              User {item.created_by_user_id} | {new Date(item.created_at).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
