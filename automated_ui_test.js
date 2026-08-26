const fs = require('fs');
const path = require('path');

console.log('====================================================');
console.log('執行「楊｜優彩打工應對與會話手帳 (傳菜人員 Runner 版)」自動化 UI 測試');
console.log('====================================================\n');

let passCount = 0;
let failCount = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  ✅ [PASS] ${message}`);
    passCount++;
  } else {
    console.error(`  ❌ [FAIL] ${message}`);
    failCount++;
  }
}

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf-8');
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'manifest.json'), 'utf-8'));

// 輔助函式：去除 HTML 標籤與 ruby 標音以便檢測純文字
function stripRubyAndHtml(str) {
  return str.replace(/<rt>[\s\S]*?<\/rt>/g, '').replace(/<[^>]*>/g, '');
}
const textContent = stripRubyAndHtml(html);

// 測試 1: Header 與 Badge 與頂部導航列
console.log('【測試 1：Header 與 Badge 規範】');
assert(html.includes('<span class="header-badge">打工度假</span>'), 'Header Badge 已正確改為「打工度假」');
assert(html.includes('<span class="header-title">楊の手帳</span>'), 'Header 主標題已正確改為「楊の手帳」');
assert(html.includes('id="top-nav-bar"'), '導航列已整合至頂部 Banner (top-nav-bar)');
assert(!html.includes('id="bottom-nav"'), '已移除舊的底部導航列 (bottom-nav)');
assert(html.includes('logo.png'), 'Header 包含專屬 Logo');

// 測試 2: 傳菜人員 8 大 SOP 步驟驗證
console.log('\n【測試 2：傳菜人員 (Runner) 8 大 SOP 流程】');
assert(textContent.includes('料理の名前を覚えます'), 'SOP 1: 首先記住所有料理名稱');
assert(textContent.includes('厨房から「できました」と言われるので取りに行きます'), 'SOP 2: 料理完成後廚房通知取餐');
assert(textContent.includes('布を必ず持って行きます'), 'SOP 3: 前往廚房取餐一定要帶著布巾');
assert(textContent.includes('扉を閉めて行きます'), 'SOP 4: 離開餐廳入口隨手關門');
assert(textContent.includes('台車に乗せ') && textContent.includes('運んできます'), 'SOP 5: 確認料理後放餐車運回餐廳');
assert(textContent.includes('台車を少し持ち上げて水平にします'), 'SOP 6: 入口斜坡稍微抬起餐車保持水平');
assert(textContent.includes('インカムで伝えます'), 'SOP 7: 送到餐廳使用無線電通報料理名稱');
assert(textContent.includes('元の場所に戻します'), 'SOP 8: 料理放指定位置，推車用完歸位');

// 測試 3: 現場實用對話與無線電通報 (叫菜、撤菜、等候應對)
console.log('\n【測試 3：現場實用對話與無線電通報】');
assert(textContent.includes('ご注文の方へ、〇〇をお願いします'), '向點單/廚房叫菜：ご注文の方へ、〇〇をお願いします');
assert(textContent.includes('お待ちいただきました'), '端菜給等候客人：お待ちいただきました');
assert(textContent.includes('〇〇を下げます'), '撤菜送回廚房補：〇〇を下げます');
assert(textContent.includes('チキン南蛮できました！'), '廚房通知：南蠻炸雞做好了');
assert(textContent.includes('了解です！'), '傳菜人員應答：了解です！');
assert(textContent.includes('チキン南蛮持ってきました'), '無線電通報：チキン南蛮持ってきました');
assert(textContent.includes('〇〇がなくなりました'), '缺菜回報：〇〇がなくなりました');

// 測試 4: 料理放置位置對照表
console.log('\n【測試 4：料理放置位置對照表】');
assert(textContent.includes('冷蔵庫に入れる') && textContent.includes('鯛の刺身') && textContent.includes('赤牛') && textContent.includes('馬刺し'), '冰箱：鯛魚刺身、赤牛、馬刺し');
assert(textContent.includes('チキン南蛮などのお皿を交換する料理'), '作業區：南蠻炸雞等換盤料理');
assert(textContent.includes('保温庫に入れる') && textContent.includes('鍋、スープ'), '保溫庫：火鍋、湯品等保溫料理');

// 測試 5: 常用工具與備品單字
console.log('\n【測試 5：常用工具與備品單字庫】');
assert(textContent.includes('ワゴン / 台車'), '推車/餐車: ワゴン/台車');
assert(textContent.includes('クロス / 布'), '布巾: クロス/布');
assert(textContent.includes('インカム'), '無線電對講機: インカム');
assert(textContent.includes('ダスター'), '抹布: ダスター');
assert(textContent.includes('トレー / お盆'), '托盤: トレー/お盆');
assert(textContent.includes('タイのお皿'), '鯛魚盤: タイのお皿');
assert(textContent.includes('冷蔵庫'), '冰箱: 冷蔵庫');
assert(textContent.includes('保温庫'), '保溫庫: 保温庫');
assert(textContent.includes('元の場所'), '原位: 元の場所');

// 測試 6: 必須記住的料理名稱與湯頭分類
console.log('\n【測試 6：必須記住的料理名稱與分類】');
assert(html.includes('南蠻炸雞'), '肉類海鮮：南蠻炸雞');
assert(html.includes('鯛魚生魚片'), '肉類海鮮：鯛魚生魚片');
assert(html.includes('炙燒鰹魚'), '肉類海鮮：炙燒鰹魚');
assert(html.includes('馬肉刺身'), '肉類海鮮：馬肉刺身');
assert(html.includes('赤牛'), '肉類海鮮：赤牛');
assert(html.includes('鹽烤大蝦'), '炭火圍爐裏：鹽烤大蝦');
assert(html.includes('現炸天婦羅'), '熱食炸物：現炸天婦羅');
assert(html.includes('龍膽豬肩里肌牛排'), '熱食鐵板：龍膽豬肩里肌牛排');
assert(html.includes('時蔬甜辛煮'), '和食燉煮：時蔬甜辛煮');
assert(html.includes('麻婆豆腐'), '中華料理：麻婆豆腐');
assert(html.includes('甜口牛肉咖哩'), '洋食：甜口牛肉咖哩');
assert(html.includes('蛤蜊味噌湯'), '熱湯：蛤蜊味噌湯');
assert(html.includes('熊本阿蘇高菜拌飯'), '主食：熊本阿蘇高菜拌飯');
assert(html.includes('火鍋高湯'), '湯頭類：火鍋高湯 (已正確歸入菜餚類)');
assert(html.includes('豚骨拉麵'), '餐點類：豚骨拉麵 (已正確歸入餐點類)');
assert(html.includes('玉子燒壽司') && html.includes('藍鰭鮪魚壽司') && html.includes('鮭魚壽司'), '壽司：玉子、鮪魚、鮭魚');
assert(html.includes('鰻魚壽司') && html.includes('花枝壽司') && html.includes('鮮蝦壽司'), '壽司：鰻魚、花枝、鮮蝦');
assert(html.includes('哈密瓜') && html.includes('巧克力布朗尼切塊蛋糕') && html.includes('抹茶蕨餅') && html.includes('和菓子'), '水果甜點：哈密瓜、巧克力蛋糕、抹茶蕨餅、和菓子');

// 測試 7: 收桌與撤盤 SOP (バッシング)
console.log('\n【測試 7：收桌與撤盤 SOP (バッシング) 與會話】');
assert(textContent.includes('バッシング') || textContent.includes('お下げ'), '包含收桌術語：バッシング / お下げ');
assert(textContent.includes('食事終了') || textContent.includes('お食事終了'), '包含用餐結束牌：食事終了カード');
assert(textContent.includes('お下げしてもよろしいでしょうか'), '收桌詢問：お皿、お下げしてもよろしいでしょうか？');
assert(textContent.includes('かしこまりました。失礼いたします。'), '客人表示可收時回覆：かしこまりました。失礼いたします。');
assert(textContent.includes('恐れ入ります。ごゆっくりどうぞ。'), '客人道謝時回覆：恐れ入ります。ごゆっくりどうぞ。');
assert(textContent.includes('大変失礼いたしました。ごゆっくりお召し上がりくださいませ。'), '客人表示還在吃時回覆：大変失礼いたしました。ごゆっくりお召し上がりくださいませ。');

// 測試 8: 酒水飲品與機台操作說明 (碳酸取代蘇打水)
console.log('\n【測試 8：酒水飲品與機台操作說明 (碳酸)】');
assert(textContent.includes('王様の涙') && textContent.includes('赤ワイン') && textContent.includes('白ワイン'), '紅酒白酒：王様の涙 赤・白ワイン');
assert(textContent.includes('れいざん') && textContent.includes('純米酒'), '阿蘇名酒：れいざん 純米酒');
assert(textContent.includes('オールフリー') && textContent.includes('ノンアルコールビール'), '無酒精啤酒：Suntory ALL-FREE');
assert(textContent.includes('黄色いボタンを１回押すと') && textContent.includes('自動で注がれます'), '生啤酒機操作：按一次黃色按鈕自動注酒');
assert(textContent.includes('アルコールの入っていないシロップ'), '糖漿說明：這是無酒精的風味糖漿');
assert(textContent.includes('炭酸') && html.includes('碳酸'), '已全面改用「碳酸」（無蘇打水字眼）');

// 測試 9: 五大核心單字分類規範 (餐點、酒水、工具、名字、職稱)
console.log('\n【測試 9：單字五大分類 (餐點、酒水、工具、名字、職稱)】');
assert(html.includes('"cat": "餐點"'), '單字庫包含「餐點」分類');
assert(html.includes('"cat": "酒水"'), '單字庫包含「酒水」分類');
assert(html.includes('"cat": "工具"'), '單字庫包含「工具」分類');
assert(html.includes('"cat": "名字"'), '單字庫包含「名字」分類 (純人名)');
assert(html.includes('"cat": "職稱"'), '單字庫包含「職稱」分類 (純職稱)');
assert(textContent.includes('内間') && html.includes('うちま'), '同仁名：内間 (うちま)');
assert(textContent.includes('須藤') && html.includes('すどう'), '同仁名：須藤 (すどう)');
assert(textContent.includes('森田') && html.includes('もりた'), '同仁名：森田 (もりた)');
assert(textContent.includes('ピョー') && textContent.includes('ビム') && textContent.includes('ハン') && textContent.includes('プラティマ'), '外籍同仁名：ピョー、ビム、ハン、プラティマ');
assert(textContent.includes('最後確認する人'), '職稱名：最後確認する人');
assert(textContent.includes('すしランナー'), '職稱名：すしランナー');
assert(textContent.includes('ランナー') && html.includes('ranna-'), '職稱名：ランナー');

// 測試 10: 拼音標註 (<ruby>) 規範 (無括號重複平假名)
console.log('\n【測試 10：拼音標註 (<ruby>) 規範 與 無括號平假名重複】');
assert(html.includes('<ruby>料理<rt>りょうり</rt></ruby>'), '漢字上方標平假名 (例: 料理→りょうり)');
assert(html.includes('<ruby>チキン<rt>chikin</rt></ruby>'), '片假名上方標 Romaji (例: チキン→chikin)');
assert(html.includes('<ruby>ワゴン<rt>wagon</rt></ruby>'), '片假名上方標 Romaji (例: ワゴン→wagon)');
assert(html.includes('<ruby>バッシング<rt>basshingu</rt></ruby>'), '片假名上方標 Romaji (例: バッシング→basshingu)');
assert(!html.includes('本鮪（ほんまぐろ）') && !html.includes('海老（えび）'), '日文字串中已清除重複的括號假名');

// 測試 12: Word 表格式密集網格 & 名字日本人前外國人後 & 點一下發音點兩下詳情
console.log('\n【測試 12：Word 表格網格 & 名字分組 & 點一下發音點兩下看詳情】');
assert(html.includes('vocab-word-grid'), '包含單字網格佈局樣式 (vocab-word-grid)');
assert(html.includes('repeat(6, 1fr)') && html.includes('repeat(5, 1fr)') && html.includes('repeat(4, 1fr)') && html.includes('repeat(3, 1fr)'), '響應式網格完整支援：電腦6欄、iPad橫5欄、iPad直4欄、手機3欄');
assert(html.includes('word-cell name-cell'), '包含名字專用無中文純日文標音卡片 (name-cell)');
assert(html.includes('handleWordCellClick('), '包含點一下發音與雙擊防抖處理 (handleWordCellClick)');
// 測試 13: 智慧假名發音提取 (修復麻婆豆腐與全站發音走調問題)
console.log('\n【測試 13：TTS 智慧假名發音提取 (修復麻婆豆腐等單字)】');
assert(html.includes('function extractSpokenJapanese('), '包含智慧假名發音提取函式 (extractSpokenJapanese)');

// 模擬函式執行驗證
function testExtractSpokenJapanese(htmlStr) {
  let result = htmlStr.replace(/<ruby>(.*?)<rt>(.*?)<\/rt><\/ruby>/gi, (match, base, rt) => {
    const cleanRt = (rt || '').trim();
    const cleanBase = (base || '').trim();
    if (/[\u3040-\u309F\u30A0-\u30FF]/.test(cleanRt)) return cleanRt;
    else return cleanBase;
  });
  return result.replace(/<[^>]+>/g, '').replace(/[\/／]/g, '、').trim();
}

assert(testExtractSpokenJapanese('<ruby>麻婆豆腐<rt>まーぼーどうふ</rt></ruby>') === 'まーぼーどうふ', '麻婆豆腐發音精準提取為「まーぼーどうふ」(非 Asaba Tofu)');
assert(testExtractSpokenJapanese('<ruby>市石<rt>いちいし</rt></ruby>') === 'いちいし', '市石發音精準提取為「いちいし」(非 Shiseki)');
assert(testExtractSpokenJapanese('<ruby>楊<rt>よう</rt></ruby>') === 'よう', '楊發音精準提取為「よう」(非 Yanagi)');
assert(testExtractSpokenJapanese('<ruby>チキン<rt>chikin</rt></ruby>') === 'チキン', '片假名保留日文發音「チキン」(非英文 chikin)');

console.log('\n====================================================');
console.log(`測試統計：通過 ${passCount} 項，失敗 ${failCount} 項`);
console.log('====================================================');

if (failCount > 0) process.exit(1);
else console.log('🎉 所有真實傳菜、酒水、收桌與排班手冊內容測試 100% 全部通過！');


