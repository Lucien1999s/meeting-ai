#!/usr/bin/env python3
"""
AI Meeting Generator Runner
專業化的會議記錄生成器執行腳本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """設置環境變數"""
    # 載入 .env 檔案
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("已載入 .env 檔案")
    else:
        logger.warning("未找到 .env 檔案，將使用系統環境變數")

def validate_config(config):
    """驗證配置參數"""
    required_fields = ['meeting_name', 'file_path', 'api_key']
    
    for field in required_fields:
        if not config.get(field):
            raise ValueError(f"缺少必要參數: {field}")
    
    # 檢查檔案是否存在
    if not Path(config['file_path']).exists():
        raise FileNotFoundError(f"音頻檔案不存在: {config['file_path']}")
    
    # 檢查 API 金鑰格式
    if not config['api_key'].startswith('sk-'):
        logger.warning("API 金鑰格式可能不正確")

def main():
    """主要執行函數"""
    try:
        # 設置環境
        setup_environment()
        
        # 配置參數
        config = {
            'meeting_name': "儒林會議",
            'file_path': os.getenv('AUDIO_FILE_PATH', "/Users/lucienlin/Downloads/儒林2.m4a"),
            'api_key': os.getenv('OPENAI_API_KEY'),
            'audio_model': os.getenv('AUDIO_MODEL', "base"),
            'text_model': os.getenv('TEXT_MODEL', "gpt-4"),
        }
        
        # 驗證配置
        validate_config(config)
        
        # 導入和執行
        logger.info(f"開始處理會議: {config['meeting_name']}")
        
        try:
            from src.ai_meeting_generator import run
        except ImportError as e:
            logger.error(f"無法導入模組: {e}")
            sys.exit(1)
        
        # 執行會議生成
        result = run(
            meeting_name=config['meeting_name'],
            file_path=config['file_path'],
            api_key=config['api_key'],
            audio_model=config['audio_model'],
            text_model=config['text_model'],
        )
        
        logger.info("會議記錄生成完成")
        return result
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()