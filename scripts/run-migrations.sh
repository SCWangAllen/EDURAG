#!/bin/bash

# EduRAG 資料庫遷移腳本
# 用法: ./scripts/run-migrations.sh [migration_file]

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
MIGRATIONS_DIR="backend/migrations"

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

print_migration() {
    echo -e "${BLUE}[MIGRATION]${NC} $1"
}

# 檢查 PostgreSQL 連線
check_connection() {
    if docker exec edurag_postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; then
        return 0
    else
        print_error "無法連線到資料庫"
        return 1
    fi
}

# 執行單一遷移檔案
run_migration() {
    local migration_file=$1
    local filename=$(basename "$migration_file")

    print_migration "執行遷移: $filename"

    if [ ! -f "$migration_file" ]; then
        print_error "遷移檔案不存在: $migration_file"
        return 1
    fi

    # 執行遷移
    docker exec -i edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < "$migration_file"

    if [ $? -eq 0 ]; then
        print_status "✓ 遷移完成: $filename"
        return 0
    else
        print_error "✗ 遷移失敗: $filename"
        return 1
    fi
}

# 執行所有待執行的遷移
run_all_migrations() {
    print_status "掃描遷移目錄: $MIGRATIONS_DIR"

    if [ ! -d "$MIGRATIONS_DIR" ]; then
        print_error "遷移目錄不存在: $MIGRATIONS_DIR"
        exit 1
    fi

    # 建立遷移追蹤表（如果不存在）
    print_status "檢查遷移追蹤表..."
    docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_file VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'success'
        );
    " > /dev/null 2>&1

    # 取得已執行的遷移
    applied_migrations=$(docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -t -c "
        SELECT migration_file FROM schema_migrations WHERE status = 'success';
    " | tr -d ' ' | grep -v '^$')

    # 掃描並執行新遷移
    migration_count=0
    for migration_file in $(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | sort); do
        filename=$(basename "$migration_file")

        # 檢查是否已執行
        if echo "$applied_migrations" | grep -q "^$filename$"; then
            print_status "⊙ 已執行: $filename"
            continue
        fi

        # 執行新遷移
        if run_migration "$migration_file"; then
            # 記錄成功執行的遷移
            docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
                INSERT INTO schema_migrations (migration_file, status)
                VALUES ('$filename', 'success')
                ON CONFLICT (migration_file) DO UPDATE SET
                    applied_at = CURRENT_TIMESTAMP,
                    status = 'success';
            " > /dev/null 2>&1
            migration_count=$((migration_count + 1))
        else
            # 記錄失敗的遷移
            docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
                INSERT INTO schema_migrations (migration_file, status)
                VALUES ('$filename', 'failed')
                ON CONFLICT (migration_file) DO UPDATE SET
                    applied_at = CURRENT_TIMESTAMP,
                    status = 'failed';
            " > /dev/null 2>&1
            print_error "遷移失敗，停止執行"
            exit 1
        fi
    done

    if [ $migration_count -eq 0 ]; then
        print_status "沒有新的遷移需要執行"
    else
        print_status "成功執行 $migration_count 個遷移"
    fi
}

# 顯示遷移狀態
show_migration_status() {
    print_status "遷移執行歷史："

    docker exec edurag_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
        SELECT
            id,
            migration_file,
            applied_at,
            status
        FROM schema_migrations
        ORDER BY id;
    " 2>/dev/null || {
        print_warning "遷移追蹤表不存在"
    }
}

# 顯示使用說明
show_help() {
    echo "EduRAG 資料庫遷移工具"
    echo ""
    echo "用法: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  run [file]  - 執行指定的遷移檔案"
    echo "  all         - 執行所有待執行的遷移"
    echo "  status      - 顯示遷移執行狀態"
    echo "  help        - 顯示此說明"
    echo ""
    echo "Examples:"
    echo "  $0 all                                    # 執行所有待執行的遷移"
    echo "  $0 run backend/migrations/002_*.sql       # 執行指定遷移"
    echo "  $0 status                                 # 查看遷移狀態"
}

# 主程式
main() {
    # 檢查 Docker 容器是否運行
    if ! docker ps | grep -q edurag_postgres; then
        print_error "PostgreSQL 容器未運行"
        print_status "請先執行: docker-compose up -d postgres"
        exit 1
    fi

    # 檢查資料庫連線
    if ! check_connection; then
        exit 1
    fi

    case "$1" in
        run)
            if [ -z "$2" ]; then
                print_error "請指定遷移檔案"
                show_help
                exit 1
            fi
            run_migration "$2"
            ;;
        all)
            run_all_migrations
            ;;
        status)
            show_migration_status
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            print_error "未知指令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
