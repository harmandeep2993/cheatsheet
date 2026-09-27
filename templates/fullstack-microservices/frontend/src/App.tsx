// Page layout: documents on one side, chat on the other.
import { ChatPanel } from "./components/ChatPanel";
import { DocumentList } from "./components/DocumentList";

export function App() {
  return (
    <main className="layout">
      <header className="layout__header">
        <h1>Docs Chat</h1>
        <p className="muted">Add documents, then ask questions about them.</p>
      </header>
      <DocumentList />
      <ChatPanel />
    </main>
  );
}
