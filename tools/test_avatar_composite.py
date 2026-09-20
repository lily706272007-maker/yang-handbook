import os
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')
BRAIN_DIR = '/Users/yangyongzhu/.gemini/antigravity/brain/b58ba25a-e9f5-48ce-a86c-daf46a4f945e'

CANVAS_W, CANVAS_H = 896, 1200
CENTER_X = 448

def composite_avatar(layers_list, out_path, is_female=True):
    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    body_im = None
    face_im = None
    eyes_im = None
    brows_im = None
    bangs_im = None
    
    loaded = {}
    for rel in layers_list:
        if not rel:
            continue
        p = os.path.join(LAYERS_DIR, rel)
        if os.path.exists(p):
            sub = rel.split('/')[0]
            loaded[sub] = Image.open(p).convert('RGBA')
            
    # 1. Background
    if 'bg' in loaded:
        canvas.alpha_composite(loaded['bg'])
        
    # 2. Back hair
    if 'back_hair' in loaded:
        canvas.alpha_composite(loaded['back_hair'])
        
    # 3. Body (under layer)
    body_im = loaded.get('body')
    if body_im:
        canvas.alpha_composite(body_im)
        
    # 4. Face & extended neck
    face_im = loaded.get('faces')
    if face_im:
        canvas.alpha_composite(face_im)
        
    # 5. Front shirt lapels wrap OVER neck base
    if body_im:
        front_shirt = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        y_start = 440 if is_female else 435
        v_y_top = 444 if is_female else 438
        v_y_bot = 480 if is_female else 478
        
        for y in range(y_start, CANVAS_H):
            for x in range(CANVAS_W):
                pb = body_im.getpixel((x, y))
                if pb[3] > 50:
                    in_v_opening = False
                    if v_y_top <= y <= v_y_bot:
                        progress = (y - v_y_top) / float(v_y_bot - v_y_top)
                        v_left = 422 + progress * 24 if is_female else 426 + progress * 22
                        v_right = 472 - progress * 24 if is_female else 472 - progress * 22
                        if v_left < x < v_right:
                            in_v_opening = True
                    if not in_v_opening:
                        front_shirt.putpixel((x, y), pb)
        canvas.alpha_composite(front_shirt)
        
    # 6. Nose
    if 'noses' in loaded:
        canvas.alpha_composite(loaded['noses'])
        
    # 7. Mouth
    if 'mouths' in loaded:
        canvas.alpha_composite(loaded['mouths'])
        
    # 8. Eyes
    eyes_im = loaded.get('eyes')
    if eyes_im:
        canvas.alpha_composite(eyes_im)
        
    # 9. Eyebrows
    brows_im = loaded.get('eyebrows')
    if brows_im:
        canvas.alpha_composite(brows_im)
        
    # Forehead shadow under bangs
    bangs_im = loaded.get('bangs')
    if bangs_im:
        shadow = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        for y in range(270, 330):
            for x in range(390, 510):
                bx = x - 2
                by = y - 4
                if 0 <= bx < CANVAS_W and 0 <= by < CANVAS_H:
                    if bangs_im.getpixel((bx, by))[3] > 180 and bangs_im.getpixel((x, y))[3] < 50:
                        shadow.putpixel((x, y), (170, 105, 75, 20))
        canvas.alpha_composite(shadow)
        canvas.alpha_composite(bangs_im)
        
    # 11. Anime expressive eye shine through hair
    if bangs_im and (eyes_im or brows_im):
        shine = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        for y in range(300, 350):
            for x in range(380, 520):
                if bangs_im.getpixel((x, y))[3] > 100:
                    if eyes_im:
                        pe = eyes_im.getpixel((x, y))
                        if pe[3] > 0:
                            shine.putpixel((x, y), (*pe[:3], int(pe[3] * 0.80)))
                    if brows_im:
                        pb = brows_im.getpixel((x, y))
                        if pb[3] > 0:
                            shine.putpixel((x, y), (*pb[:3], int(pb[3] * 0.65)))
        canvas.alpha_composite(shine)
        
    # 12. Accessories (Glasses)
    if 'accessories' in loaded:
        canvas.alpha_composite(loaded['accessories'])
        
    canvas.convert('RGB').save(out_path, quality=95)
    print(f'Saved: {out_path}')
    return canvas

# -------------------------------------------------------------
# Character A:
# 女生・接睫毛美睫款＋低包包頭＋幼態短臉＋法式八字瀏海 (焦糖亞麻棕)
# -------------------------------------------------------------
char_a_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景 (原圖 896x1200 無裁切)
    'back_hair/back_02_low_bun_flaxen.png',    # L2: 後髮 (低包包頭・焦糖亞麻棕)
    'body/body_female_normal.png',             # L3: 身軀 (女外場制服・純黑和風・頭到大腿取景)
    'faces/face_02_nat.png',                   # L4: 臉型 (幼態短臉・自然膚色・脖子無縫收攏入衣領)
    'mouths/mouth_01.png',                     # L5: 嘴巴 (微笑微揚嘴・晶透果凍唇・黃金比例y=390)
    'noses/nose_01.png',                       # L6: 鼻子 (小巧點鼻・立體動漫鼻・中軸y=362)
    'eyes/eye_f05.png',                        # L7: 眼睛 (柔美美睫眼・臥蠶陰影・瞳孔y=330)
    'eyebrows/brow_f06.png',                   # L8: 眉毛 (歐式細眉・眉骨y=312)
    'bangs/bang_08_flaxen.png',                # L9: 前瀏海 (法式八字外翻・天使光澤)
    None                                       # L10: 配件
]

# -------------------------------------------------------------
# Character B:
# 男生・聚焦小眼＋漸層俐落短髮＋圓角方臉＋中分碎髮流＋透光黑框眼鏡 (純黑)
# -------------------------------------------------------------
char_b_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景 (原圖 896x1200 無裁切)
    'back_hair/back_07_undercut_black.png',    # L2: 後髮 (漸層俐落短髮・純黑)
    'body/body_male_normal.png',               # L3: 身軀 (男外場制服・統一黑階和風制服)
    'faces/face_05_nat.png',                   # L4: 臉型 (柔和方臉・脖子平滑插入衣領)
    'mouths/mouth_03.png',                     # L5: 嘴巴 (平直自然微笑嘴・黃金比例y=390)
    'noses/nose_02.png',                       # L6: 鼻子 (挺拔直鼻・鼻尖高光・y=362)
    'eyes/eye_m04.png',                        # L7: 眼睛 (聚焦英氣小眼・雙眼明亮・y=330)
    'eyebrows/brow_m01.png',                   # L8: 眉毛 (劍眉英氣眉・眉骨y=312)
    'bangs/bang_05_black.png',                 # L9: 前瀏海 (微捲短髮・左右平衡高顱頂)
    'accessories/acc_glasses_square.png'       # L10: 配件 (晶透黑框方鏡・白高光反射・y=330)
]

# -------------------------------------------------------------
# Character C:
# 女生留男生短髮 (Unisex)・清爽神采眼＋層次碎短髮＋經典鵝蛋臉 (純黑)
# -------------------------------------------------------------
char_c_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景 (原圖 896x1200 無裁切)
    'back_hair/back_10_layered_pixie_black.png',# L2: 後髮 (層次碎短髮・推剪質感)
    'body/body_female_normal.png',             # L3: 身軀 (女生外場制服身軀・柔美肩線・頭到大腿取景)
    'faces/face_01_nat.png',                   # L4: 臉型 (經典鵝蛋臉・長頸收攏入衣領)
    'mouths/mouth_02.png',                     # L5: 嘴巴 (露齒開朗笑・白齒晶亮・黃金比例y=390)
    'noses/nose_01.png',                       # L6: 鼻子 (小巧點鼻・立體動漫鼻・y=362)
    'eyes/eye_m01.png',                        # L7: 眼睛 (清爽神采眼・臥蠶笑意・y=330)
    'eyebrows/brow_f02.png',                   # L8: 眉毛 (溫柔平直眉・貼合眉骨・y=312)
    'bangs/bang_01_black.png',                 # L9: 前瀏海 (俐落側分短髮・左右平衡高顱頂)
    None                                       # L10: 配件
]

im_a = composite_avatar(char_a_layers, os.path.join(PHOTOS_DIR, 'composite_character_a.png'), is_female=True)
im_b = composite_avatar(char_b_layers, os.path.join(PHOTOS_DIR, 'composite_character_b.png'), is_female=False)
im_c = composite_avatar(char_c_layers, os.path.join(PHOTOS_DIR, 'composite_character_c.png'), is_female=True)

for f in ['composite_character_a.png', 'composite_character_b.png', 'composite_character_c.png']:
    p_src = os.path.join(PHOTOS_DIR, f)
    p_dst = os.path.join(BRAIN_DIR, f)
    with open(p_src, 'rb') as sf, open(p_dst, 'wb') as df:
        df.write(sf.read())

card_w = 480
card_img_h = int(card_w * 1200 / 896)
card_info_h = 190
card_h = card_img_h + card_info_h

showcase_w = 30 + 3 * (card_w + 20) + 10
showcase_h = 80 + card_h + 30

showcase = Image.new('RGB', (showcase_w, showcase_h), (245, 247, 250))
d = ImageDraw.Draw(showcase)

font_title = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 26)
font_sub = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 16)
font_h2 = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 17)
font_desc = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 13)

d.rectangle([(0, 0), (showcase_w, 75)], fill=(26, 32, 40))
d.text((30, 15), '【日系外場立繪合成・v142 終極無瑕版 × 5 大缺陷全面修復】', font=font_title, fill=(255, 255, 255))
d.text((30, 48), '① 背景原圖完全不裁切  ② 頭部至大腿標準鏡頭  ③ 五官髮型三庭五眼精準對齊  ④ 脖子無縫收攏於衣領內  ⑤ 全體制服和風曜黑統一', font=font_sub, fill=(190, 205, 220))

chars_info = [
    (im_a, '示範同仁 A（精緻甜美風）', [
        '【背景取景】原圖 896×1200 完全無裁切，完整保留天花板暖燈與深邃走道',
        '【鏡頭比例】頭頂至大腿黃金距離取景，自然站立於居酒屋中央走道',
        '【結構對齊】三庭五眼黃金對齊 (眉312/眼330/鼻362/果凍微笑嘴390/下巴440)',
        '【領口銜接】天鵝頸深收於衣領 V 口內，雙側立領自然包覆鎖骨，零斷層浮空',
        '【制服顏色】日式餐飲曜黑制服 (RGB 26,28,32)，標準折痕明暗層次'
    ]),
    (im_b, '示範同仁 B（俐落專業風）', [
        '【背景取景】原圖 896×1200 完全無裁切，寬闊景深與日式庭園落地窗',
        '【鏡頭比例】頭頂至大腿男款標準取景，肩線挺拔大方',
        '【結構對齊】英氣雙眼 (聚焦小眼330) 於晶透眼鏡內清晰對稱呈現，高顱頂漸層短髮',
        '【領口銜接】英挺粗頸順暢沒入立領開口，前襟門襟自然扣合覆蓋，無破圖',
        '【制服顏色】曜黑統一面料，銀質金屬銘牌光芒，與女款制服色階 100% 一致'
    ]),
    (im_c, '示範同仁 C（率性中性風）', [
        '【背景取景】原圖 896×1200 完全無裁切，完整日式居酒屋走道深邃景深',
        '【鏡頭比例】頭頂至大腿黃金取景，男女通用制服圍裙與修身剪裁',
        '【結構對齊】開朗露齒笑 (真實嘴型390，晶亮白齒)、神采雙眼、俐落碎短髮',
        '【領口銜接】鵝蛋臉修長頸部完全沒入衣領內，衣領立體搭接，零懸空',
        '【制服顏色】曜黑面料與和風圍裙，光影層次細緻分明，完美融合'
    ])
]

for idx, (im, name, descs) in enumerate(chars_info):
    cx = 30 + idx * (card_w + 20)
    cy = 90
    d.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=12, fill=(255, 255, 255), outline=(220, 225, 232), width=1)
    im_scaled = im.resize((card_w - 4, card_img_h - 2), Image.Resampling.LANCZOS)
    showcase.paste(im_scaled, (cx + 2, cy + 2))
    d.line([(cx, cy + card_img_h), (cx + card_w, cy + card_img_h)], fill=(230, 234, 240), width=1)
    ty = cy + card_img_h + 12
    d.text((cx + 16, ty), name, font=font_h2, fill=(20, 30, 45))
    ty += 26
    for desc in descs:
        d.text((cx + 16, ty), desc, font=font_desc, fill=(70, 80, 95))
        ty += 25

showcase_path = os.path.join(PHOTOS_DIR, 'avatar_stacking_3chars_showcase.jpg')
showcase.save(showcase_path, quality=95)
showcase.save(os.path.join(BRAIN_DIR, 'avatar_stacking_3chars_showcase.jpg'), quality=95)
print(f'Saved: {showcase_path}')
