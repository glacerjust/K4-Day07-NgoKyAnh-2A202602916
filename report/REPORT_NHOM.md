# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** ACC
**Thành viên:** Đinh Tiến Cảnh, Ngô Kỳ Anh, Nguyễn Quốc Cường
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế đào tạo, quy định chuẩn ngoại ngữ và chính sách học phí — Đại học Bách khoa Hà Nội (HUST).

**Tại sao nhóm chọn chủ đề này?**
> Bộ tài liệu bao gồm các văn bản quy chế, quy định học vụ và chính sách học phí chính thức, công khai của Đại học Bách khoa Hà Nội (Quy chế đào tạo năm 2025 theo QĐ 5445/QĐ-ĐHBK, Quy định chuẩn ngoại ngữ các khóa K70 và K71, Thông báo bản dịch tiếng Anh và Quyết định mức học phí năm học 2025-2026). Các văn bản có cấu trúc rõ ràng (điều, khoản, bảng biểu chuẩn đầu ra, khung học phí), chứa nhiều mốc số liệu định lượng, thời hạn cụ thể và phân loại theo phòng ban (`academic-affairs` vs `finance`) và danh mục (`regulations`, `language-requirements`, `tuition`), rất phù hợp để thử nghiệm các chiến lược chunking và kiểm thử truy xuất kết hợp lọc metadata (`metadata_filter`).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định ngoại ngữ từ khóa K71 (Đại học Bách khoa Hà Nội) | https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/00_%20Quy%20%C4%91%E1%BB%8Bnh%20ngo%E1%BA%A1i%20ng%E1%BB%AF%20K71_final_%C4%91%C3%A3%20k%C3%BD.pdf | 2026-09-19 / 10828/QĐ-ĐHBK (2026-09-07) | 63,532 | doc_id: hust-quy-dinh-ngoai-ngu-k71, audience: student, category: language-requirements, department: academic-affairs |
| 2 | Quy định ngoại ngữ từ khóa K70 (Đại học Bách khoa Hà Nội) | https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/06_%20Quy%20%C4%91%E1%BB%8Bnh%20ngo%E1%BA%A1i%20ng%E1%BB%AF%20t%E1%BB%AB%20K70_ch%C3%ADnh%20quy_final.pdf | 2026-09-19 / not-stated | 67,376 | doc_id: hust-quy-dinh-ngoai-ngu-k70, audience: student, category: language-requirements, department: academic-affairs |
| 3 | Học phí năm học 2025-2026 (Đại học Bách khoa Hà Nội) | https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hocphi/2025-2026/QD%20HOC%20PHI%20-%202025-2026-final.pdf | 2026-09-19 / 10232/QĐ-ĐHBK (2025-09-12) | 14,190 | doc_id: hust-hoc-phi-2025-2026, audience: student, category: tuition, department: finance |
| 4 | Thông báo công bố bản dịch tiếng Anh Quy chế đào tạo năm 2025 (Đại học Bách khoa Hà Nội) | https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/03_%20TB%20cong%20bo%20ban%20dich%20tieng%20Anh%20QCDT%202025.pdf | 2026-09-19 / not-stated | 2,332 | doc_id: hust-ban-dich-tieng-anh-quy-che-dao-tao-2025, audience: all, category: regulations, department: academic-affairs |
| 5 | Quy chế đào tạo năm 2025 (Đại học Bách khoa Hà Nội) | https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf | 2026-09-19 / 5445/QĐ-ĐHBK (2025-05-28) | 77,924 | doc_id: hust-quy-che-dao-tao-2025, audience: student, category: regulations, department: academic-affairs |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

Hệ thống sử dụng cấu trúc metadata chuẩn hóa để hỗ trợ cả **truy xuất ngữ nghĩa (semantic search)** và **truy xuất có điều kiện (filtered retrieval)**:

| Trường metadata | Kiểu dữ liệu | Giá trị hợp lệ / Ví dụ | Mục đích & Lợi ích cho truy xuất (Retrieval) |
|---|---|---|---|
| `doc_id` | `string` | `hust-quy-che-dao-tao-2025`, `hust-hoc-phi-2025-2026` | Định danh tài liệu duy nhất (unique ID). Giúp liên kết chính xác chunk với tài liệu gốc, hỗ trợ trích dẫn nguồn (citation) và loại bỏ trùng lặp khi tổng hợp kết quả. |
| `title` | `string` | `Quy chế đào tạo năm 2025 (Đại học Bách khoa Hà Nội)` | Cung cấp ngữ cảnh cấp tài liệu (document context) khi hiển thị nguồn trích dẫn cho người dùng và hỗ trợ reranking/tiền xử lý câu hỏi. |
| `source_url` | `string` (URL) | `https://ctt.hust.edu.vn/.../QCDT_2025_5445_QD-DHBK.pdf` | Đảm bảo tính kiểm chứng (provenance), dẫn link trực tiếp tới văn bản gốc chính thức của nhà trường. |
| `retrieved_at` | `string` (ISO Date `YYYY-MM-DD`) | `2026-09-19` | Ghi nhận thời điểm thu thập dữ liệu; hữu ích để kiểm soát phiên bản và cảnh báo dữ liệu hết hạn hoặc cần tái thu thập (data freshness). |
| `document_version` | `string` | `5445/QĐ-ĐHBK (2025-05-28)`, `10828/QĐ-ĐHBK (2026-09-07)`, `not-stated` | Xác định số hiệu văn bản pháp lý và ngày ban hành, giúp phân biệt rõ quy chế đang áp dụng với các quy chế cũ, giải quyết câu hỏi về tính pháp lý. |
| `audience` | `string` (Enum) | `student`, `all` | Phân loại đối tượng áp dụng (sinh viên hoặc toàn thể cán bộ/giảng viên/sinh viên). Cho phép lọc nhanh phạm vi áp dụng qua `metadata_filter={"audience": "student"}`. |
| `department` | `string` (Enum) | `academic-affairs`, `finance` | Xác định đơn vị quản lý chuyên môn (Phòng Đào tạo / Phòng Tài chính - Kế toán). Giúp thu hẹp không gian tìm kiếm khi truy vấn câu hỏi chuyên sâu về học phí hay học vụ. |
| `category` | `string` (Enum) | `regulations`, `language-requirements`, `tuition` | Phân loại mảng nội dung chuyên biệt. Rất quan trọng khi truy xuất các câu hỏi đặc thù (ví dụ: lọc `category="language-requirements"` để tránh nhầm quy định ngoại ngữ K70/K71 với quy chế chung). |
| `language` | `string` (ISO 639-1) | `vi` | Định rõ ngôn ngữ văn bản để lựa chọn embedding model phù hợp (hỗ trợ tiếng Việt hoặc đa ngôn ngữ). |
| `license_or_permission` | `string` | `public-source` | Xác nhận tính hợp pháp, phạm vi cấp phép dữ liệu công khai theo quy định quản trị dữ liệu. |

#### Ứng dụng của Metadata trong việc cải thiện chất lượng Retrieval:
1. **Tránh nhầm lẫn giữa các khóa/đối tượng (Disambiguation):** Các văn bản ngoại ngữ K70 và K71 có cấu trúc và thuật ngữ tương đồng nhưng chuẩn đầu ra khác nhau. Bằng cách kết hợp `doc_id` hoặc `document_version` trong metadata, retriever tránh tình trạng trả về nhầm chuẩn ngoại ngữ giữa các khóa.
2. **Thu hẹp không gian tìm kiếm (Search Space Pruning):** Khi người dùng hỏi về học phí (`category: "tuition"` hoặc `department: "finance"`), retriever có thể lọc trước (pre-filtering) hoặc lọc sau (post-filtering) để chỉ quét qua các chunk thuộc văn bản tài chính, loại bỏ 100% nhiễu từ các quy chế học vụ dài hàng chục nghìn ký tự.
3. **Cung cấp bằng chứng minh bạch (Provenance & Grounding):** Mọi chunk khi được trích xuất đều kèm theo `title`, `source_url` và `document_version` giúp câu trả lời của hệ thống RAG có thể trích dẫn chính xác số hiệu quyết định và đường link đối soát.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện (đã loại bỏ frontmatter YAML):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `hust-hoc-phi-2025-2026.md` | FixedSizeChunker (`fixed_size`) | 31 | 485.6 ký tự | Kém — Dễ cắt ngang giữa các dòng bảng học phí và phân mục. |
| `hust-hoc-phi-2025-2026.md` | SentenceChunker (`by_sentences`) | 19 | 709.1 ký tự | Trung bình — Bảng biểu bị dồn vào các câu rất dài do ít dấu chấm kết câu. |
| `hust-hoc-phi-2025-2026.md` | RecursiveChunker (`recursive`) | 40 | 337.1 ký tự | Tốt — Tách tốt theo dòng và đoạn văn, không làm rách bảng. |
| `hust-quy-che-dao-tao-2025.md` | FixedSizeChunker (`fixed_size`) | 172 | 499.2 ký tự | Kém — Cắt vụn các điều khoản dài, mất tiêu đề Điều ở nửa sau. |
| `hust-quy-che-dao-tao-2025.md` | SentenceChunker (`by_sentences`) | 215 | 356.1 ký tự | Khá — Giữ câu trọn vẹn nhưng các khoản nhỏ bị tách rời khỏi tên Điều. |
| `hust-quy-che-dao-tao-2025.md` | RecursiveChunker (`recursive`) | 204 | 377.1 ký tự | Tốt — Tôn trọng cấu trúc phân đoạn `\n\n` và `\n` của quy chế. |
| `hust-quy-dinh-ngoai-ngu-k71.md` | FixedSizeChunker (`fixed_size`) | 140 | 497.9 ký tự | Kém — Rách bảng quy đổi chứng chỉ và phụ lục. |
| `hust-quy-dinh-ngoai-ngu-k71.md` | SentenceChunker (`by_sentences`) | 51 | 1222.0 ký tự | Kém — Do bảng markdown không có dấu chấm câu nên chunk bị phình to (1222 chars). |
| `hust-quy-dinh-ngoai-ngu-k71.md` | RecursiveChunker (`recursive`) | 166 | 376.7 ký tự | Tốt — Tách theo dòng bảng và phân mục phụ lục rất ổn định. |

### Chiến lược của từng thành viên

**Thành viên 1 — Đinh Tiến Cảnh**
- **Loại chiến lược:** Custom `MarkdownHeadingChunker` (Phân mảnh theo tiêu đề kết hợp tiêm ngữ cảnh phân cấp).
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy phạm pháp luật và quy chế đại học có cấu trúc phân cấp cực kỳ chặt chẽ theo từng Điều/Khoản (`## Điều X...`). Chiến lược này tách văn bản tại từng tiêu đề Markdown và Điều luật. Nếu một Điều quá dài (> 600 ký tự), thuật toán chuyển sang `RecursiveChunker` và tự động gắn tiền tố tiêu đề `[Tên Điều]` vào từng mảnh con, giúp mọi chunk đều giữ được ngữ cảnh toàn cục.
- **Code snippet (nếu custom):**
```python
class MarkdownHeadingChunker:
    def __init__(self, max_chunk_size: int = 600) -> None:
        self.max_chunk_size = max_chunk_size
        self.recursive_fallback = RecursiveChunker(separators=["\n\n", "\n", ". ", " "], chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        lines = text.split("\n")
        sections, current_heading, current_lines = [], "Mở đầu", []
        for line in lines:
            m = re.match(r"^(#{1,4}\s+.*|\*{0,2}Điều\s+\d+.*)", line.strip())
            if m:
                if current_lines: sections.append((current_heading, current_lines))
                current_heading, current_lines = m.group(0).strip("#* "), [line]
            else: current_lines.append(line)
        if current_lines: sections.append((current_heading, current_lines))
        chunks = []
        for heading, s_lines in sections:
            content = "\n".join(s_lines).strip()
            if len(content) <= self.max_chunk_size:
                chunks.append(content)
            else:
                for sc in self.recursive_fallback.chunk(content):
                    chunks.append(f"[{heading}]\n{sc}" if not sc.startswith(heading) else sc)
        return chunks
```

**Thành viên 2 — Ngô Kỳ Anh**
- **Loại chiến lược:** `RecursiveChunker` (chunk_size=500, separators=["\n\n", "\n", ". ", " ", ""]).
- **Mô tả & lý do chọn:** Quy chế đào tạo gồm nhiều đoạn văn bản pháp lý với các điểm a, b, c xuống dòng liên tục. Recursive chunking ưu tiên chia nhỏ tại các ngắt đoạn lớn (`\n\n`) rồi tới xuống dòng (`\n`), tránh việc xé nhỏ câu giữa chừng và đảm bảo các đoạn nội dung không vượt quá kích thước 500 ký tự.
- **Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=500, separators=["\n\n", "\n", ". ", " ", ""])
chunks = chunker.chunk(document_body)
```

**Thành viên 3 — Nguyễn Quốc Cường**
- **Loại chiến lược:** `SentenceChunker` (max_sentences_per_chunk=3).
- **Mô tả & lý do chọn:** Tiếp cận theo đơn vị ngữ pháp tự nhiên của câu. Gom nhóm 3 câu liên tiếp để tạo thành một khối thông tin có nghĩa tương đối trọn vẹn, phù hợp với các câu hỏi tra cứu định nghĩa, mốc thời gian hoặc điều kiện đơn lẻ.
- **Code snippet (nếu custom):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=3)
chunks = chunker.chunk(document_body)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Đinh Tiến Cảnh | `MarkdownHeadingChunker` | 8 / 10 | Giữ trọn vẹn ngữ cảnh Điều/Khoản nhờ context injection; truy xuất chính xác Top-1 ở các câu hỏi điều khoản học vụ. | Phức tạp hơn trong triển khai; phụ thuộc vào tính chuẩn hóa của heading Markdown. |
| Ngô Kỳ Anh | `RecursiveChunker` | 7 / 10 | Xử lý mượt mà văn bản nhiều bảng biểu và ngắt dòng; độ dài chunk đồng đều (~370 ký tự). | Các chunk con ở phía sau của một Điều dài bị mất tiêu đề Điều dẫn đến giảm độ tương đồng ngữ nghĩa. |
| Nguyễn Quốc Cường | `SentenceChunker` | 6 / 10 | Cấu trúc câu hoàn chỉnh, không bị cụt câu; số lượng chunk ít hơn. | Gặp khó khăn lớn với bảng Markdown (do bảng không có dấu chấm kết câu khiến chunk bị kéo dài hơn 1200 ký tự). |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Chiến lược `MarkdownHeadingChunker` (theo Heading/Section kết hợp Context Injection) là tối ưu nhất cho văn bản quy định đại học.* Do văn bản pháp quy được tổ chức theo từng Điều/Khoản độc lập, việc chunk theo ranh giới heading giữ trọn một đơn vị logic; đồng thời kỹ thuật tiêm lại tiêu đề `[Tên Điều]` vào các chunk con giải quyết triệt để vấn đề mất ngữ cảnh khi một điều khoản quá dài phải chia nhỏ.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên chương trình đại học không bị cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính? | Sinh viên không bị cảnh báo học tập được đăng ký tối đa 24 tín chỉ và tối thiểu 12 tín chỉ trong học kỳ chính. Không áp dụng ngưỡng đăng ký tối thiểu với sinh viên trình độ năm cuối. | `hust-quy-che-dao-tao-2025` (Khoản 1 Điều 10) |
| 2 | Khi nào sinh viên bị nâng một mức cảnh báo học tập và khi nào bị áp dụng cảnh báo học tập mức 3? | Nâng 1 mức cảnh báo khi số tín chỉ không đạt trong học kỳ > 8 TC. Áp dụng cảnh báo mức 3 khi số tín chỉ nợ đọng từ đầu khóa > 24 TC. | `hust-quy-che-dao-tao-2025` (Khoản 1 Điều 19) |
| 3 | Mức học phí các học phần học trong học kỳ hè và mức học phí đối với sinh viên nước ngoài tự chi trả được tính bằng bao nhiêu lần mức học phí thông thường? | Mức học phí học kỳ hè và mức học phí đối với sinh viên nước ngoài tự chi trả kinh phí học tập đều được tính bằng 1,5 lần mức học phí quy định thông thường. *(Có lọc metadata: `department: "finance"`)* | `hust-hoc-phi-2025-2026` (Phụ lục I, Mục 5) |
| 4 | Chứng chỉ tiếng Anh nộp để xét chuẩn ngoại ngữ đầu ra có bắt buộc phải đánh giá đủ 4 kỹ năng không? | Có, chứng chỉ tiếng Anh phải đánh giá đầy đủ 4 kỹ năng nghe, nói, đọc, viết; được cấp bởi các đơn vị hợp pháp và có hiệu lực 02 năm tính đến ngày nộp hồ sơ. *(Có lọc metadata: `category: "language-requirements"`)* | `hust-quy-dinh-ngoai-ngu-k71` (Khoản 2 Điều 5) |
| 5 | Văn bản bản dịch tiếng Anh của Quy chế đào tạo năm 2025 được ban hành nhằm mục đích gì và có giá trị pháp lý thay thế văn bản gốc tiếng Việt không? | Bản dịch tiếng Anh phục vụ giảng dạy, học tập, trao đổi sinh viên quốc tế và kiểm định quốc tế; mang tính chất tham khảo, văn bản gốc tiếng Việt có giá trị pháp lý cao nhất nếu có khác biệt. | `hust-ban-dich-tieng-anh-quy-che-dao-tao-2025` (Mục 1 & 2 Thông báo 2034) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Số tín chỉ tối đa/tối thiểu đăng ký học kỳ chính | `MarkdownHeadingChunker` | Có (Top-1, Score: 0.4100) | Trích xuất chính xác Điều 10 nhờ giữ được tiêu đề phân mục. |
| 2 | Điều kiện nâng mức cảnh báo và cảnh báo mức 3 | `MarkdownHeadingChunker` / `Recursive` | Có (Top-1, Score: 0.3630) | Trích xuất đúng Điều 19 Quy chế đào tạo. |
| 3 | Học phí học kỳ hè và sinh viên nước ngoài | `MarkdownHeadingChunker` + Filter | Có (Top-1, Score: 0.2085) | Lọc `department="finance"` loại bỏ 100% nhiễu học vụ, trả về đúng bảng học phí Phụ lục I. |
| 4 | Yêu cầu 4 kỹ năng chứng chỉ tiếng Anh đầu ra | `RecursiveChunker` / `Heading` + Filter | Có (Top-1/Top-3, Score: 0.3695) | Lọc `category="language-requirements"` giúp trỏ đúng văn bản ngoại ngữ K71. |
| 5 | Mục đích và tính pháp lý của bản dịch tiếng Anh | `SentenceChunker` / `Heading` | Chưa đạt trong MockEmbedder (Score thấp) | Do file bản dịch tiếng Anh ngắn (2.3k chars) và dùng mock embedding băm chuỗi nên bị lấn át bởi các chunk dài khác. Cần semantic embedding thực tế. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Lọc bằng metadata mang lại hiệu quả vượt trội ở Câu 3 và Câu 4.* Ở Câu 3, nếu không lọc `department: "finance"`, câu hỏi về học phí dễ bị nhầm sang các quy định thu học phí lặp lại trong quy chế chung. Ở Câu 4, việc lọc `category: "language-requirements"` giúp loại bỏ toàn bộ hàng trăm chunk từ quy chế chung và học phí, định vị chính xác văn bản quy định ngoại ngữ chuyên biệt.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Sức mạnh của cấu trúc tài liệu (Domain-specific Chunking):** Với văn bản quy chế đại học, chia nhỏ theo cấu trúc Heading/Điều khoản tự nhiên vượt trội hoàn toàn so với chia cắt cứng nhắc theo độ dài cố định (Fixed-size).
2. **Kỹ thuật Context Injection:** Khi bắt buộc phải cắt một đoạn dài, việc tự động tiêm lại tiêu đề phân mục cha `[Tên Điều]` vào từng mảnh con giúp chunk giữ nguyên ngữ cảnh ngữ nghĩa độc lập.
3. **Vai trò then chốt của Metadata Pre-filtering:** Metadata filtering là chìa khóa để phân tách các quy định có thuật ngữ trùng lặp (ví dụ: chuẩn ngoại ngữ K70 vs K71, học phí vs quy chế học vụ).

**Bài học rút ra khi so sánh trong nhóm:**
> Khi so sánh giữa 3 thành viên, nhóm nhận thấy `FixedSize` và `SentenceChunker` dễ làm vỡ cấu trúc bảng biểu Markdown (đặc biệt trong văn bản học phí và chuẩn ngoại ngữ), trong khi `RecursiveChunker` và `MarkdownHeadingChunker` kiểm soát ranh giới phân tách tốt hơn nhiều.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa trước các bảng Markdown phức tạp thành cấu trúc cặp key-value hoặc danh sách rút gọn trước khi đưa vào pipeline chunking; đồng thời bổ sung thêm trường metadata `target_cohort` (ví dụ `K70`, `K71`) để lọc trực tiếp theo khóa tuyển sinh của sinh viên.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 0 / 5 |
| **Tổng phần nhóm** | **33 / 40** |
