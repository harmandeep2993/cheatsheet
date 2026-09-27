// Sends a question to chat-service and shows the answer with its sources.
import { type FormEvent, useState } from "react";

import { askQuestion, type ChatAnswer } from "../api/client";

export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<ChatAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setAnswer(await askQuestion(question));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Ask</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <input
          placeholder="How long do refunds take?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          minLength={3}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>
      {error && <p className="status status--error">{error}</p>}
      {answer && (
        <div className="answer">
          <p>{answer.answer}</p>
          {answer.sources.length > 0 && (
            <p className="muted">Sources: {answer.sources.map((s) => s.title).join(", ")}</p>
          )}
        </div>
      )}
    </section>
  );
}
