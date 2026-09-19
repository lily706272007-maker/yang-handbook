import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')
BRAIN_DIR = '/Users/yangyongzhu/.gemini/antigravity/brain/b58ba25a-e9f5-48ce-a86c-daf46a4f945e'

def composite_avatar(layers_list, out_path, add_forehead_shadow=True):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    bangs_im = None
    for layer_rel in layers_list:
        if not layer_rel:
            continue
        p = os.path.join(LAYERS_DIR, layer_rel)
        if os.path.exists(p):
            layer_im = Image.open(p).convert('RGBA')
            if 'bangs/' in layer_rel:
                bangs_im = layer_im
                if add_forehead_shadow:
                    # Delicate warm anime skin shadow under bangs with dithered edge
                    shadow = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
                    for y in range(110, 205):
                        for x in range(410, 545):
                            bx = x - 2
                            by = y - 4
                            if 0 <= bx < 1024 and 0 <= by < 1024:
                                p_bang = bangs_im.getpixel((bx, by))
                                if p_bang[3] > 180:
                                    p_curr = bangs_im.getpixel((x, y))
                                    if p_curr[3] < 50:
                                        by_edge = y - 5
                                        p_edge = bangs_im.getpixel((bx, by_edge)) if 0 <= by_edge < 1024 else (0,0,0,0)
                                        if p_edge[3] < 120 and ((x + y) % 2 == 0):
                                            shadow.putpixel((x, y), (170, 105, 75, 14))
                                        else:
                                            shadow.putpixel((x, y), (170, 105, 75, 26))
                    canvas.alpha_composite(shadow)
            canvas.alpha_composite(layer_im)
        else:
            print(f'Warning: Layer not found: {p}')
    canvas.convert('RGB').save(out_path, quality=95)
    print(f'Saved: {out_path}')
    return canvas

# -------------------------------------------------------------
# Character A:
# 女生・接睫毛美睫款＋低包包頭＋幼態短臉＋法式八字瀏海 (焦糖亞麻棕)
# -------------------------------------------------------------
char_a_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景
    'back_hair/back_02_low_bun_flaxen.png',    # L2: 後髮 (低包包頭・焦糖亞麻棕)
    'body/body_female_normal.png',             # L3: 身軀 (女外場制服・修身肩寬)
    'faces/face_02_nat.png',                   # L4: 臉型 (幼態短臉・自然膚色・天鵝頸)
    'mouths/mouth_01.png',                     # L5: 嘴巴 (微笑微揚嘴・晶透果凍唇)
    'noses/nose_01.png',                       # L6: 鼻子 (小巧點鼻・立體L型動漫鼻)
    'eyes/eye_f05.png',                        # L7: 眼睛 (柔美美睫眼・臥蠶陰影)
    'eyebrows/brow_f06.png',                   # L8: 眉毛 (歐式細眉・微上揚親切弧度)
    'bangs/bang_08_flaxen.png',                # L9: 前瀏海 (法式八字外翻・天使光澤)
    None                                       # L10: 配件
]

# -------------------------------------------------------------
# Character B:
# 男生・小眼睛＋漸層俐落短髮＋圓角方臉＋逗號瀏海＋透光黑框眼鏡 (純黑)
# -------------------------------------------------------------
char_b_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景
    'back_hair/back_07_undercut_black.png',    # L2: 後髮 (漸層俐落短髮・純黑)
    'body/body_male_normal.png',               # L3: 身軀 (男外場制服・英挺剪裁)
    'faces/face_05_nat.png',                   # L4: 臉型 (柔和方臉・45度立體下巴影)
    'mouths/mouth_03.png',                     # L5: 嘴巴 (平直微笑嘴・微抿嘴角笑意)
    'noses/nose_02.png',                       # L6: 鼻子 (挺拔直鼻・鼻尖高光)
    'eyes/eye_m04.png',                        # L7: 眼睛 (聚焦英氣小眼・沉穩自信)
    'eyebrows/brow_m01.png',                   # L8: 眉毛 (劍眉英氣眉・舒緩親和)
    'bangs/bang_03_black.png',                 # L9: 前瀏海 (韓系逗號中分・輕薄碎髮流)
    'accessories/acc_glasses_square.png'       # L10: 配件 (透光黑框方眼鏡・抗眩光天藍鏡片)
]

# -------------------------------------------------------------
# Character C:
# 女生留男生短髮 (Unisex)・清爽神采眼＋層次碎短髮＋經典鵝蛋臉 (純黑)
# -------------------------------------------------------------
char_c_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景
    'back_hair/back_10_layered_pixie_black.png',# L2: 後髮 (層次碎短髮・推剪質感)
    'body/body_female_normal.png',             # L3: 身軀 (女生外場制服身軀・柔美肩線)
    'faces/face_01_nat.png',                   # L4: 臉型 (經典鵝蛋臉・天鵝長頸・蜜桃氣色)
    'mouths/mouth_02.png',                     # L5: 嘴巴 (開朗微笑嘴・口腔暗角深邃笑容)
    'noses/nose_01.png',                       # L6: 鼻子 (小巧點鼻・立體L型動漫鼻)
    'eyes/eye_m01.png',                        # L7: 眼睛 (清爽神采眼・臥蠶笑意)
    'eyebrows/brow_f02.png',                   # L8: 眉毛 (溫柔平直眉・貼合眉骨)
    'bangs/bang_05_black.png',                 # L9: 前瀏海 (微捲短髮・左右平衡高顱頂)
    None                                       # L10: 配件
]

im_a = composite_avatar(char_a_layers, os.path.join(PHOTOS_DIR, 'composite_character_a.png'))
im_b = composite_avatar(char_b_layers, os.path.join(PHOTOS_DIR, 'composite_character_b.png'))
im_c = composite_avatar(char_c_layers, os.path.join(PHOTOS_DIR, 'composite_character_c.png'))

# Copy to brain dir
for f in ['composite_character_a.png', 'composite_character_b.png', 'composite_character_c.png']:
    p_src = os.path.join(PHOTOS_DIR, f)
    p_dst = os.path.join(BRAIN_DIR, f)
    with open(p_src, 'rb') as sf, open(p_dst, 'wb') as df:
        df.write(sf.read())

# Generate a 3-character side-by-side showcase card
showcase_w, showcase_h = 1536, 680
showcase = Image.new('RGB', (showcase_w, showcase_h), (245, 247, 250))
d = ImageDraw.Draw(showcase)

font_title = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 26)
font_h2 = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 17)
font_desc = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 13)

d.rectangle([(0, 0), (showcase_w, 65)], fill=(30, 39, 46))
d.text((30, 18), '【10 圖層絕對座標無縫合成・v139 無瑕瓷肌重調版】日系像素人型實測成果', font=font_title, fill=(255, 255, 255))

chars_info = [
    (im_a, '示範同仁 A（精緻甜美風）', [
        '性別體型：女性・優雅修身肩線',
        '五官搭配：幼態短臉＋柔美美睫眼＋果凍微笑唇',
        '髮型配色：低包包頭＋法式八字外翻（焦糖亞麻棕）',
        '美學修復：無瑕純淨基底、纖細法式外翻髮尾、柔和點鼻'
    ]),
    (im_b, '示範同仁 B（俐落專業風）', [
        '性別體型：男性・英挺幹練身軀',
        '五官搭配：柔和方臉＋自信聚焦小眼＋舒展劍眉',
        '髮型配件：漸層短髮＋韓系逗號中分＋透光黑框鏡',
        '美學修復：抹除眼眶黑圈、端正挺拔直鼻、消除方塊色差'
    ]),
    (im_c, '示範同仁 C（率性中性風）', [
        '性別體型：女性身軀 × 男士短髮（Unisex）',
        '五官搭配：經典鵝蛋臉＋英氣神采眼＋深邃開朗笑',
        '髮型配色：層次碎短髮＋微捲短髮（純黑）',
        '美學修復：修除假人眼窩、中性立體臉容、純淨瓷白膚質'
    ])
]

for idx, (im, name, desc_lines) in enumerate(chars_info):
    card_x = 30 + idx * 500
    card_y = 85
    d.rounded_rectangle([(card_x, card_y), (card_x + 475, card_y + 570)], radius=12, fill=(255, 255, 255), outline=(218, 225, 231), width=2)
    thumb = im.crop((240, 20, 784, 564)).resize((445, 445), Image.Resampling.LANCZOS)
    showcase.paste(thumb, (card_x + 15, card_y + 15))
    d.rectangle([(card_x + 15, card_y + 420), (card_x + 460, card_y + 460)], fill=(0, 0, 0, 160))
    d.text((card_x + 25, card_y + 428), name, font=font_h2, fill=(255, 230, 100))
    for l_idx, line in enumerate(desc_lines):
        d.text((card_x + 25, card_y + 472 + l_idx * 21), line, font=font_desc, fill=(70, 80, 95))

# Save versioned and master showcases
showcase.save(os.path.join(PHOTOS_DIR, 'avatar_stacking_3chars_showcase.jpg'), quality=95)
showcase.save(os.path.join(BRAIN_DIR, 'avatar_stacking_3chars_showcase.jpg'), quality=95)
showcase.save(os.path.join(PHOTOS_DIR, 'avatar_stacking_3chars_showcase_v139.jpg'), quality=95)
showcase.save(os.path.join(BRAIN_DIR, 'avatar_stacking_3chars_showcase_v139.jpg'), quality=95)
print('All showcases regenerated successfully with v139!')
