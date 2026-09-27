"""Build a grounded prompt from retrieved chunks and ask Claude for an answer with citations."""

from pydantic import BaseModel

from docs_chatbot.index import Hit

SYSTEM_PROMPT = (
    "You answer questions using only the numbered sources provided. "
    "Cite sources after each claim like [1] or [1][2]. "
    "If the sources do not contain the answer, reply exactly: "
    "\"I could not find that in the documentation.\" Do not use outside knowledge."
)
NOT_FOUND = "I could not find that in the documentation."


class Source(BaseModel):
    """A citation shown to the user."""

    id: int
    source: str
    title: str
    score: float


class Answer(BaseModel):
    """The chatbot's reply and the sources it was given."""

    answer: str
    sources: list[Source]


def build_prompt(question: str, hits: list[Hit]) -> str:
    """Numbered, tagged sources first and the question last (see 27_prompt-engineering.md section 9)."""
    sources = "\n".join(
        f'<source id="{i}" file="{h.chunk.source}">\n{h.chunk.text}\n</source>'
        for i, h in enumerate(hits, start=1)
    )
    return f"<sources>\n{sources}\n</sources>\n\nQuestion: {question}"


def to_sources(hits: list[Hit]) -> list[Source]:
    """Turn retrieval hits into numbered citations matching the prompt's source ids."""
    return [Source(id=i, source=h.chunk.source, title=h.chunk.title, score=round(h.score, 3))
            for i, h in enumerate(hits, start=1)]


def generate_answer(client, model: str, max_tokens: int, question: str, hits: list[Hit]) -> Answer:
    """Answer from the retrieved chunks; skip the LLM call entirely when nothing relevant was found."""
    if not hits:
        return Answer(answer=NOT_FOUND, sources=[])
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(question, hits)}],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    return Answer(answer=text or NOT_FOUND, sources=to_sources(hits))
