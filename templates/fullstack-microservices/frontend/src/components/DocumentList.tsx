// Lists documents from documents-service and adds new ones.
import { type FormEvent, useEffect, useState } from "react";

import { createDocument, type DocumentItem, listDocuments } from "../api/client";

export function DocumentList() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createDocument(title, content);
      setDocuments((current) => [created, ...current]);
      setTitle("");
      setContent("");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <section className="card">
      <h2>Documents</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea
          placeholder="Content"
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <button type="submit">Add document</button>
      </form>
      {error && <p className="status status--error">{error}</p>}
      <ul className="list">
        {documents.map((doc) => (
          <li key={doc.id}>
            <strong>{doc.title}</strong>
            <span className="muted"> #{doc.id}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
