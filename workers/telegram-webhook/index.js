/**
 * Cloudflare Worker — Telegram → GitHub Actions 中转站
 *
 * 零安装部署：直接粘贴到 Cloudflare Workers 网页编辑器即可
 *
 * 部署步骤（不用装任何东西）:
 *   1. 打开 https://dash.cloudflare.com → Workers & Pages → 创建 Worker
 *   2. 把下面 ===== 配置区域 ===== 的三个值改成你自己的
 *   3. 全选粘贴到编辑器 → 点右上角 "部署"
 *   4. 记下 Worker URL（如 gzhu-score-bot.xxxx.workers.dev）
 *   5. 在本机运行: python -m src.main --set-webhook https://你的URL.workers.dev
 */

// =======================================================================
// ★ 配置区域 — 改成你自己的值
// =======================================================================
const TELEGRAM_BOT_TOKEN = '8057655456:AAFcQyccg582ExDAZ2TZlcLADrNyp6t9oB0';  // @BotFather 给的 token
const GITHUB_PAT         = 'ghp_xxxxxxxxxxxxxxxxxxxx';                    // GitHub Personal Access Token（勾选 workflow 权限）
const GITHUB_REPO        = 'K1ssuh2rd/gzhu-score-monitor';               // 你的 GitHub 仓库，格式: 用户名/仓库名
// =======================================================================

export default {
  async fetch(request) {
    if (request.method !== 'POST') {
      return new Response('OK', { status: 200 });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return new Response('OK', { status: 200 });
    }

    const msg = body.message || body.edited_message;
    if (!msg || !msg.text) {
      return new Response('OK', { status: 200 });
    }

    const chatId = msg.chat.id;
    const text = (msg.text || '').trim();

    // ==================== /start ====================
    if (text.startsWith('/start')) {
      await sendMessage(chatId,
        '🎓 <b>广州大学成绩监测 Bot</b>\n\n' +
        '发送 /check 触发成绩查询，结果将发送到你的邮箱。\n' +
        '发送 /help 查看帮助。'
      );
      return new Response('OK', { status: 200 });
    }

    // ==================== /check ====================
    if (text.startsWith('/check')) {
      const ok = await triggerWorkflow();
      if (ok) {
        await sendMessage(chatId,
          '✅ 查询已触发，成绩将发送到你的邮箱，稍等片刻即可查收。'
        );
      } else {
        await sendMessage(chatId,
          '❌ 触发查询失败，请稍后重试。'
        );
      }
      return new Response('OK', { status: 200 });
    }

    // ==================== /help ====================
    if (text.startsWith('/help')) {
      await sendMessage(chatId,
        '📋 <b>使用说明</b>\n\n' +
        '/check — 触发成绩查询，结果发送到邮箱\n' +
        '/start — 开始使用\n' +
        '/help — 显示本帮助'
      );
      return new Response('OK', { status: 200 });
    }

    return new Response('OK', { status: 200 });
  },
};

// ---------------------------------------------------------------------------
// 辅助函数
// ---------------------------------------------------------------------------

async function sendMessage(chatId, text) {
  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: 'HTML',
      }),
    });
  } catch {
    // 静默失败
  }
}

async function triggerWorkflow() {
  try {
    const resp = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/actions/workflows/query.yml/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GITHUB_PAT}`,
          'Accept': 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ref: 'main' }),
      }
    );
    return resp.ok || resp.status === 204;
  } catch {
    return false;
  }
}
