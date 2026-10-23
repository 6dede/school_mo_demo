'''
全局公共配置
'''
import logging
from pathlib import Path

import pymysql

# 日志固定写到 org/ 目录，避免受启动目录影响
LOG_FILE = Path(__file__).resolve().parents[2] / "教务管理系统，log"

DB_CONFIG = {
    "host": "localhost",
    "port":3306,
    "user": "root",
    "password": "123456",
    "database": "schaool_db_study",
    "charset":"utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}
logging.basicConfig(
    level=logging.INFO,
    #asctime:时间戳，threadName:当前运行线程名称
    #levelname:日志输出级别 name:模块名称 message:日志信息
    # format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
    format="%(asctime)s - %(threadName)s - [%(levelname)s] - %(name)s:%(message)s",
    handlers=[#配置日志输出目标类型
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
MAX_PAGE_SIZE = 100