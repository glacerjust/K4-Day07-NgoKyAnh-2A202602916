# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ngô Kỳ Anh
**MSSV:** 2412540
**Nhóm:** ACC
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Góc giữa hai vector biểu diễn văn bản rất nhỏ (giá trị cosine gần 1), cho thấy hai văn bản có chung ngữ nghĩa, chủ đề hoặc từ vựng tương đồng rất cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chứng chỉ tiếng Anh phải đánh giá đầy đủ 4 kỹ năng nghe, nói, đọc, viết; đồng thời phải được cấp trong vòng 2 năm tính đến thời điểm xét chuẩn ngoại ngữ đầu ra" (Trích Điều 5 Khoản 2 - Quy định ngoại ngữ K70)
- Câu B: "Thời hạn hiệu lực của chứng chỉ tiếng Anh 4 kỹ năng không được vượt quá 2 năm cho tới lúc sinh viên xét chuẩn đầu ra ngoại ngữ."
- Tại sao tương đồng: Dùng từ vựng khác nhau, độ dài khác nhau nhưng mang chung một ngữ nghĩa cốt lõi về thời hạn (2 năm) và yêu cầu kỹ năng của chứng chỉ ngoại ngữ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chứng chỉ tiếng Anh phải đánh giá đầy đủ 4 kỹ năng nghe, nói, đọc, viết; đồng thời phải được cấp trong vòng 2 năm tính đến thời điểm xét chuẩn ngoại ngữ đầu ra" (Trích Điều 5 Khoản 2 - Quy định ngoại ngữ K70)
- Câu B: "Thời gian tiếp nhận đơn đề nghị xét miễn học phần NNCB muộn nhất là 2 tuần trước khi bắt đầu học kỳ theo Khung kế hoạch năm học." (Trích Điều 3 Khoản 5 - Quy định ngoại ngữ K70)
- Tại sao khác: Mặc dù nằm trong cùng một file quy chế đào tạo nhưng hai câu có bối cảnh và mục đích hành chính hoàn toàn khác biệt (xét chuẩn đầu ra vs thủ tục nộp đơn miễn học phần). Vector embedding của chúng sẽ có khoảng cách góc lớn.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì cosine similarity chỉ quan tâm đến "hướng" (ngữ nghĩa) chứ không bị ảnh hưởng bởi "độ dài" của vector (tương quan với độ dài văn bản). Khoảng cách Euclid sẽ bị sai lệch lớn nếu ta so sánh một câu ngắn và một đoạn văn dài có cùng ý nghĩa, trong khi Cosine vẫn phát hiện được sự tương đồng chính xác.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Bước nhảy thực tế (stride) = chunk_size - overlap = 500 - 50 = 450 ký tự.
> Bỏ qua chunk đầu tiên (500 ký tự), phần còn lại là 9,500 ký tự.
> Số chunk tiếp theo = ceiling(9500 / 450) = ceiling(21.11) = 22.
> *Đáp án:* Tổng cộng cần khoảng 1 + 22 = 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Nếu overlap=100, stride=400, số lượng chunk sẽ tăng lên (khoảng 25 chunks). Ta muốn độ chồng chéo nhiều hơn để tránh trường hợp một câu hoặc một khái niệm quan trọng bị cắt đứt ở ranh giới giữa hai chunk, giúp bảo toàn ngữ cảnh hoàn chỉnh khi vector hóa.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy `re.split(r'([.!?]\s+|\.\n)', text)` để chia văn bản, giữ lại các dấu câu kết thúc (., !, ?). Nhóm các câu lại không vượt quá `max_sentences_per_chunk` và xử lý khoảng trắng thừa bằng `.strip()`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán chia để trị (đệ quy). Base case là khi chuỗi nhỏ hơn `chunk_size` hoặc hết bộ `separators`. Nếu một đoạn nhỏ hơn chunk_size, nó sẽ được ưu tiên ghép lại với phần trước đó bằng dấu phân cách hiện tại để đảm bảo độ dài tối đa mà không bị dư.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ in-memory dưới dạng list of dictionaries, đồng thời lưu vào ChromaDB (nếu có). Tìm kiếm bằng cách tính toán Cosine Similarity trực tiếp giữa vector câu hỏi và vector chunks rồi lấy Top K.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc (filter) trước bằng cách duyệt qua `metadata` của từng chunk in-memory, sau đó mới tính độ tương tự. Xóa (delete) bằng List Comprehension để loại bỏ các chunk có id hoặc doc_id trùng khớp.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Cấu trúc prompt đưa `Context` (các văn bản tìm được nối bằng dấu xuống dòng) lên trước `Question`. Điều này giúp Inject ngữ cảnh cho LLM để nó có đủ dữ kiện trả lời thay vì ảo giác.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
================================================ test session starts =================================================
platform win32 -- Python 3.12.7, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Desktop\K4-L3A-Data-Foundations\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Admin\Desktop\K4-L3A-Data-Foundations
plugins: anyio-4.15.1
collected 42 items                                                                                                    

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                           [  2%] 
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                    [  4%] 
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                             [  7%] 
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                              [  9%] 
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                   [ 11%] 
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                   [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                         [ 16%] 
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                          [ 19%] 
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                        [ 21%] 
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                          [ 23%] 
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                          [ 26%] 
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                     [ 28%] 
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                 [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                           [ 33%] 
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                  [ 35%] 
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                      [ 38%] 
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                [ 40%] 
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                      [ 42%] 
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                          [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                            [ 47%] 
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                              [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                    [ 52%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                         [ 54%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                           [ 57%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED               [ 59%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                            [ 61%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                     [ 64%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                    [ 66%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                               [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                           [ 71%] 
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                      [ 73%] 
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                          [ 76%] 
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                [ 78%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                          [ 80%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED       [ 83%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                     [ 85%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                    [ 88%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED        [ 90%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                   [ 92%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED            [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED  [ 97%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED      [100%] 

================================================= 42 passed in 0.11s =================================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được đăng ký tối đa 24 tín chỉ | Sinh viên được đăng ký ít nhất 12 tín chỉ | thấp | 0.8453 | Sai |
| 2 | TOEIC 500 là chuẩn đầu ra | Yêu cầu tiếng Anh cần TOEIC 500 | cao | 0.7548 | Có |
| 3 | Cảnh báo học tập mức 3 | Buộc thôi học do nợ môn | cao | 0.4357 | Sai |
| 4 | Học phí 1,5 lần cho kỳ hè | Học kỳ hè thu học phí gấp rưỡi | cao | 0.7295 | Có |
| 5 | Quy chế đào tạo | Quy định chuẩn ngoại ngữ | thấp | 0.2635 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp số 1 và số 3 mang lại bất ngờ lớn nhất:
> 1. Ở cặp 1, mô hình chấm điểm cực kỳ cao (0.84) dù hai câu mang nghĩa trái ngược nhau ("tối đa" vs "ít nhất"). Điều này cho thấy Embeddings hiện tại vẫn bị bias (thiên lệch) bởi sự lặp lại từ vựng ("Sinh viên được đăng ký... tín chỉ") mà bỏ qua các từ mang tính phủ định/hạn mức lượng từ.
> 2. Ở cặp 3, ngược lại, mô hình chấm điểm khá thấp (0.43) dù "cảnh báo mức 3" chính là "buộc thôi học do nợ môn" theo luật của Bách Khoa. Điều này chứng tỏ mô hình Embedding tổng quát của OpenAI không có sẵn tri thức ngành (domain-specific knowledge) của trường đại học nếu không được tinh chỉnh (fine-tune) hoặc cung cấp ngữ cảnh đầy đủ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Số tín chỉ tối đa và tối thiểu... | `hust-quy-che-dao-tao-2025` (Sinh viên không thuộc diện cảnh báo... được đăng ký 24 TC...) | 0 / 2 | Không (Do dùng chữ viết tắt 'TC' thay vì 'tín chỉ' nên trượt logic `must_contain`) | Sinh viên được đăng ký tối đa 24 TC và tối thiểu 12 TC. |
| 2 | Cảnh báo học tập mức 3... | `hust-quy-che-dao-tao-2025` (Sinh viên đang bị cảnh báo mức 1 và 2...) | 0 / 2 | Không (Đúng văn bản nhưng sai đoạn, thiếu thông tin về nợ đọng từ đầu khóa) | Ngữ cảnh không đủ để trả lời chính xác điều kiện mức 3. |
| 3 | Mức học phí kỳ hè và sinh viên quốc tế... | `hust-hoc-phi-2025-2026` (Mức học phí sinh viên nước ngoài tự chi trả...) | 2 / 2 | Có (Rất chính xác, Top-1 chứa đầy đủ thông tin) | Tính bằng 1.5 lần mức học phí quy định thông thường. |
| 4 | Chứng chỉ tiếng Anh bắt buộc đánh giá 4 kỹ năng không... | `hust-quy-dinh-ngoai-ngu-k70` (Chứng chỉ tiếng Anh phải đánh giá đầy đủ 4 kỹ năng...) | 1 / 2 | Có (Thông tin đúng nằm ở Top-2 của văn bản K71) | Có, bắt buộc đánh giá đầy đủ 4 kỹ năng nghe, nói, đọc, viết. |
| 5 | Bản dịch tiếng Anh Quy chế đào tạo nhằm mục đích gì... | `hust-ban-dich-tieng-anh-quy-che-dao-tao-2025` (Thông báo công bố bản dịch...) | 1 / 2 | Có (Thông tin mục đích nằm ở Top-2) | Bản dịch mang tính chất tham khảo. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Nhờ xem kết quả của bạn Cảnh (`MarkdownHeadingChunker`), tôi nhận ra sức mạnh của việc tiêm lại (inject) heading vào các đoạn bị cắt nhỏ. Trong khi `RecursiveChunker` của tôi chỉ chia theo độ dài và dấu câu làm mất ngữ cảnh (như ở câu 1 và 5 bị lệch ngữ nghĩa), kỹ thuật tiêm heading giúp chunk giữ được bối cảnh gốc trọn vẹn hơn rất nhiều.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
