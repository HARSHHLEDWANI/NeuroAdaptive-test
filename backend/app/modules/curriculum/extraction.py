"""
Concept extraction: per-section LLM proposal of candidate concepts.

Run per document section (this phase groups by a document's heading_path,
already computed by Phase 1's chunker) with bounded context, never as one
whole-document prompt -- the mandate's specific instruction, and the reason
being the same one that motivates 500-800 token chunks in the first place:
a model asked to summarize an entire 90-page document in one call produces
fluent structure with weak grounding to any specific part of it.

Source-chunk granularity for this phase is section-level, not per-sentence:
a concept extracted from a section is linked to every chunk in that section
group. Precise which-exact-chunk-supports-which-exact-concept is a nice-to-
have this phase does not attempt; ConceptSource still resolves to real, owned
chunks either way, which is what validation.py actually checks.
"""
import json
import re
from typing import Dict, List

from app.core.prompt_safety import UNTRUSTED_CONTENT_WARNING, wrap_untrusted
from app.core.config import settings
from app.modules.curriculum.normalization import CandidateConcept
from app.modules.documents.chunk_models import Chunk
from app.services.embedding.gateway import EmbeddingGateway
from app.services.generation.gateway import GenerationError, GenerationGateway

MAX_SECTION_CHARS = 6000  # bounded-context ceiling for one extraction call
# Keep concept normalization embeddings within the live Gemini gateway's
# documented request ceiling.  Sending one request for every concept can
# exhaust the provider immediately after a large document's chunk-indexing
# stage has finished.
MAX_CONCEPT_EMBEDDING_BATCH_SIZE = 10


class ExtractionParseError(Exception):
    """The model's response could not be parsed as the expected shape."""


def group_chunks_into_sections(chunks: List[Chunk]) -> List[List[Chunk]]:
    """
    Groups chunks by heading_path, preserving document order. A chunk with no
    heading_path (a document with no detected structure) becomes its own
    single-chunk group rather than being silently dropped.
    """
    groups: Dict[str, List[Chunk]] = {}
    order: List[str] = []
    for chunk in sorted(chunks, key=lambda c: (str(c.document_id), c.position)):
        key = chunk.heading_path or f"__no_heading__:{chunk.id}"
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(chunk)
    return [groups[key] for key in order]


def batch_sections_for_generation(section_groups: List[List[Chunk]]) -> List[List[Chunk]]:
    """Pack adjacent small sections into bounded generation requests.

    PDF heading detection can yield a heading for nearly every short paragraph.
    Sending one request per such heading makes a normal document need hundreds
    of provider calls.  Packing preserves document order and exact source
    provenance while enforcing the same ``MAX_SECTION_CHARS`` context bound
    used by a single large section.
    """
    batches: List[List[Chunk]] = []
    current: List[Chunk] = []
    current_chars = 0

    for group in section_groups:
        group_chars = sum(len(chunk.text) for chunk in group)
        if current and current_chars + group_chars > MAX_SECTION_CHARS:
            batches.append(current)
            current = []
            current_chars = 0
        current.extend(group)
        current_chars += group_chars

    if current:
        batches.append(current)
    return batches


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z]*\n?", "", stripped)
        stripped = re.sub(r"\n?```$", "", stripped)
    return stripped.strip()


def propose_concepts_for_section(
    section_chunks: List[Chunk],
    generation: GenerationGateway,
    embeddings: EmbeddingGateway,
) -> List[CandidateConcept]:
    """One bounded-context LLM call, then one embedding call per proposed
    concept (needed for normalization's similarity comparison)."""
    if not section_chunks:
        return []

    text = "\n\n".join(c.text for c in section_chunks)[:MAX_SECTION_CHARS]
    heading = section_chunks[0].heading_path or "(untitled section)"

    prompt = (
        f"Section: {heading}\n\n{wrap_untrusted(text)}\n\n"
        "Identify the distinct, independently teachable concepts in this "
        "section. For each, give a name, a self-contained one-to-two "
        "sentence definition grounded ONLY in this text, an importance score "
        "in [0,1], and a Bloom's taxonomy level "
        "(remember|understand|apply|analyze|evaluate|create).\n\n"
        "Respond with ONLY this JSON shape:\n"
        '{"concepts": [{"name": "...", "definition": "...", '
        '"importance": 0.0, "bloom_level": "..."}]}\n'
        "If the section contains no distinct teachable concept, return "
        '{"concepts": []}.'
    )

    payload = None
    last_error = None
    for attempt in range(settings.CONCEPT_EXTRACTION_MAX_GENERATION_ATTEMPTS_V1):
        attempt_prompt = prompt
        if attempt:
            attempt_prompt += "\nYour preceding response was not valid JSON. Return the requested JSON object only."
        try:
            raw = generation.generate(
                attempt_prompt,
                system_instruction=UNTRUSTED_CONTENT_WARNING,
                temperature=0.2,
                max_output_tokens=2000,
                json_mode=True,
            )
            payload = json.loads(_strip_code_fence(raw))
            break
        except (GenerationError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc

    if payload is None:
        raise ExtractionParseError(str(last_error)) from last_error

    concepts = payload.get("concepts")
    if not isinstance(concepts, list):
        raise ExtractionParseError("Response missing a 'concepts' list.")

    chunk_ids = [c.id for c in section_chunks]
    candidates = []
    for item in concepts:
        name = item.get("name")
        definition = item.get("definition")
        if not isinstance(name, str) or not isinstance(definition, str) or not name.strip():
            continue  # skip a malformed entry rather than fail the whole section

        importance = item.get("importance", 0.5)
        importance = importance if isinstance(importance, (int, float)) else 0.5
        importance = max(0.0, min(1.0, float(importance)))

        candidates.append(
            CandidateConcept(
                name=name.strip(),
                definition=definition.strip(),
                source_chunk_ids=list(chunk_ids),
                embedding=[],
                importance=importance,
                bloom_level=item.get("bloom_level") if isinstance(item.get("bloom_level"), str) else None,
            )
        )
    # The gateway guarantees one embedding per input in the same order. Batch
    # here rather than making a provider request for every candidate; this is
    # both materially gentler on quota and preserves the candidate-to-vector
    # mapping exactly.
    for start in range(0, len(candidates), MAX_CONCEPT_EMBEDDING_BATCH_SIZE):
        batch = candidates[start : start + MAX_CONCEPT_EMBEDDING_BATCH_SIZE]
        vectors = embeddings.embed_texts([candidate.definition for candidate in batch])
        for candidate, vector in zip(batch, vectors):
            candidate.embedding = vector

    return candidates
