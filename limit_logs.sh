#!/bin/bash

set -e

echo "======================================"
echo "       Linux 日志自动限制脚本"
echo "======================================"

# 必须 root
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ 请使用 root 运行此脚本"
    exit 1
fi

echo
echo "[1/5] 配置 systemd-journald..."

JOURNAL_CONF="/etc/systemd/journald.conf"

# 备份原配置
if [ ! -f "${JOURNAL_CONF}.bak" ]; then
    cp "$JOURNAL_CONF" "${JOURNAL_CONF}.bak"
    echo "已备份: ${JOURNAL_CONF}.bak"
fi

# 删除旧配置项，避免重复
sed -i \
    -e '/^[[:space:]]*SystemMaxUse=/d' \
    -e '/^[[:space:]]*SystemKeepFree=/d' \
    -e '/^[[:space:]]*SystemMaxFileSize=/d' \
    -e '/^[[:space:]]*MaxRetentionSec=/d' \
    "$JOURNAL_CONF"

cat >> "$JOURNAL_CONF" <<'EOF'

# ===== Custom log limits =====
SystemMaxUse=200M
SystemKeepFree=500M
SystemMaxFileSize=20M
MaxRetentionSec=30day
# ===== End custom log limits =====
EOF

echo "✓ journald 配置完成"


echo
echo "[2/5] 重启 systemd-journald..."

systemctl restart systemd-journald

echo "✓ journald 已重启"


echo
echo "[3/5] 清理旧 journal..."

journalctl --vacuum-size=200M

echo "✓ journal 清理完成"


echo
echo "[4/5] 配置 logrotate..."

LOGROTATE_CONF="/etc/logrotate.conf"

if [ ! -f "${LOGROTATE_CONF}.bak" ]; then
    cp "$LOGROTATE_CONF" "${LOGROTATE_CONF}.bak"
    echo "已备份: ${LOGROTATE_CONF}.bak"
fi

# 修改全局 logrotate 配置
sed -i \
    -e 's/^[[:space:]]*weekly/daily/' \
    -e 's/^[[:space:]]*rotate[[:space:]].*/rotate 7/' \
    -e 's/^[[:space:]]*#*[[:space:]]*compress/compress/' \
    -e 's/^[[:space:]]*#*[[:space:]]*delaycompress/delaycompress/' \
    "$LOGROTATE_CONF"

echo "✓ logrotate 配置完成"


echo
echo "[5/5] 测试 logrotate..."

if logrotate -d /etc/logrotate.conf >/dev/null 2>&1; then
    echo "✓ logrotate 配置正常"
else
    echo "⚠️ logrotate 配置可能存在问题，请检查:"
    echo "   logrotate -d /etc/logrotate.conf"
fi


echo
echo "======================================"
echo "          当前日志占用"
echo "======================================"

echo
echo "📦 systemd journal:"
journalctl --disk-usage

echo
echo "📁 /var/log:"
du -sh /var/log 2>/dev/null || true

echo
echo "💾 磁盘:"
df -h /

echo
echo "======================================"
echo "✓ 日志限制配置完成"
echo "======================================"
