import argparse
import sys
from pathlib import Path

try:
    import pymupdf4llm
except ImportError:
    print("Lỗi: Bạn chưa cài thư viện pymupdf4llm.")
    print("Vui lòng chạy lệnh sau để cài đặt trước khi dùng script:")
    print("pip install pymupdf4llm")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Chuyển đổi file PDF sang Markdown bằng pymupdf4llm (nhanh, đơn giản)")
    parser.add_argument("input_pdf", type=Path, help="Đường dẫn đến file PDF cần chuyển")
    parser.add_argument("--output", "-o", type=Path, help="Đường dẫn lưu file Markdown (mặc định lưu vào data/university/)")
    
    args = parser.parse_args()
    
    if not args.input_pdf.is_file():
        print(f"Lỗi: Không tìm thấy file {args.input_pdf}")
        sys.exit(1)
        
    output_path = args.output
    if not output_path:
        # Mặc định lưu vào thư mục data/university cùng tên với file gốc
        output_dir = Path("data/university")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{args.input_pdf.stem}.md"
        
    print(f"Đang chuyển đổi {args.input_pdf} sang Markdown...")
    try:
        # Gọi hàm to_markdown của pymupdf4llm
        md_text = pymupdf4llm.to_markdown(str(args.input_pdf))
        
        # Ghi ra file
        output_path.write_text(md_text, encoding="utf-8")
        print(f"Thành công! Đã lưu kết quả tại: {output_path}")
        print("\nLưu ý: Bạn có thể cần mở file lên để tự chèn thêm khối Metadata (---) lên đầu file nhé.")
    except Exception as e:
        print(f"Chuyển đổi thất bại: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
