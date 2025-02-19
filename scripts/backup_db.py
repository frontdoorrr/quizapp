import sys
import os
import subprocess
from datetime import datetime
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings

def backup_database(backup_dir: str = "backups"):
    """데이터베이스 백업"""
    settings = get_settings()
    
    # 백업 디렉토리 생성
    os.makedirs(backup_dir, exist_ok=True)
    
    # 데이터베이스 URL에서 정보 추출
    db_url = settings.database_url
    db_info = {
        "host": db_url.split("@")[1].split(":")[0],
        "port": db_url.split(":")[3].split("/")[0],
        "user": db_url.split("://")[1].split(":")[0],
        "password": db_url.split(":")[2].split("@")[0],
        "database": db_url.split("/")[-1]
    }
    
    # 백업 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")
    
    # pg_dump 명령어 실행
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = db_info["password"]
        
        command = [
            "pg_dump",
            "-h", db_info["host"],
            "-p", db_info["port"],
            "-U", db_info["user"],
            "-d", db_info["database"],
            "-f", backup_file
        ]
        
        subprocess.run(command, env=env, check=True)
        print(f"Database backup created successfully: {backup_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating database backup: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during backup: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup database")
    parser.add_argument("--backup-dir", default="backups", help="Directory to store backups")
    
    args = parser.parse_args()
    backup_database(args.backup_dir)
