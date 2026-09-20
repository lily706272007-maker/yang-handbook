import os, sys, math
from PIL import Image, ImageDraw, ImageFilter
from collections import deque

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')
BRAIN_DIR = '/Users/yangyongzhu/.gemini/antigravity/brain/b58ba25a-e9f5-48ce-a86c-daf46a4f945e'

CANVAS_W, CANVAS_H = 896, 1200
CENTER_X = 448 # Center aisle of restaurant background

for sub in ['bg', 'body', 'faces', 'mouths', 'noses', 'eyes', 'eyebrows', 'bangs', 'back_hair', 'accessories']:
    os.makedirs(os.path.join(LAYERS_DIR, sub), exist_ok=True)

# ------------------------------------------------------------------
# Palette Swapping & Uniform Color Standardization Functions
# ------------------------------------------------------------------
def to_flaxen_brown(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    nr = int(58 + ratio * (240 - 58))
    ng = int(36 + ratio * (205 - 36))
    nb = int(22 + ratio * (160 - 22))
    if ratio > 0.52:
        sheen = (ratio - 0.52) / 0.48
        nr = min(255, int(nr + sheen * 25))
        ng = min(255, int(ng + sheen * 20))
        nb = min(255, int(nb + sheen * 10))
    return nr, ng, nb, a

def to_natural_black(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    nr = int(14 + ratio * (85 - 14))
    ng = int(15 + ratio * (95 - 15))
    nb = int(24 + ratio * (135 - 24))
    if ratio > 0.50:
        sheen = (ratio - 0.50) / 0.50
        nb = min(255, int(nb + sheen * 28))
        ng = min(255, int(ng + sheen * 15))
    return nr, ng, nb, a

def recolor_image(im_rgba, recolor_fn):
    out = Image.new('RGBA', im_rgba.size, (0, 0, 0, 0))
    for y in range(im_rgba.height):
        for x in range(im_rgba.width):
            p = im_rgba.getpixel((x, y))
            out.putpixel((x, y), recolor_fn(*p))
    return out

def recolor_uniform(im):
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for y in range(im.height):
        for x in range(im.width):
            p = im.getpixel((x, y))
            if p[3] < 30:
                continue
            r, g, b = p[:3]
            is_skin = (r > 130 and g > 85 and r > b + 15)
            is_metal = (abs(r - g) < 6 and abs(g - b) < 6 and r > 90)
            if is_skin:
                out.putpixel((x, y), p)
            elif is_metal:
                out.putpixel((x, y), (140, 145, 155, p[3]))
            else:
                v = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
                if v < 0.08:
                    nr, ng, nb = 14, 15, 18
                elif v < 0.18:
                    t = (v - 0.08) / 0.10
                    nr = int(14 + t * (26 - 14))
                    ng = int(15 + t * (28 - 15))
                    nb = int(18 + t * (33 - 18))
                elif v < 0.32:
                    t = (v - 0.18) / 0.14
                    nr = int(26 + t * (42 - 26))
                    ng = int(28 + t * (45 - 28))
                    nb = int(33 + t * (52 - 33))
                else:
                    t = min(1.0, (v - 0.32) / 0.25)
                    nr = int(42 + t * (60 - 42))
                    ng = int(45 + t * (64 - 45))
                    nb = int(52 + t * (74 - 52))
                out.putpixel((x, y), (nr, ng, nb, p[3]))
    return out

# ------------------------------------------------------------------
# 1. Background Layer (Layer 1) - Original 896x1200 Uncropped
# ------------------------------------------------------------------
print('1. Background Layer (Original 896x1200 restaurant scene)...')
bg = Image.open(os.path.join(PHOTOS_DIR, 'restaurant_pixel_bg.jpg')).convert('RGBA')
assert bg.size == (CANVAS_W, CANVAS_H), f"Background size is {bg.size}, expected {(CANVAS_W, CANVAS_H)}"
bg.save(os.path.join(LAYERS_DIR, 'bg/bg_restaurant.png'))

# ------------------------------------------------------------------
# 2. Body Layers (Layer 3) - Head-to-Thigh Framing & Standard Black Uniform
# ------------------------------------------------------------------
print('2. Body Layers (Standardized black uniform, head-to-thigh framing)...')
scale_factor = 0.74
feat_scale = scale_factor * 1.05

body_meta = [
    ('body_layer_male_normal.png', 'body_male_normal.png', (204, 35, 753, 1024), 0.74, False),
    ('body_layer_male_sturdy.png', 'body_male_sturdy.png', (128, 97, 891, 1024), 0.72, False),
    ('body_layer_female_normal.png', 'body_female_normal.png', (189, 92, 789, 1024), 0.74, True),
    ('body_layer_female_chubby.png', 'body_female_chubby.png', (225, 133, 789, 1024), 0.72, True)
]

for src_file, out_name, bbox, b_scale, is_female in body_meta:
    raw = Image.open(os.path.join(PHOTOS_DIR, src_file)).convert('RGBA')
    recolored = recolor_uniform(raw)
    
    b_crop = recolored.crop(bbox)
    bw = int((bbox[2] - bbox[0]) * b_scale)
    bh = int((bbox[3] - bbox[1]) * b_scale)
    b_scaled = b_crop.resize((bw, bh), Image.Resampling.LANCZOS)
    
    body_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    paste_x = CENTER_X - bw // 2
    paste_y = 444 if is_female else 440
    body_canvas.paste(b_scaled, (paste_x, paste_y), b_scaled)
    body_canvas.save(os.path.join(LAYERS_DIR, 'body', out_name))

# ------------------------------------------------------------------
# 3. Face Shapes (Layer 4) - Porcelain Face, Seamless Extended Neck
# ------------------------------------------------------------------
print('3. Face Shapes (Clean porcelain base, seamless extended neck)...')
face_eye_mids = {
    1: 132.5,
    2: 125.5,
    3: 120.0,
    4: 114.5,
    5: 134.5,
    6: 128.0,
    7: 124.0,
    8: 118.5,
    9: 123.5,
    10: 127.5
}

for i in range(1, 11):
    for tone in ['natural', 'tan']:
        f_path = os.path.join(PHOTOS_DIR, f'faces/face_{i:02d}_{tone}.jpg')
        if not os.path.exists(f_path):
            continue
        fim = Image.open(f_path).convert('RGB')
        # Crop to y=355 so card labels (自然膚色 01. 經典鵝蛋臉) are NEVER included
        hc = fim.crop((10, 15, 258, 355))
        base_skin = hc.getpixel((90, 125))
        shadow_skin = (int(base_skin[0] * 0.82), int(base_skin[1] * 0.74), int(base_skin[2] * 0.72), 255)
        
        # Extend canvas downward to extend neck 40px deep into shirt
        head_full = Image.new('RGBA', (hc.width, hc.height + 40), (0, 0, 0, 0))
        for y in range(hc.height):
            for x in range(hc.width):
                r, g, b = hc.getpixel((x, y))[:3]
                is_skin = (r > b + 18) or (r < 95 and g < 95 and b < 95 and y < 330)
                if is_skin and (8 < x < hc.width - 8 and 8 < y < hc.height - 4):
                    head_full.putpixel((x, y), (r, g, b, 255))
                    
        # Clean eye sockets, nose, and mouth zones for clean porcelain face
        for y in range(160, 290):
            for x in range(40, 185):
                p = head_full.getpixel((x, y))
                if p[3] > 0 and max(p[:3]) > 100:
                    head_full.putpixel((x, y), base_skin)
                    
        # Seamless neck downward extension (goes deep behind front collar lapels)
        for y in range(hc.height - 4, hc.height + 38):
            for x in range(95, 180):
                src_color = head_full.getpixel((x, hc.height - 8))
                if src_color[3] > 0:
                    head_full.putpixel((x, y), src_color)
                else:
                    head_full.putpixel((x, y), shadow_skin if x > 130 else (*base_skin, 255))
                    
        hw = int(head_full.width * feat_scale)
        hh = int(head_full.height * feat_scale)
        head_scaled = head_full.resize((hw, hh), Image.Resampling.LANCZOS)
        
        # Exact Golden Ratio landmark alignment:
        # eye_mid_x -> CENTER_X (448), eye_level (168) -> pupil line (330)
        face_x = CENTER_X - int(face_eye_mids[i] * feat_scale)
        face_y = 330 - int(168 * feat_scale)
        
        face_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        face_canvas.paste(head_scaled, (face_x, face_y), head_scaled)
        
        t_short = 'nat' if tone == 'natural' else 'tan'
        face_canvas.save(os.path.join(LAYERS_DIR, f'faces/face_{i:02d}_{t_short}.png'))

# ------------------------------------------------------------------
# 4. Eyes Layer (Layer 7) - Aegyo-sal, Catchlights, Orbit Centered at y=330
# ------------------------------------------------------------------
print('4. Eyes Layer (Watery sparkle, orbital alignment at y=330)...')
eye_cat = Image.open(os.path.join(PHOTOS_DIR, 'eye_styles_14_catalog.jpg'))
eye_cards = [
    ('eye_m01', (29, 132, 333, 230)),
    ('eye_m02', (359, 132, 663, 230)),
    ('eye_m03', (690, 132, 994, 230)),
    ('eye_m04', (29, 350, 333, 448)),
    ('eye_m05', (359, 350, 663, 448)),
    ('eye_m06', (690, 350, 994, 448)),
    ('eye_f01', (29, 623, 254, 719)),
    ('eye_f02', (275, 623, 501, 719)),
    ('eye_f03', (522, 623, 748, 719)),
    ('eye_f04', (768, 623, 994, 719)),
    ('eye_f05', (29, 842, 255, 937)),
    ('eye_f06', (275, 842, 501, 937)),
    ('eye_f07', (522, 842, 748, 937)),
    ('eye_f08', (768, 842, 994, 937)),
]

for name, box in eye_cards:
    card = eye_cat.crop(box)
    e_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for y in range(4, card.height - 4):
        for x in range(4, card.width - 4):
            r, g, b = card.getpixel((x, y))
            is_sclera = (r > 215 and g > 215 and b > 215 and abs(r - b) < 18)
            is_dark = (r < 140 and g < 100 and b < 100) or (max(r, g, b) < 90)
            is_highlight = (r > 245 and g > 245 and b > 245)
            if is_sclera or is_dark or is_highlight:
                e_rgba.putpixel((x, y), (r, g, b, 255))
                
    if name == 'eye_f05':
        for y in range(int(card.height * 0.72), card.height):
            for x in range(card.width):
                p = e_rgba.getpixel((x, y))
                if p[3] > 0 and max(p[:3]) < 90:
                    e_rgba.putpixel((x, y), (0, 0, 0, 0))
                    
    bbox = e_rgba.getbbox()
    if bbox:
        ec = e_rgba.crop(bbox)
        target_w = int(120.0 * feat_scale * 0.88 / 0.777)
        ratio = float(target_w) / ec.width
        scaled = ec.resize((int(ec.width * ratio), int(ec.height * ratio)), Image.Resampling.NEAREST)
        
        c = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        px = CENTER_X - scaled.width // 2
        py = 330 - scaled.height // 2 # Golden ratio pupil center
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'eyes/{name}.png'))

# ------------------------------------------------------------------
# 5. Eyebrows Layer (Layer 8) - Brow Bone Alignment at y=312
# ------------------------------------------------------------------
print('5. Eyebrows Layer (Aligned with brow bone at y=312)...')
brow_cat = Image.open(os.path.join(PHOTOS_DIR, 'eyebrow_styles_11_catalog.jpg'))
brow_cards = [
    ('brow_m01', (29, 130, 333, 230)),
    ('brow_m02', (359, 130, 663, 230)),
    ('brow_m03', (690, 130, 994, 230)),
    ('brow_m04', (29, 360, 333, 460)),
    ('brow_m05', (359, 360, 663, 460)),
    ('brow_f01', (29, 580, 254, 680)),
    ('brow_f02', (275, 580, 501, 680)),
    ('brow_f03', (522, 580, 748, 680)),
    ('brow_f04', (768, 580, 994, 680)),
    ('brow_f05', (29, 790, 255, 890)),
    ('brow_f06', (275, 790, 501, 890)),
]

for name, box in brow_cards:
    card = brow_cat.crop(box)
    b_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for y in range(4, card.height - 4):
        for x in range(4, card.width - 4):
            r, g, b = card.getpixel((x, y))
            if max(r, g, b) < 110:
                b_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        target_w = int(122.0 * feat_scale * 0.88 / 0.777)
        ratio = float(target_w) / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.NEAREST)
        
        c = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        px = CENTER_X - scaled.width // 2
        py = 312 - scaled.height // 2 # 18px above pupil line
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'eyebrows/{name}.png'))

# ------------------------------------------------------------------
# 6. Nose Layer (Layer 6) - Crisp Anime Nose at y=362
# ------------------------------------------------------------------
print('6. Nose Layer (Midline x=448, y=362)...')
nose_styles = {
    'nose_01': {'line_len': 8, 'w': 2, 'highlight': True, 'dot': True},
    'nose_02': {'line_len': 10, 'w': 2, 'highlight': True, 'dot': True},
    'nose_03': {'line_len': 6, 'w': 1, 'highlight': False, 'dot': True},
    'nose_04': {'line_len': 9, 'w': 2, 'highlight': True, 'dot': False},
}

for name, conf in nose_styles.items():
    c = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    ny = 362
    ll = conf['line_len']
    d.line([(CENTER_X, ny - ll), (CENTER_X + 1, ny)], fill=(155, 95, 75, 220), width=conf['w'])
    if conf['dot']:
        d.point((CENTER_X + 2, ny + 1), fill=(130, 75, 55, 240))
    if conf['highlight']:
        d.point((CENTER_X - 1, ny), fill=(255, 230, 215, 190))
    c.save(os.path.join(LAYERS_DIR, f'noses/{name}.png'))

# ------------------------------------------------------------------
# 7. Mouth Layer (Layer 5) - Real Mouth Catalog Illustrations at y=390
# ------------------------------------------------------------------
print('7. Mouth Layer (Real illustrations with feathered blending at y=390)...')
mouth_cat = Image.open(os.path.join(PHOTOS_DIR, 'mouth_styles_6_catalog.jpg'))
mouth_boxes = [
    ('mouth_01', (61, 206, 324, 439), 113, 130), # 微笑微揚嘴
    ('mouth_02', (380, 206, 644, 439), 121, 119), # 露齒開朗笑
    ('mouth_03', (700, 206, 963, 439), 113, 130), # 平直自然嘴
    ('mouth_04', (61, 620, 324, 853), 98, 130),  # 小巧微張嘴
    ('mouth_05', (380, 620, 644, 853), 105, 128), # 親切波浪笑
    ('mouth_06', (700, 620, 963, 853), 98, 129),  # 飽滿立體唇
]

for name, box, cx, cy in mouth_boxes:
    card = mouth_cat.crop(box)
    x1 = max(0, cx - 80)
    y1 = max(0, cy - 45)
    lip_crop = card.crop((x1, y1, x1 + 160, y1 + 90))
    base_skin = lip_crop.getpixel((15, 10))
    
    out = Image.new('RGBA', lip_crop.size, (0, 0, 0, 0))
    for y in range(lip_crop.height):
        for x in range(lip_crop.width):
            p = lip_crop.getpixel((x, y))
            d_sq = ((x - 80.0) / 72.0)**2 + ((y - 45.0) / 38.0)**2
            if d_sq >= 1.0:
                continue
            color_diff = sum(abs(p[c] - base_skin[c]) for c in range(3))
            radial_fade = 1.0 if d_sq < 0.65 else (1.0 - (d_sq - 0.65) / 0.35)
            
            is_dark = max(p) < 95
            is_white = p[0] > 230 and p[1] > 230 and p[2] > 230
            is_lip_tone = (p[0] - p[1] > 30) or (p[0] - p[2] > 50)
            is_highlight = (p[0] > 245 and p[1] > 210 and p[2] > 195)
            
            if is_dark or is_white or is_lip_tone or is_highlight or color_diff > 25:
                a = int(255 * radial_fade)
                out.putpixel((x, y), (*p[:3], a))
            elif color_diff > 12:
                a = int(180 * radial_fade * (color_diff / 25.0))
                out.putpixel((x, y), (*p[:3], a))
                
    bbox = out.getbbox()
    if bbox:
        mc = out.crop(bbox)
        target_w = int(54.0 * feat_scale * 0.88 / 0.777)
        ratio = float(target_w) / mc.width
        scaled = mc.resize((int(mc.width * ratio), int(mc.height * ratio)), Image.Resampling.LANCZOS)
        
        c = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        px = CENTER_X - scaled.width // 2
        py = 390 - scaled.height // 2
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'mouths/{name}.png'))

# ------------------------------------------------------------------
# 8. Bangs Layer (Layer 9) - High Cranial Dome at y=232
# ------------------------------------------------------------------
print('8. Bangs Layer (High cranial dome at y=232)...')
bangs_cat = Image.open(os.path.join(PHOTOS_DIR, 'bangs_16_catalog.jpg'))
bang_cards = [
    ('bang_01', (135, 60, 290, 230), 235),
    ('bang_02', (415, 60, 585, 230), 235),
    ('bang_03', (695, 60, 876, 230), 248),
    ('bang_04', (135, 280, 290, 450), 235),
    ('bang_05', (415, 280, 585, 450), 238),
    ('bang_06', (710, 280, 865, 450), 235),
    ('bang_07', (38, 542, 208, 715), 245),
    ('bang_08', (222, 542, 402, 735), 245),
    ('bang_09', (425, 542, 585, 715), 235),
    ('bang_10', (615, 542, 780, 715), 235),
    ('bang_11', (805, 542, 975, 715), 240),
    ('bang_12', (42, 770, 205, 945), 235),
    ('bang_13', (228, 770, 398, 945), 240),
    ('bang_14', (425, 770, 585, 945), 245),
    ('bang_15', (615, 770, 780, 945), 245),
    ('bang_16', (805, 770, 975, 945), 240)
]

for name, box, target_w_base in bang_cards:
    card = bangs_cat.crop(box)
    dark_pixels = set()
    for y in range(card.height):
        if y < 14: continue
        for x in range(card.width):
            if y < 35 and x < 35: continue
            p = card.getpixel((x, y))
            if max(p) < 135:
                dark_pixels.add((x, y))
                
    hair_pixels = set()
    seeds = [p for p in dark_pixels if p[1] < 45]
    queue = deque(seeds)
    visited = set(seeds)
    while queue:
        cx, cy = queue.popleft()
        hair_pixels.add((cx, cy))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,-1), (-1,1), (1,1)]:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in dark_pixels and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
                
    b_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for x, y in hair_pixels:
        b_rgba.putpixel((x, y), (*card.getpixel((x, y)), 255))
        
    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        target_w = int(target_w_base * feat_scale * 0.88 / 0.777)
        ratio = float(target_w) / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.LANCZOS)
        
        c_black = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        px = CENTER_X - scaled.width // 2
        py = 232 # Cranial dome baseline
        c_black.paste(scaled, (px, py), scaled)
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_black = recolor_image(c_black, to_natural_black)
        
        c_black.save(os.path.join(LAYERS_DIR, f'bangs/{name}_black.png'))
        c_flaxen.save(os.path.join(LAYERS_DIR, f'bangs/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 9. Back Hair Layer (Layer 2) - Exactly 20 Files (10 Styles × 2 Colors)
# ------------------------------------------------------------------
print('9. Back Hair Layer (Accurate 3-row catalog extraction at y=232)...')
back_cat = Image.open(os.path.join(PHOTOS_DIR, 'back_hair_styles_catalog.jpg'))

# Clean bounding boxes from 3-row catalog
back_cards = [
    # Row 1: Female styles 1-3
    ('back_01_mid_bun', (50, 90, 185, 270), (195, 90, 320, 270), 235),
    ('back_02_low_bun', (370, 90, 500, 270), (510, 90, 635, 270), 235),
    ('back_03_bob_cut', (680, 90, 810, 270), (820, 90, 945, 270), 235),
    # Row 2: Female styles 4-6
    ('back_04_claw_clip', (55, 340, 185, 520), (190, 340, 320, 520), 235),
    ('back_05_high_pony', (360, 340, 500, 520), (505, 340, 635, 520), 245),
    ('back_06_low_pony', (680, 340, 810, 520), (815, 340, 945, 520), 235),
    # Row 3: Male styles 7-10
    ('back_07_undercut', (55, 700, 245, 880), None, 235),
    ('back_08_wavy_bob', (295, 700, 480, 880), None, 235),
    ('back_09_half_up', (535, 700, 715, 880), None, 235),
    ('back_10_layered_pixie', (765, 700, 945, 880), None, 235)
]

def extract_hair_pixels(card_crop):
    b_rgba = Image.new('RGBA', card_crop.size, (0, 0, 0, 0))
    for y in range(4, card_crop.height - 4):
        for x in range(4, card_crop.width - 4):
            r, g, b = card_crop.getpixel((x, y))[:3]
            # Dark hair or flaxen hair
            is_hair = (max(r, g, b) < 140) or (r > 60 and g > 40 and b < 80 and max(r, g, b) < 170)
            # exclude white background / grey card background
            if is_hair:
                b_rgba.putpixel((x, y), (r, g, b, 255))
    return b_rgba

# Clean up any extra untracked files
for f in os.listdir(os.path.join(LAYERS_DIR, 'back_hair')):
    if f.endswith('.png'):
        os.remove(os.path.join(LAYERS_DIR, 'back_hair', f))

for name, black_box, flaxen_box, target_w_base in back_cards:
    black_crop = back_cat.crop(black_box)
    b_rgba = extract_hair_pixels(black_crop)
    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        target_w = int(target_w_base * feat_scale * 0.88 / 0.777)
        ratio = float(target_w) / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.LANCZOS)
        
        c_black = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        px = CENTER_X - scaled.width // 2
        py = 232 # Cranial dome baseline
        c_black.paste(scaled, (px, py), scaled)
        c_black = recolor_image(c_black, to_natural_black)
        c_black.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_black.png'))
        
        # Flaxen version
        if flaxen_box:
            flaxen_crop = back_cat.crop(flaxen_box)
            f_rgba = extract_hair_pixels(flaxen_crop)
            f_bbox = f_rgba.getbbox()
            if f_bbox:
                fc = f_rgba.crop(f_bbox)
                f_scaled = fc.resize((int(fc.width * ratio), int(fc.height * ratio)), Image.Resampling.LANCZOS)
                c_flaxen = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
                c_flaxen.paste(f_scaled, (px, py), f_scaled)
                c_flaxen = recolor_image(c_flaxen, to_flaxen_brown)
                c_flaxen.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_flaxen.png'))
            else:
                c_flaxen = recolor_image(c_black, to_flaxen_brown)
                c_flaxen.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_flaxen.png'))
        else:
            c_flaxen = recolor_image(c_black, to_flaxen_brown)
            c_flaxen.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 10. Accessories Layer (Layer 10) - Crystal Clear Anime Glasses at y=330
# ------------------------------------------------------------------
print('10. Accessories Layer (Crystal clear anime glasses at pupil line y=330)...')
for shape in ['square', 'round']:
    c = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    py = 330
    
    if shape == 'square':
        # 100% transparent glass, fine black wireframe, white specular glare reflection
        d.rounded_rectangle([(CENTER_X - 58, py - 18), (CENTER_X - 10, py + 18)], radius=3, outline=(30, 32, 38, 250), width=2)
        d.rounded_rectangle([(CENTER_X + 10, py - 18), (CENTER_X + 58, py + 18)], radius=3, outline=(30, 32, 38, 250), width=2)
        d.line([(CENTER_X - 10, py - 3), (CENTER_X + 10, py - 3)], fill=(40, 42, 48, 245), width=2)
        d.line([(CENTER_X - 50, py - 11), (CENTER_X - 35, py - 11)], fill=(255, 255, 255, 200), width=1)
        d.line([(CENTER_X + 18, py - 11), (CENTER_X + 33, py - 11)], fill=(255, 255, 255, 200), width=1)
    else:
        d.ellipse([(CENTER_X - 58, py - 19), (CENTER_X - 10, py + 19)], outline=(30, 32, 38, 250), width=2)
        d.ellipse([(CENTER_X + 10, py - 19), (CENTER_X + 58, py + 19)], outline=(30, 32, 38, 250), width=2)
        d.line([(CENTER_X - 10, py - 2), (CENTER_X + 10, py - 2)], fill=(40, 42, 48, 245), width=2)
        d.line([(CENTER_X - 48, py - 10), (CENTER_X - 34, py - 10)], fill=(255, 255, 255, 200), width=1)
        d.line([(CENTER_X + 20, py - 10), (CENTER_X + 34, py - 10)], fill=(255, 255, 255, 200), width=1)
        
    c.save(os.path.join(LAYERS_DIR, f'accessories/acc_glasses_{shape}.png'))

print('All 10 layers rebuilt successfully with 896x1200 uncropped architecture!')

