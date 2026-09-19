import os
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')
BRAIN_DIR = '/Users/yangyongzhu/.gemini/antigravity/brain/b58ba25a-e9f5-48ce-a86c-daf46a4f945e'

def composite_avatar(layers_list, out_path):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    for layer_rel in layers_list:
        if not layer_rel:
            continue
        p = os.path.join(LAYERS_DIR, layer_rel)
        if os.path.exists(p):
            layer_im = Image.open(p).convert('RGBA')
            canvas.alpha_composite(layer_im, (0, 0))
        else:
            print(f'Warning: Layer not found: {p}')
    canvas.convert('RGB').save(out_path, quality=95)
    print(f'Saved: {out_path}')
    return canvas

# -------------------------------------------------------------
# Character A:
# 女生・接睫毛美睫款＋低包包頭＋清秀瓜子臉＋法式八字瀏海 (亞麻棕)
# -------------------------------------------------------------
char_a_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景
    'back_hair/back_02_low_bun_flaxen.png',    # L2: 後髮 (低包包頭・亞麻棕)
    'body/body_female_normal.png',             # L3: 身軀 (女外場制服)
    'faces/face_02_nat.png',                   # L4: 臉型 (幼態短臉・自然膚色)
    'mouths/mouth_01.png',                     # L5: 嘴巴 (微笑微揚嘴)
    'noses/nose_01.png',                       # L6: 鼻子 (小巧點鼻)
    'eyes/eye_f05.png',                        # L7: 眼睛 (濃密美睫眼 - 上下睫毛加強)
    'eyebrows/brow_f06.png',                   # L8: 眉毛 (歐式細眉)
    'bangs/bang_08_flaxen.png',                # L9: 前瀏海 (法式八字外翻・亞麻棕)
    None                                       # L10: 配件
]

# -------------------------------------------------------------
# Character B:
# 男生・小眼睛＋漸層俐落短髮＋圓角方臉＋逗號瀏海＋黑框眼鏡 (純黑)
# -------------------------------------------------------------
char_b_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景
    'back_hair/back_07_undercut_black.png',    # L2: 後髮 (漸層俐落短髮・純黑)
    'body/body_male_normal.png',               # L3: 身軀 (男外場制服)
    'faces/face_05_nat.png',                   # L4: 臉型 (柔和方臉/圓角方臉)
    'mouths/mouth_03.png',                     # L5: 嘴巴 (平直自然嘴)
    'noses/nose_02.png',                       # L6: 鼻子 (挺拔直鼻)
    'eyes/eye_m04.png',                        # L7: 眼睛 (小眼睛)
    'eyebrows/brow_m01.png',                   # L8: 眉毛 (劍眉英氣眉)
    'bangs/bang_03_black.png',                 # L9: 前瀏海 (韓系逗號中分・純黑)
    'accessories/acc_glasses_square.png'       # L10: 配件 (黑框方眼鏡)
]

# -------------------------------------------------------------
# Character C:
# 女生留男生短髮 (Unisex)・清爽神采眼＋層次碎短髮＋經典鵝蛋臉 (純黑)
# -------------------------------------------------------------
char_c_layers = [
    'bg/bg_restaurant.png',                    # L1: 背景
    'back_hair/back_10_layered_pixie_black.png',# L2: 後髮 (層次碎短髮・純黑)
    'body/body_female_normal.png',             # L3: 身軀 (女生外場制服身軀)
    'faces/face_01_nat.png',                   # L4: 臉型 (經典鵝蛋臉)
    'mouths/mouth_02.png',                     # L5: 嘴巴 (露齒開朗笑)
    'noses/nose_01.png',                       # L6: 鼻子 (小巧點鼻)
    'eyes/eye_m01.png',                        # L7: 眼睛 (清爽神采眼)
    'eyebrows/brow_f02.png',                   # L8: 眉毛 (溫柔平直眉)
    'bangs/bang_05_black.png',                 # L9: 前瀏海 (四六微捲中分・男生短髮頭)
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

# Header
d.rectangle([(0, 0), (showcase_w, 65)], fill=(30, 39, 46))
d.text((30, 18), '【10 圖層絕對座標無縫合成】32位元日系像素人型・即時疊加驗證成果', font=font_title, fill=(255, 255, 255))

chars_info = [
    (im_a, '示範同仁 A（精緻甜美風）', [
        '• 後髮：2. 低包包頭（亞麻棕）',
        '• 臉型：2. 清秀瓜子臉（自然膚）',
        '• 眼睛：5. 濃密美睫眼（上下睫毛）',
        '• 眉毛：6. 歐式細眉',
        '• 瀏海：8. 法式八字外翻（亞麻棕）',
        '• 身軀：女外場制服'
    ]),
    (im_b, '示範同仁 B（沈穩俐落風）', [
        '• 後髮：7. 漸層俐落短髮（純黑）',
        '• 臉型：5. 柔和圓角方臉',
        '• 眼睛：4. 小眼睛款（自然沈穩）',
        '• 眉毛：1. 劍眉英氣眉',
        '• 瀏海：3. 韓系逗號中分（純黑）',
        '• 配件：黑框方型眼鏡'
    ]),
    (im_c, '示範同仁 C（女生留男生頭・中性風）', [
        '• 後髮：10. 層次碎短髮（純黑）',
        '• 臉型：1. 經典鵝蛋臉',
        '• 眼睛：1. 清爽神采眼',
        '• 眉毛：2. 溫柔平直眉',
        '• 瀏海：5. 四六微捲短髮（男士款）',
        '• 身軀：女外場制服（打破性別限制）'
    ]),
]

card_w = 470
card_h = 570
crop_box = (200, 20, 824, 760) # crop head and upper body
crop_size = (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1])

for idx, (im, name, desc_lines) in enumerate(chars_info):
    cx = 30 + idx * (card_w + 33)
    cy = 85
    # card background
    d.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=10, fill=(255, 255, 255), outline=(218, 225, 233), width=1)
    # title banner
    d.rounded_rectangle([(cx, cy), (cx + card_w, cy + 45)], radius=10, fill=(240, 243, 248))
    d.rectangle([(cx, cy + 30), (cx + card_w, cy + 45)], fill=(240, 243, 248))
    d.text((cx + 15, cy + 12), name, font=font_h2, fill=(44, 62, 80))
    
    # avatar preview
    cropped = im.crop(crop_box)
    preview = cropped.resize((240, int(240 * (crop_size[1] / crop_size[0]))), Image.Resampling.LANCZOS)
    d.rectangle([(cx + 15, cy + 58), (cx + 15 + preview.width + 4, cy + 58 + preview.height + 4)], fill=(230, 234, 240))
    showcase.paste(preview, (cx + 17, cy + 60))
    
    # Layer details list
    tx = cx + 275
    ty = cy + 68
    d.text((tx, ty), '【10 層堆疊明細】', font=font_h2, fill=(39, 174, 96))
    ty += 32
    for line in desc_lines:
        d.text((tx, ty), line, font=font_desc, fill=(74, 85, 104))
        ty += 28

showcase_path = os.path.join(PHOTOS_DIR, 'avatar_stacking_3chars_showcase.jpg')
showcase.save(showcase_path, quality=95)
showcase.save(os.path.join(BRAIN_DIR, 'avatar_stacking_3chars_showcase.jpg'), quality=95)
print(f'Saved showcase: {showcase_path}')
