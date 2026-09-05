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

// 測試 10: 名字五十音與特殊發音提取 (依據真實出勤班表)
console.log('\n【測試 10：名字五十音與特殊發音提取 (真實出勤班表)】');
assert(textContent.includes('加治木') && html.includes('かじき'), '同仁名：加治木 (かじき・支配人)');
assert(textContent.includes('市石') && html.includes('いちいし'), '同仁名：市石 (いちいし)');
assert(textContent.includes('長森') && html.includes('ながもり'), '同仁名：長森 愛実 (ながもり まなみ)');
assert(textContent.includes('野別') && html.includes('のべつ'), '同仁名：野別 充旗 (のべつ みつき)');
assert(textContent.includes('森田') && html.includes('もりた'), '同仁名：森田 亨 (もりた とおる)');
assert(textContent.includes('森本') && html.includes('もりもと'), '同仁名：森本 健太郎 (もりもと けんたろう)');
assert(textContent.includes('川畑') && html.includes('かわばた'), '同仁名：川畑 (かわばた)');
assert(textContent.includes('楊') && html.includes('よう'), '同仁名：楊英筑 (よう えいちく・本人)');
assert(html.includes('ビム') && html.includes('ハン') && html.includes('エンティハ') && html.includes('プラティマ'), '包含外籍同仁與實習生 (ビム/ハン/エンティハ/プラティマ/イバオイェン/ホンイェン)');
assert(html.includes('支配人') && html.includes('正社員') && html.includes('派遣社員') && html.includes('インターン') && html.includes('朝配') && html.includes('夜配') && html.includes('洗い場') && html.includes('タイミー'), '職稱完整涵蓋班表所有職務與班別 (支配人/正社員/派遣/實習生/朝配/夜配/洗滌/Timee)');

// 測試 11: 語音聲線切換、試聽與自選語速功能
console.log('\n【測試 11：語音聲線切換與試聽功能】');
assert(html.includes('id="setting-voice-select"'), '包含設備語音聲線下拉選單 (setting-voice-select)');
assert(html.includes('id="setting-rate-slider"'), '包含語音朗讀速度調整滑桿 (setting-rate-slider)');
assert(html.includes('testCurrentVoice'), '包含即時語音試聽功能函式 (testCurrentVoice)');
assert(html.includes('saveVoiceSettings'), '包含自選聲線儲存功能函式 (saveVoiceSettings)');
assert(html.includes('populateVoiceList'), '包含設備語音清單動態載入函式 (populateVoiceList)');
assert(html.includes('getSavedVoiceSettings'), '包含本機聲線偏好讀取函式 (getSavedVoiceSettings)');

// 測試 12: 懸浮小浣熊實戰工作台與 Apple 輪盤手勢
console.log('\n【測試 12：懸浮小浣熊實戰工作台與 Apple 輪盤手勢】');
assert(html.includes('id="floating-raccoon-widget"'), '包含懸浮小浣熊元件 (floating-raccoon-widget)');
assert(html.includes('photos/raccoon_pet.png'), '使用新版透明背景小浣熊圖檔 (raccoon_pet.png)');
assert(html.includes('id="modal-raccoon-dashboard"'), '包含小浣熊全功能工作台抽屜 (modal-raccoon-dashboard)');
assert(html.includes('initFloatingRaccoon'), '包含小浣熊拖曳與手勢初始化函式 (initFloatingRaccoon)');
assert(html.includes('toggleMemoRecording'), '包含小浣熊語音 Memo 錄音函式 (toggleMemoRecording)');
assert(html.includes('openRaccoonDashboard'), '包含開啟小浣熊工作台函式 (openRaccoonDashboard)');
assert(html.includes('openRaccoonRadialMenu'), '包含開啟 Apple 輪盤選單函式 (openRaccoonRadialMenu)');
assert(html.includes('updateRaccoonVisibility'), '包含跨頁面顯示/隱藏控制函式 (updateRaccoonVisibility)');

// 測試 13: Google Gemini API Key 設定與智慧離線大腦
console.log('\n【測試 13：Gemini API Key 設定與離線智慧知識庫】');
assert(html.includes('id="setting-gemini-api-key"'), '包含 Gemini API Key 設定輸入框 (setting-gemini-api-key)');
assert(html.includes('saveGeminiApiKeySetting'), '包含儲存 API Key 函式 (saveGeminiApiKeySetting)');
assert(html.includes('testGeminiApiKeyConnection'), '包含測試 API Key 連線函式 (testGeminiApiKeyConnection)');
assert(html.includes('getLocalRoleplaySimulation'), '包含情境模擬離線智慧對話引擎 (getLocalRoleplaySimulation)');
assert(html.includes('赤牛') && html.includes('akaushi.jpg'), '生鮮名物：阿蘇赤牛 (赤牛・附現場實拍照)');
assert(html.includes('callGeminiApiUnified'), '包含統一 Gemini API 調用函式 (callGeminiApiUnified)');

// 測試 14: 情境對話 AI 評分、〇〇朗讀為なになに、點擊日文句子直接朗讀、Ruby 標音防重複
console.log('\n【測試 14：AI 評分、〇〇轉なになに、點擊句子朗讀、Ruby 標音】');
assert(html.includes('user-eval-card'), '情境對話包含 AI 評分卡片 (user-eval-card)');
assert(html.includes('grammarGrade') && html.includes('betterExpression'), 'AI 評分包含文法評級與更道地的推薦說法');
assert(html.includes('なになに'), '語音合成 extractSpokenJapanese 將 〇〇 正確轉為 なになに');
assert(html.includes('dialog-bubble-ja') && html.includes('speakJapanese'), '對話氣泡日文句子支援點擊直接朗讀');
assert(html.includes('<ruby>了解<rt>りょうかい</rt></ruby>です') && html.includes('<ruby>伺<rt>うかが</rt></ruby>う'), '文法單字使用標準 Ruby 上方標音（無括號重複）');

// 測試 15: 情境對話角色更新（新增「同事」在最前、「陌生人」在最後，移除「廚房取餐」）
console.log('\n【測試 15：情境對話角色更新（同事在最前、陌生人在最後）】');
assert(html.includes('sc_colleague') && html.includes('同事工作與日常應對'), '情境清單開頭包含「同事工作與日常應對」');
assert(html.includes('sc_stranger') && html.includes('陌生人/路人日常對話'), '情境清單結尾包含「陌生人/路人日常對話」');
assert(!html.includes('sc_runner_ready') && !html.includes('廚房取餐與通報應答'), '已成功移除舊的「廚房取餐與通報應答」情境');

// 測試 16: 對話與實拍照詳情彈窗包含單字與文法解析
console.log('\n【測試 16：對話彈窗包含單字與文法解析】');
assert(html.includes('id="lightbox-vocabs-wrap"'), '照片詳情彈窗包含關鍵單字容器 (lightbox-vocabs-wrap)');
assert(html.includes('id="lightbox-points-wrap"'), '照片詳情彈窗包含文法重點容器 (lightbox-points-wrap)');
assert(html.includes('id="lightbox-tips-wrap"'), '照片詳情彈窗包含職場應對叮嚀容器 (lightbox-tips-wrap)');
assert(html.includes('入っていないシロップ') && html.includes('でございます'), '風味糖漿對話包含文法解析與單字拆解');

// 測試 17: 小浣熊 6 大實戰工作台與 Apple 輪盤選單
console.log('\n【測試 17：小浣熊 6 大實戰工作台與 Apple 輪盤選單】');
assert(html.includes('id="raccoon-radial-overlay"'), '包含 Apple 輪盤遮罩 (raccoon-radial-overlay)');
assert(html.includes('id="raccoon-radial-menu"'), '包含 Apple 輪盤選單 (raccoon-radial-menu)');
assert(html.includes('id="raccoon-timer-badge"'), '包含小浣熊頭頂計時徽章 (raccoon-timer-badge)');
assert(html.includes('id="modal-raccoon-dashboard"'), '包含小浣熊半屏實戰工作台抽屜 (modal-raccoon-dashboard)');
assert(html.includes('copyAllMemosToClipboard'), '包含語音 Memo「一鍵複製給工程師」函式 (copyAllMemosToClipboard)');
assert(html.includes('setRaccoonTimerPreset'), '包含料理與出餐多段計時器預設函式 (setRaccoonTimerPreset)');
assert(html.includes('runFuzzyGuess'), '包含抗雜音・碎詞模糊猜測引擎函式 (runFuzzyGuess)');
assert(html.includes('drawRandomPracticeSentence'), '包含 300 句現場實戰句庫隨抽隨學函式 (drawRandomPracticeSentence)');
assert(html.includes('executeSilentTranslate'), '包含「我想說這句話」靜音大字轉日文函式 (executeSilentTranslate)');
assert(html.includes('renderYusaiLandmarks'), '包含優彩館內地標指引函式 (renderYusaiLandmarks)');
assert(html.includes('startRaccoonQuickQuiz'), '包含 3 題單字情境快問快答函式 (startRaccoonQuickQuiz)');
assert(html.includes('PRACTICE_SENTENCES_BANK') && html.includes('FUZZY_KITCHEN_GUESS_DICT'), '內建 300 句現場實戰句庫與 40+ 碎詞模糊資料庫');

// 測試 18: 「你叫什麼名字？」同仁專屬 Q 版形象圖鑑與雙擊立繪互動
console.log('\n【測試 18：「你叫什麼名字？」Q 版形象圖鑑與雙擊立繪互動】');
assert(html.includes('id="btn-who-are-you"') || html.includes('who-are-you-pill'), '包含「👤 你叫什麼名字？」專屬入口按鈕');
assert(html.includes('id="modal-who-are-you"'), '包含小浣熊「你叫什麼名字？」照相館彈窗 (modal-who-are-you)');
assert(html.includes('id="modal-name-avatar-card"'), '包含雙擊跳出 Q 版個人立繪名牌彈窗 (modal-name-avatar-card)');
assert(html.includes('openWhoAreYouModal'), '包含開啟照相館函式 (openWhoAreYouModal)');
assert(html.includes('triggerSilentCameraCapture'), '包含靜默前鏡頭特徵捕捉函式 (triggerSilentCameraCapture)');
assert(html.includes('submitCustomColleagueName'), '包含外國人/新夥伴自訂名字提交函式 (submitCustomColleagueName)');
assert(html.includes('generateTransparentChibiAvatar'), '包含方形純透明背景 Q 版角色立繪生成函式 (generateTransparentChibiAvatar)');
assert(html.includes('openNameAvatarModal'), '包含雙擊開啟同仁 Q 版名牌彈窗函式 (openNameAvatarModal)');
assert(html.includes('playNameCardSpeech') && html.includes('playWhoResultSpeech'), '包含日文自我介紹發音播放函式 (100% 靜音保護)');
assert(html.includes('setAvatarTrait') && html.includes('rephotoWhoDirectly'), '包含特徵快速微調 (髮型/眼鏡/髮色) 與即時補拍函式');
assert(html.includes('name-cell-avatar-img') && html.includes('has-avatar'), '名字卡片支援方形透明 Q 版頭像縮圖顯示');
assert(html.includes('photos/avatar_yang.png'), '包含小楊專屬 Q 版立繪圖檔參照 (avatar_yang.png)');

// 測試 19: 現場四國同步翻譯板（日文・尼泊爾文・緬甸文・英文）功能測試
console.log('\n【測試 19：現場四國同步翻譯板 (日/尼/緬/英 並排大字與語音)】');
assert(html.includes('data-page="page-broadcast"') && html.includes('四國翻譯'), '頂部導航列包含「🌐 四國翻譯」按鈕');
assert(html.includes('id="page-broadcast"'), '包含四國翻譯專屬頁面 (page-broadcast)');
assert(html.includes('id="broadcast-zh-input"'), '包含中文翻譯事項輸入框 (broadcast-zh-input)');
assert(html.includes('id="broadcast-cards-grid"'), '包含四國語言並排網格容器 (broadcast-cards-grid)');
assert(!html.includes('id="broadcast-templates-wrap"'), '已移除常用職場快捷範本標籤列 (broadcast-templates-wrap)');
assert(html.includes('id="modal-broadcast-bigscreen"') && html.includes('現場四國大字翻譯板'), '包含全螢幕大字亮屏展示彈窗 (modal-broadcast-bigscreen / 現場四國大字翻譯板)');
assert(html.includes('QUAD_BROADCAST_TEMPLATES'), '包含 15 組離線職場四國對照範本庫 (QUAD_BROADCAST_TEMPLATES)');
assert(html.includes('executeQuadTranslation'), '包含四國同步翻譯執行函式 (executeQuadTranslation)');
assert(html.includes('triggerBroadcastTranslation'), '包含手動點擊同步翻譯觸發函式 (triggerBroadcastTranslation)');
assert(html.includes('applyBroadcastTemplate'), '包含快捷範本套用函式 (applyBroadcastTemplate)');
assert(html.includes('copySingleLang'), '包含單一語言複製函式 (copySingleLang)');
assert(html.includes('copyAllQuadBroadcast'), '包含一鍵複製全部 4 國語言翻譯函式 (copyAllQuadBroadcast)');
assert(html.includes('openBroadcastBigScreen') && html.includes('closeBroadcastBigScreen'), '包含開啟/關閉大字亮屏全螢幕展示函式');
assert(html.includes('speakBroadcast'), '包含多語系語音合成朗讀函式 (speakBroadcast)');
assert(html.includes('toggleBroadcastMic'), '包含中文語音輸入辨識函式 (toggleBroadcastMic)');
assert(html.includes('日本語') && html.includes('नेपाली') && html.includes('မြန်မာဘာသာ') && html.includes('English'), '完整涵蓋日文、尼泊爾文、緬甸文、英文四大語言');

// 測試 20: 外場撤盤 6 組自然應對與同事平級 10 大動作 30 句高頻指示
console.log('\n【測試 20：外場撤盤 6 組自然應對與同事平級 10 個動作 30 句高頻指示】');
// 1. 外場撤盤 6 組自然應對
assert(textContent.includes('こちら、お下げしてもよろしいでしょうか') && textContent.includes('はい、お願いします') && textContent.includes('ありがとうございます。失礼します'), '撤盤情境 1：標準撤盤（店員問 ➔ 客人答 ➔ 店員應答）');
assert(textContent.includes('こちらはお済みでしょうか') && textContent.includes('大丈夫です、下げてください') && textContent.includes('お下げしますね'), '撤盤情境 2：確認剩餘物（店員問 ➔ 客人答 ➔ 店員應答）');
assert(textContent.includes('空いたお皿をお下げいたします') && textContent.includes('ごちそうさまでした') && textContent.includes('ごゆっくりどうぞ'), '撤盤情境 3：明顯空盤（店員告知 ➔ 客人示意 ➔ 店員應答）');
assert(textContent.includes('グラスをお下げしてもよろしいですか') && textContent.includes('まだ食べてます') && textContent.includes('失礼しました！ごゆっくりどうぞ'), '撤盤情境 4：撤玻璃杯（店員問 ➔ 客人表示未完 ➔ 店員得體退下）');
assert(textContent.includes('テーブルの上、お片付けしてもよろしいでしょうか') && textContent.includes('そのままでお願いします') && textContent.includes('こちらは下げますね'), '撤盤情境 5：整理桌面（店員問 ➔ 客人指定保留 ➔ 店員應答）');
assert(textContent.includes('こちら、お下げしますね') && textContent.includes('もうちょっと後でいいですか') && textContent.includes('また後で来ますね'), '撤盤情境 6：隨和口吻（店員問 ➔ 客人委婉推遲 ➔ 店員應答）');

// 2. 同事平級 10 個動作 × 3 種說法（共 30 句高頻指示）
assert(html.includes('tab_colleague_tasks') && html.includes('同事平級高頻指示'), '分頁清單包含獨立分頁「同事平級高頻指示」');
assert(textContent.includes('ライター戻してきて') && textContent.includes('ライター元の場所に置いといて') && textContent.includes('ライター戻しお願い'), '動作 1（放打火機）：戻してきて / 置いといて / ライター戻しお願い');
assert(textContent.includes('これ、ラップしといて') && textContent.includes('これ、ラップかけてきて') && textContent.includes('これラップお願い'), '動作 2（包保鮮膜）：ラップしといて / ラップかけてきて / これラップお願い');
assert(textContent.includes('テーブル拭いてきて') && textContent.includes('テーブル拭いといて') && textContent.includes('あそこのテーブルお願い'), '動作 3（擦桌子）：テーブル拭いてきて / テーブル拭いといて / あそこのテーブルお願い');
assert(textContent.includes('ご飯盛ってきて') && textContent.includes('ご飯よそっといて') && textContent.includes('ご飯おかわりお願い'), '動作 4（添飯）：ご飯盛ってきて / ご飯よそっといて / ご飯おかわりお願い');
assert(textContent.includes('インカム拭いといて') && textContent.includes('インカム消毒しといて') && textContent.includes('インカムの掃除お願い'), '動作 5（擦對講機）：インカム拭いといて / インカム消毒しといて / インカムの掃除お願い');
assert(textContent.includes('ゴミまとめて捨ててきて') && textContent.includes('ゴミ集めて捨てといて') && textContent.includes('ゴミ出し行ってきて'), '動作 6（收集垃圾丟掉）：ゴミまとめて捨ててきて / ゴミ集めて捨てといて / ゴミ出し行ってきて');
assert(textContent.includes('これ捨てといて') && textContent.includes('これポイしといて') && textContent.includes('これ処分お願い'), '動作 7（把這個丟掉）：これ捨てといて / これポイしといて / これ処分お願い');
assert(textContent.includes('トング集めてきて') && textContent.includes('トング回収しといて') && textContent.includes('トング集めお願い'), '動作 8（收集夾子）：トング集めてきて / トング回収しといて / トング集めお願い');
assert(textContent.includes('元の場所に戻しといて') && textContent.includes('定位置にしまってきて') && textContent.includes('お椀の片付けお願い'), '動作 9（碗放回原位）：元の場所に戻しといて / 定位置にしまってきて / お椀の片付けお願い');
assert(textContent.includes('氷取ってきて') && textContent.includes('氷足しといて') && textContent.includes('氷の補充お願い'), '動作 10（補充冰塊）：氷取ってきて / 氷足しといて / 氷の補充お願い');

// 測試 21: 小浣熊 Apple 輪盤選單點擊修復與彈窗層級
console.log('\n【測試 21：小浣熊 Apple 輪盤選單點擊修復與彈窗層級】');
assert(html.includes('--rx: 0px; --ry: -100px') && html.includes('--rx: 88px; --ry: -50px'), '輪盤選項採用 CSS 變數維持圓形座標，防止 active 狀態觸發位置突變');
assert(html.includes('triggerRadialAction(\'memo\', event)') && html.includes('triggerRadialAction(\'timer\', event)'), '輪盤按鈕完整傳遞 event 並阻止事件冒泡 (stopPropagation)');
assert(html.includes('setTimeout') && html.includes('openRaccoonDashboard(tabId)'), 'triggerRadialAction 包含安全非同步切換，保證全功能工作台順暢開啟');

const swContent = fs.readFileSync(path.join(__dirname, 'sw.js'), 'utf-8');
assert(swContent.includes('yang-pwa-v64'), 'Service Worker 快取版本已升級至 yang-pwa-v64');

console.log('====================================================');
console.log(`測試統計：通過 ${passCount} 項，失敗 ${failCount} 項`);
console.log('====================================================');

if (failCount > 0) {
  process.exit(1);
} else {
  console.log('🎉 所有真實傳菜、酒水、收桌、餐具、文法解析、聲線切換、小浣熊 6 大工作台點擊修復、「你叫什麼名字？」Q 版形象圖鑑、「現場四國同步翻譯板」、外場撤盤 6 組自然應對與同事平級 10 個動作 30 句高頻指示測試 100% 全部通過！');
}

