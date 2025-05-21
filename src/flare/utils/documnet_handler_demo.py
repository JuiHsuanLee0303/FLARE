from document_handler import DocumentHandler
import os

def main():
    # 創建 DocumentHandler 實例
    handler = DocumentHandler(chunk_size=20, chunk_overlap=5)
    
    # 示範處理文本文件
    try:
        # 創建一個示例文本文件
        with open("example.txt", "w", encoding="utf-8") as f:
            f.write("這是一個示例文本文件。\n它包含多個段落。\n" * 10)
        
        print("處理文本文件：")
        chunks = handler.process_document("example.txt")
        print(f"文本被分割成 {len(chunks)} 個塊")
        print("第一個塊的內容：")
        print(chunks[0])
        print("第二個塊的內容：")
        print(chunks[1])
        print("\n" + "="*50 + "\n")
        
        # 清理示例文件
        os.remove("example.txt")
        
    except Exception as e:
        print(f"處理文本文件時發生錯誤：{str(e)}")
    
    # 示範如何處理其他類型的文件
    print("要處理 PDF 或 Word 文件，請確保文件存在於正確的路徑：")
    print("PDF 文件示例：")
    print("chunks = handler.process_document('path/to/your/file.pdf')")
    print("\nWord 文件示例：")
    print("chunks = handler.process_document('path/to/your/file.docx')")

if __name__ == "__main__":
    main()
