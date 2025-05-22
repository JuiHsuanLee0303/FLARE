from main import LLMHandler
import logging
import time

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 初始化 LLMHandler
    model_path = "lora_model"  # 使用相對路徑
    
    # 自定義生成配置
    generation_config = {
        "max_new_tokens": 256,  # 減少生成的 token 數量
        "temperature": 0.8,     # 增加創造性
        "top_p": 0.95,         # 增加多樣性
        "do_sample": True,      # 啟用採樣
        "num_return_sequences": 1  # 返回序列數量
    }
    
    try:
        # 創建 LLMHandler 實例，啟用 CPU 模式
        llm = LLMHandler(
            fine_tuned_model_path=model_path,
            generation_config=generation_config,
            max_retries=3,
            retry_delay=1.0,
            use_cpu=True  # 強制使用 CPU
        )
        
        # 載入模型
        logger.info("開始載入模型...")
        llm.load_fine_tuned_model()
        logger.info("模型載入完成")
        
        # 測試生成
        test_cases = [
            {
                "instruction": "請解釋什麼是機器學習",
                "input": "用簡單的語言解釋"
            },
            {
                "instruction": "寫一首關於春天的詩",
                "input": "使用中文"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n測試案例 {i}:")
            logger.info(f"指令: {test_case['instruction']}")
            logger.info(f"輸入: {test_case['input']}")
            
            start_time = time.time()
            response = llm.generate_fine_tuned_response(
                instruction=test_case['instruction'],
                input_text=test_case['input']
            )
            end_time = time.time()
            
            logger.info(f"回應: {response}")
            logger.info(f"生成時間: {end_time - start_time:.2f} 秒")
            
            # 測試快取功能
            logger.info("\n測試快取功能（第二次生成應該更快）...")
            start_time = time.time()
            response = llm.generate_fine_tuned_response(
                instruction=test_case['instruction'],
                input_text=test_case['input']
            )
            end_time = time.time()
            logger.info(f"快取生成時間: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        logger.error(f"發生錯誤: {str(e)}")
    finally:
        # 清理資源
        if 'llm' in locals():
            llm.close()
            logger.info("資源已清理")

if __name__ == "__main__":
    main()
