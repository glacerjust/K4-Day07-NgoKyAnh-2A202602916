"""
Benchmark script for evaluating retrieval strategies on University Corpus.
Supports multiple chunking strategies for team members:
- Member 1 (Đinh Tiến Cảnh): MarkdownHeadingChunker (Section/Heading-based with context injection)
- Member 2 (Ngô Kỳ Anh): RecursiveChunker (chunk_size=500)
- Member 3 (Nguyễn Quốc Cường): SentenceChunker (max_sentences_per_chunk=3)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    GeminiEmbedder,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.models import Document
from src.store import EmbeddingStore


class MarkdownHeadingChunker:
    """
    Chunk markdown documents based on headings (#, ##, ###, ####, Điều ...).
    If a section exceeds max_chunk_size, recursively split it while injecting
    the section title into each sub-chunk to preserve hierarchical context.
    """

    def __init__(self, max_chunk_size: int = 600, overlap: int = 50) -> None:
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.recursive_fallback = RecursiveChunker(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=max_chunk_size,
        )

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Split text by Markdown headings (# to ####) or 'Điều X.'
        lines = text.split("\n")
        sections: list[tuple[str, list[str]]] = []
        current_heading = "Mở đầu"
        current_lines: list[str] = []

        for line in lines:
            heading_match = re.match(r"^(#{1,4}\s+.*|\*{0,2}Điều\s+\d+.*)", line.strip())
            if heading_match:
                if current_lines:
                    sections.append((current_heading, current_lines))
                    current_lines = []
                current_heading = heading_match.group(0).strip("#* ")
                current_lines.append(line)
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_heading, current_lines))

        chunks: list[str] = []
        for heading, s_lines in sections:
            section_content = "\n".join(s_lines).strip()
            if not section_content:
                continue

            if len(section_content) <= self.max_chunk_size:
                chunks.append(section_content)
            else:
                # Sub-split long section and prepend heading context
                sub_chunks = self.recursive_fallback.chunk(section_content)
                for sc in sub_chunks:
                    sc_clean = sc.strip()
                    if not sc_clean:
                        continue
                    if not sc_clean.startswith(heading):
                        sc_with_header = f"[{heading}]\n{sc_clean}"
                    else:
                        sc_with_header = sc_clean
                    chunks.append(sc_with_header)

        return chunks


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter and markdown body."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            metadata = {}
            for line in fm_text.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    metadata[key] = val
            return metadata, body
    return {}, content


BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Sinh viên chương trình đại học không bị cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính?",
        "filter": None,
        "gold_answer": "Sinh viên không bị cảnh báo học tập được đăng ký tối đa 24 tín chỉ và tối thiểu 12 tín chỉ trong học kỳ chính. Không áp dụng ngưỡng đăng ký tối thiểu với sinh viên trình độ năm cuối (Điều 10 Quy chế đào tạo 2025).",
        "expected_doc": "hust-quy-che-dao-tao-2025",
        "must_contain": "đăng ký tối đa 24 tín chỉ",
    },
    {
        "id": 2,
        "query": "Khi nào sinh viên bị nâng một mức cảnh báo học tập và khi nào bị áp dụng cảnh báo học tập mức 3?",
        "filter": None,
        "gold_answer": "Nâng 1 mức cảnh báo khi số tín chỉ không đạt trong học kỳ > 8 TC. Áp dụng cảnh báo mức 3 khi số tín chỉ nợ đọng từ đầu khóa > 24 TC (Điều 19 Quy chế đào tạo 2025).",
        "expected_doc": "hust-quy-che-dao-tao-2025",
        "must_contain": "số tín chỉ nợ đọng từ đầu khóa",
    },
    {
        "id": 3,
        "query": "Mức học phí các học phần học trong học kỳ hè và mức học phí đối với sinh viên nước ngoài tự chi trả được tính bằng bao nhiêu lần mức học phí thông thường?",
        "filter": {"department": "finance"},
        "gold_answer": "Mức học phí học kỳ hè và mức học phí đối với sinh viên nước ngoài tự chi trả đều được tính bằng 1,5 lần mức học phí quy định thông thường (Phụ lục I Mục 5 Quyết định học phí 2025-2026).",
        "expected_doc": "hust-hoc-phi-2025-2026",
        "must_contain": "tính bằng 1,5 lần",
    },
    {
        "id": 4,
        "query": "Chứng chỉ tiếng Anh nộp để xét chuẩn ngoại ngữ đầu ra có bắt buộc phải đánh giá đủ 4 kỹ năng không?",
        "filter": {"category": "language-requirements"},
        "gold_answer": "Có, chứng chỉ tiếng Anh phải đánh giá đầy đủ 4 kỹ năng nghe, nói, đọc, viết; được cấp bởi các đơn vị hợp pháp và có hiệu lực 02 năm tính đến ngày nộp hồ sơ (Điều 5 Quy định ngoại ngữ K71).",
        "expected_doc": "hust-quy-dinh-ngoai-ngu-k71",
        "must_contain": "đánh giá đầy đủ 4 kỹ năng",
    },
    {
        "id": 5,
        "query": "Văn bản bản dịch tiếng Anh của Quy chế đào tạo năm 2025 được ban hành nhằm mục đích gì và có giá trị pháp lý thay thế văn bản gốc tiếng Việt không?",
        "filter": None,
        "gold_answer": "Bản dịch tiếng Anh phục vụ giảng dạy, học tập, trao đổi sinh viên quốc tế và kiểm định quốc tế; có tính chất tham khảo, nếu có khác biệt thì bản gốc tiếng Việt có giá trị pháp lý cao nhất (Thông báo số 2034/TB-ĐHBK năm 2025).",
        "expected_doc": "hust-ban-dich-tieng-anh-quy-che-dao-tao-2025",
        "must_contain": "tính chất tham khảo",
    },
]


def load_corpus_and_chunk(
    data_dir: str,
    strategy_name: str,
    chunk_size: int = 500,
) -> tuple[list[Document], int]:
    corpus_path = Path(data_dir)
    md_files = sorted(corpus_path.glob("*.md"))

    if strategy_name == "heading":
        chunker = MarkdownHeadingChunker(max_chunk_size=chunk_size)
    elif strategy_name == "recursive":
        chunker = RecursiveChunker(chunk_size=chunk_size)
    elif strategy_name == "sentence":
        chunker = SentenceChunker(max_sentences_per_chunk=3)
    elif strategy_name == "fixed":
        chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=50)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy_name}")

    documents: list[Document] = []
    total_files = 0

    for file_path in md_files:
        raw_text = file_path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(raw_text)
        doc_id = metadata.get("doc_id", file_path.stem)
        metadata["doc_id"] = doc_id
        metadata["source_file"] = file_path.name

        chunks = chunker.chunk(body)
        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{doc_id}#{i}",
                content=chunk_text,
                metadata={**metadata, "chunk_index": i},
            )
            documents.append(doc)
        total_files += 1

    return documents, total_files


def run_benchmark(
    strategy: str = "heading",
    data_dir: str = "data/university",
    top_k: int = 3,
    chunk_size: int = 500,
) -> None:
    print("=" * 80)
    print(f"BẮT ĐẦU CHẠY BENCHMARK RETRIEVAL — CHIẾN LƯỢC: [{strategy.upper()}]")
    print("=" * 80)

    docs, file_count = load_corpus_and_chunk(data_dir, strategy, chunk_size=chunk_size)
    print(f"Đã đọc {file_count} file từ '{data_dir}'. Tổng số chunks được tạo ra: {len(docs)}")

    from dotenv import load_dotenv
    load_dotenv()
    embedder = OpenAIEmbedder(model_name=OPENAI_EMBEDDING_MODEL)
    store = EmbeddingStore(collection_name=f"bench_{strategy}", embedding_fn=embedder)
    store.add_documents(docs)
    print(f"Đã nạp {store.get_collection_size()} chunks vào vector store.")
    print("-" * 80)

    total_score = 0

    for item in BENCHMARK_QUERIES:
        q_id = item["id"]
        query = item["query"]
        q_filter = item["filter"]
        gold = item["gold_answer"]
        expected_doc = item["expected_doc"]

        print(f"\n[CÂU HỎI #{q_id}] {query}")
        if q_filter:
            print(f"  -> Áp dụng metadata filter: {q_filter}")
            results = store.search_with_filter(query, top_k=top_k, metadata_filter=q_filter)
        else:
            results = store.search(query, top_k=top_k)

        found_relevant = False
        top1_correct = False

        print("  Top-3 Chunks truy xuất được:")
        for rank, res in enumerate(results, start=1):
            res_doc_id = res["metadata"].get("doc_id", "")
            contains_answer = item["must_contain"].lower() in res["content"].lower()
            is_match = (res_doc_id == expected_doc) and contains_answer
            marker = " [V]" if is_match else " [X]"
            if is_match:
                found_relevant = True
                if rank == 1:
                    top1_correct = True

            snippet = res["content"][:140].replace("\n", " ")
            print(f"    {rank}. score={res['score']:.4f} | doc={res_doc_id} | id={res['id']}{marker}")
            print(f"       Trích đoạn: {snippet}...")

        # Scoring
        if top1_correct:
            points = 2
        elif found_relevant:
            points = 1
        else:
            points = 0

        total_score += points
        print(f"  => Đánh giá: {points}/2 điểm (Tài liệu chuẩn: {expected_doc})")

    print("\n" + "=" * 80)
    print(f"TỔNG KẾT BENCHMARK CHIẾN LƯỢC [{strategy.upper()}]: {total_score}/10 ĐIỂM")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Run retrieval benchmark for Lab 7")
    parser.add_argument(
        "--strategy",
        choices=["heading", "recursive", "sentence", "fixed"],
        default="recursive",
        help="Chunking strategy to benchmark (default: recursive)",
    )
    parser.add_argument(
        "--data-dir",
        default="data/university",
        help="Path to directory containing university corpus markdown files",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Chunk size in characters (default: 500)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Top-K results to retrieve (default: 3)",
    )

    args = parser.parse_args()
    run_benchmark(
        strategy=args.strategy,
        data_dir=args.data_dir,
        top_k=args.top_k,
        chunk_size=args.chunk_size,
    )


if __name__ == "__main__":
    main()
