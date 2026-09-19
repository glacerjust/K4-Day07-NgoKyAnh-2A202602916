import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure the parent directory is in sys.path so we can import src
sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings import OpenAIEmbedder, OPENAI_EMBEDDING_MODEL
from src.chunking import _dot

def main():
    # Load .env from the project root
    load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))
    
    embedder = OpenAIEmbedder(model_name=OPENAI_EMBEDDING_MODEL)

    pairs = [
        ("Sinh viên được đăng ký tối đa 24 tín chỉ", "Sinh viên được đăng ký ít nhất 12 tín chỉ"),
        ("TOEIC 500 là chuẩn đầu ra", "Yêu cầu tiếng Anh cần TOEIC 500"),
        ("Cảnh báo học tập mức 3", "Buộc thôi học do nợ môn"),
        ("Học phí 1,5 lần cho kỳ hè", "Học kỳ hè thu học phí gấp rưỡi"),
        ("Quy chế đào tạo", "Quy định chuẩn ngoại ngữ")
    ]

    print("=" * 60)
    print("DỰ ĐOÁN ĐỘ TƯƠNG TỰ (SIMILARITY PREDICTIONS)")
    print("=" * 60)
    for i, (a, b) in enumerate(pairs, 1):
        emb_a = embedder(a)
        emb_b = embedder(b)
        
        # OpenAI embeddings are pre-normalized, so dot product == cosine similarity
        score = _dot(emb_a, emb_b)
        print(f"Cặp {i}:")
        print(f"  A: {a}")
        print(f"  B: {b}")
        print(f"  -> Score = {score:.4f}\n")

if __name__ == "__main__":
    main()
