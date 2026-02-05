#!/bin/bash

# EduRAG 資料庫初始化管理腳本
# 用法: ./scripts/db-init.sh [command]
# Commands: init, reset, check, backup, restore

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 載入環境變數
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 預設值
POSTGRES_USER=${POSTGRES_USER:-edurag_user}
POSTGRES_DB=${POSTGRES_DB:-edurag}
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# 函數定義
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 檢查 PostgreSQL 連線
check_connection() {
    print_status "檢查資料庫連線..."

    if docker exec edurag_postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; then
        print_status "資料庫連線正常"
        return 0
    else
        print_error "無法連線到資料庫"
        return 1
    fi
}

# 初始化資料庫
init_database() {
    print_status "開始初始化資料庫..."

    # 檢查 PostgreSQL 服務是否運行
    if ! docker ps | grep -q edurag_postgres; then
        print_warning "PostgreSQL 容器未運行，啟動中..."
        docker-compose up -d postgres
        sleep 5
    fi

    # 等待資料庫就緒
    print_status "等待資料庫就緒..."
    for i in {1..30}; do
        if check_connection; then
            break
        fi
        sleep 1
    done

    # 執行初始化腳本
    print_status "執行初始化腳本..."
    docker exec -i edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < backend/db/init.sql

    if [ $? -eq 0 ]; then
        print_status "資料庫初始化完成！"
        check_database
    else
        print_error "資料庫初始化失敗"
        exit 1
    fi
}

# 重置資料庫
reset_database() {
    print_warning "即將重置資料庫，這將刪除所有資料！"
    read -p "確定要繼續嗎？ (y/N): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_status "操作已取消"
        exit 0
    fi

    print_status "停止服務..."
    docker-compose down

    print_status "清除資料 volumes..."
    docker volume rm edurag_postgres_data 2>/dev/null || true

    print_status "重新啟動服務..."
    docker-compose up -d postgres

    # 等待服務就緒
    sleep 10

    # 重新初始化
    init_database
}

# 檢查資料庫狀態
check_database() {
    print_status "檢查資料庫狀態..."

    if ! check_connection; then
        exit 1
    fi

    # 執行健康檢查
    print_status "執行健康檢查..."
    docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM check_database_health();" 2>/dev/null || {
        print_warning "健康檢查函數不存在，執行基本檢查..."

        # 基本表檢查
        for table in subjects templates documents questions embeddings; do
            count=$(docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "N/A")
            printf "  %-15s: %s rows\n" "$table" "$count"
        done
    }

    # 檢查擴充套件
    print_status "檢查擴充套件..."
    docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\dx vector" | grep -q vector
    if [ $? -eq 0 ]; then
        print_status "✓ pgvector 擴充套件已安裝"
    else
        print_error "✗ pgvector 擴充套件未安裝"
    fi
}

# 備份資料庫
backup_database() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backup/edurag_backup_$timestamp.sql"

    print_status "建立備份目錄..."
    mkdir -p backup

    print_status "備份資料庫到 $backup_file..."
    docker exec edurag_postgres pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > $backup_file

    if [ $? -eq 0 ]; then
        print_status "備份完成！檔案: $backup_file"
        print_status "檔案大小: $(du -h $backup_file | cut -f1)"
    else
        print_error "備份失敗"
        exit 1
    fi
}

# 還原資料庫
restore_database() {
    if [ -z "$2" ]; then
        print_error "請指定備份檔案"
        echo "用法: $0 restore <backup_file>"
        exit 1
    fi

    backup_file=$2

    if [ ! -f "$backup_file" ]; then
        print_error "備份檔案不存在: $backup_file"
        exit 1
    fi

    print_warning "即將還原資料庫，這將覆蓋現有資料！"
    read -p "確定要繼續嗎？ (y/N): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_status "操作已取消"
        exit 0
    fi

    print_status "還原資料庫..."
    docker exec -i edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < $backup_file

    if [ $? -eq 0 ]; then
        print_status "還原完成！"
        check_database
    else
        print_error "還原失敗"
        exit 1
    fi
}

# 顯示使用說明
show_help() {
    echo "EduRAG 資料庫管理工具"
    echo ""
    echo "用法: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  init     - 初始化資料庫（保留現有資料）"
    echo "  reset    - 重置資料庫（刪除所有資料）"
    echo "  check    - 檢查資料庫狀態"
    echo "  backup   - 備份資料庫"
    echo "  restore  - 還原資料庫"
    echo "  help     - 顯示此說明"
    echo ""
    echo "Examples:"
    echo "  $0 init                          # 初始化資料庫"
    echo "  $0 reset                         # 重置資料庫"
    echo "  $0 check                         # 檢查狀態"
    echo "  $0 backup                        # 建立備份"
    echo "  $0 restore backup/file.sql       # 還原備份"
}

# 主程式
case "$1" in
    init)
        init_database
        ;;
    reset)
        reset_database
        ;;
    check)
        check_database
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知指令: $1"
        show_help
        exit 1
        ;;
esac