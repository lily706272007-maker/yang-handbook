/**
 * automated_ui_test.js
 * 驗證「楊｜優彩打工應對與會話手帳 (傳菜人員 Runner 版)」完整資料與功能測試
 */

const fs = require('fs');
const path = require('path');

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

console.log('====================================================');
console.log('執行「楊｜優彩打工應對與會話手帳 (傳菜人員 Runner 版)」自動化 UI 測試');
console.log('====================================================\n');

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

// 測試 2: 傳菜人員 SOP 流程 (依據上司官方 10 步驟手冊)
console.log('\n【測試 2：傳菜人員 (Runner) SOP 流程】');
assert(textContent.includes('厨房から「〇〇できました」と言われるので') || textContent.includes('料理ができたら'), 'SOP: 料理完成後廚房通知取餐');
assert(textContent.includes('布を必ず持って行きます'), 'SOP: 前往廚房取餐一定要帶著布巾');
assert(textContent.includes('冷蔵庫') && textContent.includes('刺身'), 'SOP: 生鮮品放入冰箱');
assert(textContent.includes('保温庫に入れます') || textContent.includes('保温庫'), 'SOP: 鍋物湯品放入保溫庫');
assert(textContent.includes('インカムで伝えます') || textContent.includes('持って来ました'), 'SOP: 送到餐廳使用無線電通報料理送達');
assert(textContent.includes('台車を元の場所に戻します'), 'SOP: 料理送達後，推車用完歸位');

// 測試 3: 現場實用對話與無線電通報 (叫菜、撤菜、等候應對)
console.log('\n【測試 3：現場實用對話與無線電通報】');
assert(textContent.includes('ご注文の方へ、〇〇をお願いします'), '向點單/廚房叫菜：ご注文の方へ、〇〇をお願いします');
assert(textContent.includes('お待ちいただきました'), '端菜給等候客人：お待ちいただきました');
assert(textContent.includes('〇〇を下げます'), '撤菜送回廚房補：〇〇を下げます');
assert(textContent.includes('取りに来てください'), '廚房通知：取りに来てください');
assert(textContent.includes('すぐ取りに伺います'), '傳菜人員應答：すぐ取りに伺います');
assert(textContent.includes('〇〇がなくなりました'), '缺菜回報：〇〇がなくなりました');
assert(textContent.includes('お通りします') || textContent.includes('失礼します'), '推車借過應對：お通りします');

// 測試 4: 上司交代事項與收桌撤盤 SOP
console.log('\n【測試 4：上司交代事項與收桌撤盤 SOP】');
assert(textContent.includes('バッシング') && textContent.includes('お下げ'), '包含收桌術語：バッシング / お下げ');
assert(textContent.includes('食事終了') || textContent.includes('お食事終了'), '包含用餐結束牌：食事終了カード');
assert(textContent.includes('お下げしてもよろしいでしょうか'), '收桌詢問：お下げしてもよろしいでしょうか？');
assert(textContent.includes('上段にお皿・お椀') && textContent.includes('中段に黒トレイ') && textContent.includes('下段に4マス仕切りプレート'), '推車收餐盤三層擺放規則：上段碗盤、中段黑餐盤、下段四格盤');
assert(textContent.includes('お皿拭き') && textContent.includes('水分をしっかり拭き取り'), '擦盤子作業：お皿拭き');
assert(textContent.includes('ドリンクコーナーの片付け'), '收拾飲料區域：ドリンクコーナーの片付け');
assert(textContent.includes('掃除機をかける'), '使用吸塵器打掃地板：掃除機をかける');

// 收桌 6 種說法
assert(textContent.includes('こちらのお皿、お下げしてもよろしいでしょうか'), '收桌①：標準萬用句');
assert(textContent.includes('空いたお皿をお下げいたしますね'), '收桌②：空盤親切句');
assert(textContent.includes('お食事はお済みでしょうか'), '收桌③：用餐完畢確認句');
assert(textContent.includes('こちらのお椀、お下げしてもよろしいでしょうか'), '收桌④：專收湯碗小缽句');
assert(textContent.includes('テーブルの上、お広くいたしますね'), '收桌⑤：騰出桌面空間句');
assert(textContent.includes('まだ召し上がりますか'), '收桌⑥：確認還在吃與得體退下句');

// 表達感謝 6 種說法
assert(textContent.includes('ありがとうございます！助かります'), '道謝①：現場靈魂萬用句');
assert(textContent.includes('お皿をまとめていただき'), '道謝②：感謝客人疊盤句');
assert(textContent.includes('ご協力ありがとうございます'), '道謝③：感謝協助配合句');
assert(textContent.includes('お気遣いいただき'), '道謝④：感謝體貼照顧句');
assert(textContent.includes('いつもありがとうございます！お疲れ様です'), '道謝⑤：對內場同事感謝句');
assert(textContent.includes('大変助かりました'), '道謝⑥：強烈感謝幫大忙句');

// 回應道謝 6 種說法
assert(textContent.includes('とんでもないです！ごゆっくりどうぞ'), '回覆①：No.1最推薦首選句');
assert(textContent.includes('こちらこそ、ありがとうございます'), '回覆②：雙向真誠感謝句');
assert(textContent.includes('恐れ入ります！ごゆっくりお過ごしください'), '回覆③：對長輩尊客敬意句');
assert(textContent.includes('喜んでいただけて嬉しいです'), '回覆④：客人稱讚開心句');
assert(textContent.includes('いえいえ！お疲れ様です'), '回覆⑤：同事夥伴默契句');
assert(textContent.includes('また何かありましたらお声がけください'), '回覆⑥：離桌隨時召喚句');

// 測試 5: 餐具與器具單字庫 (全新餐具大分類)
console.log('\n【測試 5：餐具與器具單字庫】');
assert(html.includes('"cat": "餐具"'), '單字庫包含獨立「餐具」分類');
assert(textContent.includes('醤油皿'), '餐具：醬油皿 (醤油皿)');
assert(textContent.includes('小トング'), '餐具：小夾子 (小トング)');
assert(textContent.includes('サービススプーン'), '餐具：大湯匙/公勺 (サービススプーン)');
assert(textContent.includes('ティースプーン'), '餐具：小湯匙 (ティースプーン)');
assert(textContent.includes('お皿'), '餐具：盤子 (お皿)');
assert(textContent.includes('お椀'), '餐具：碗 (お椀)');
assert(textContent.includes('黒トレイ') || textContent.includes('お盆'), '餐具：黑托盤 (黒トレイ/お盆)');
assert(textContent.includes('4マス仕切りプレート') || textContent.includes('仕切り皿'), '餐具：四格餐盤 (4マス仕切りプレート)');
assert(textContent.includes('お箸') && textContent.includes('割り箸'), '餐具：筷子/免洗筷 (お箸/割り箸)');
assert(textContent.includes('グラス') || textContent.includes('コップ'), '餐具：水杯/玻璃杯 (グラス/コップ)');
assert(textContent.includes('ダスター'), '餐具/工具：專用抹布 (ダスター)');
assert(textContent.includes('爪楊枝'), '餐具：牙籤 (爪楊枝)');
assert(textContent.includes('フォーク'), '餐具：叉子 (フォーク)');
assert(textContent.includes('ライター') || textContent.includes('チャッカマン'), '工具：打火機/點火器 (ライター/チャッカマン)');
assert(!html.includes('卓上コンロ'), '已成功移除「桌上型卡式瓦斯爐」');

// 測試 6: 必須記住的料理名稱與分類 (已核對紙本菜單並剔除停供菜餚)
console.log('\n【測試 6：料理名稱核對與剔除停供品項】');
assert(html.includes('肉燒賣') && html.includes('肉焼売'), '熱菜：肉燒賣 (肉焼売)');
assert(html.includes('馬刺') && html.includes('basashi.jpg'), '生鮮名物：生馬肉片 (馬刺し・附現場實拍照)');
assert(html.includes('鰹魚生魚片') || html.includes('鰹のたたき'), '生魚片名物：鰹魚生魚片 (鰹のたたき)');
assert(html.includes('南蠻炸雞'), '熱菜：南蠻炸雞');
assert(html.includes('高湯煎蛋捲'), '朝食熱菜：高湯煎蛋捲');
assert(html.includes('甜辛彩蔬煮'), '熱食燉煮：甜辛彩蔬煮');
assert(html.includes('麻婆豆腐'), '熱食：麻婆豆腐');
assert(html.includes('日式牛肉咖哩'), '主食：日式牛肉咖哩');
assert(html.includes('蛤蜊味噌湯'), '熱湯：蛤蜊味噌湯');
assert(html.includes('阿蘇高菜拌飯'), '主食：阿蘇高菜拌飯');
assert(html.includes('熊本龍膽豬涮涮鍋') || html.includes('りんどうポーク'), '名物鍋物：熊本龍膽豬涮涮鍋');
assert(html.includes('豚骨拉麵'), '主食：豚骨拉麵');
assert(html.includes('玉子燒壽司') && html.includes('鮪魚壽司') && html.includes('鮭魚壽司'), '壽司：玉子、鮪魚、鮭魚');
assert(html.includes('鰻魚壽司') && html.includes('烏賊壽司') && html.includes('鮮蝦壽司') && html.includes('照燒壽司'), '壽司：鰻魚、烏賊、鮮蝦、照燒');
assert(html.includes('哈密瓜') && html.includes('巧克力蛋糕') && html.includes('和菓子丸子'), '水果甜點：哈密瓜、巧克力蛋糕、和菓子');

// 測試 7: 酒水飲品、水之型態與機台操作說明 (店內全面統稱「炭酸」)
console.log('\n【測試 7：酒水飲品、水的型態與機台操作說明 (碳酸)】');
assert(textContent.includes('王様の涙') && textContent.includes('赤ワイン') && textContent.includes('白ワイン'), '紅酒白酒：王様の涙 赤・白ワイン');
assert(textContent.includes('れいざん') && textContent.includes('純米酒'), '阿蘇名酒：れいざん 純米酒');
assert(textContent.includes('オールフリー') && textContent.includes('ノンアルコールビール'), '無酒精啤酒：Suntory ALL-FREE');
assert(textContent.includes('黄色いボタンを１回押すと') && textContent.includes('自動で注がれます'), '生啤酒機操作：按一次黃色按鈕自動注酒');
assert(textContent.includes('アルコールの入っていないシロップ'), '糖漿說明：這是無酒精的風味糖漿');
assert(textContent.includes('炭酸') && html.includes('碳酸'), '已全面改用「炭酸」（無蘇打水字眼）');
assert(textContent.includes('お冷') || textContent.includes('冷水'), '水的型態：冰水/冷水 (お冷/冷水)');
assert(textContent.includes('白湯') || textContent.includes('常温'), '水的型態：溫開水/常溫水 (白湯/常温)');
assert(textContent.includes('お湯') || textContent.includes('熱湯'), '水的型態：熱水/熱開水 (お湯/熱湯)');
assert(textContent.includes('沸騰'), '水的型態：滾水/剛煮開的水 (沸騰したお湯)');

// 測試 8: 單字七大核心分類 (餐具、工具、餐點、酒水、名字、職稱、對話)
console.log('\n【測試 8：單字分類完整性】');
assert(html.includes('"cat": "餐具"'), '單字庫包含「餐具」分類');
assert(html.includes('"cat": "餐點"'), '單字庫包含「餐點」分類');
assert(html.includes('"cat": "酒水"'), '單字庫包含「酒水」分類');
assert(html.includes('"cat": "工具"'), '單字庫包含「工具」分類');
assert(html.includes('"cat": "名字"'), '單字庫包含「名字」分類 (純人名)');
assert(html.includes('"cat": "職稱"'), '單字庫包含「職稱」分類 (純職稱)');
assert(html.includes('"cat": "對話"'), '單字庫包含「對話」分類');

// 測試 9: 文法解析彈窗 (modal-sop-grammar) 與互動功能
console.log('\n【測試 9：文法解析彈窗與 CRUD 功能】');
assert(html.includes('id="modal-sop-grammar"'), '包含 SOP/對話 文法解析彈窗 (modal-sop-grammar)');
assert(html.includes('openItemGrammarModal'), '包含開啟文法解析函式 (openItemGrammarModal)');
assert(html.includes('openModalItem'), '包含開啟條目編輯函式 (openModalItem)');
assert(html.includes('submitItemForm'), '包含儲存條目函式 (submitItemForm)');
assert(html.includes('deleteSopItem'), '包含刪除條目函式 (deleteSopItem)');

// 測試 10: 名字五十音與特殊發音提取
console.log('\n【測試 10：名字五十音與特殊發音提取】');
assert(textContent.includes('市石') && html.includes('いちいし'), '同仁名：市石 (いちいし)');
assert(textContent.includes('松本') && html.includes('まつもと'), '同仁名：松本 (まつもと)');
assert(textContent.includes('楊') && html.includes('よう'), '同仁名：楊 (よう)');

// 測試 11: 語音聲線切換、試聽與自選語速功能
console.log('\n【測試 11：語音聲線切換與試聽功能】');
assert(html.includes('id="setting-voice-select"'), '包含設備語音聲線下拉選單 (setting-voice-select)');
assert(html.includes('id="setting-rate-slider"'), '包含語音朗讀速度調整滑桿 (setting-rate-slider)');
assert(html.includes('testCurrentVoice'), '包含即時語音試聽功能函式 (testCurrentVoice)');
assert(html.includes('saveVoiceSettings'), '包含自選聲線儲存功能函式 (saveVoiceSettings)');
assert(html.includes('populateVoiceList'), '包含設備語音清單動態載入函式 (populateVoiceList)');
assert(html.includes('getSavedVoiceSettings'), '包含本機聲線偏好讀取函式 (getSavedVoiceSettings)');

// 測試 12: 懸浮小浣熊 AI 助手 (透明背景、可拖曳、語音輸入、全網頁修訂)
console.log('\n【測試 12：懸浮小浣熊 AI 助手】');
assert(html.includes('id="floating-raccoon-widget"'), '包含懸浮小浣熊元件 (floating-raccoon-widget)');
assert(html.includes('photos/raccoon_pet.png'), '使用新版透明背景小浣熊圖檔 (raccoon_pet.png)');
assert(html.includes('id="modal-raccoon-chat"'), '包含小浣熊雙擊對話視窗 (modal-raccoon-chat)');
assert(html.includes('initFloatingRaccoon'), '包含小浣熊拖曳與手勢初始化函式 (initFloatingRaccoon)');
assert(html.includes('startRaccoonVoice'), '包含小浣熊語音輸入函式 (startRaccoonVoice)');
assert(html.includes('openRaccoonChatModal'), '包含雙擊開啟對話窗函式 (openRaccoonChatModal)');
assert(html.includes('updateRaccoonVisibility'), '包含跨頁面顯示/隱藏控制函式 (updateRaccoonVisibility)');
assert(html.includes('executeRaccoonAction'), '包含小浣熊全網頁資料修訂執行函式 (executeRaccoonAction)');

// 測試 13: Google Gemini API Key 設定與智慧離線大腦
console.log('\n【測試 13：Gemini API Key 設定與離線智慧知識庫】');
assert(html.includes('id="setting-gemini-api-key"'), '包含 Gemini API Key 設定輸入框 (setting-gemini-api-key)');
assert(html.includes('saveGeminiApiKeySetting'), '包含儲存 API Key 函式 (saveGeminiApiKeySetting)');
assert(html.includes('testGeminiApiKeyConnection'), '包含測試 API Key 連線函式 (testGeminiApiKeyConnection)');
assert(html.includes('getLocalRaccoonKnowledgeReply'), '包含小浣熊離線智慧知識庫函式 (getLocalRaccoonKnowledgeReply)');
assert(html.includes('getLocalRoleplaySimulation'), '包含情境模擬離線智慧對話引擎 (getLocalRoleplaySimulation)');
assert(html.includes('callGeminiApiUnified'), '包含統一 Gemini API 調用函式 (callGeminiApiUnified)');

console.log('====================================================');
console.log(`測試統計：通過 ${passCount} 項，失敗 ${failCount} 項`);
console.log('====================================================');

if (failCount > 0) {
  process.exit(1);
} else {
  console.log('🎉 所有真實傳菜、酒水、收桌、餐具、文法解析、聲線切換、小浣熊AI與API設定測試 100% 全部通過！');
}
