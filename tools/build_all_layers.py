import os, sys, math
from PIL import Image, ImageDraw, ImageFilter
from collections import deque

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')

for sub in ['bg', 'body', 'faces', 'mouths', 'noses', 'eyes', 'eyebrows', 'bangs', 'back_hair', 'accessories']:
    os.makedirs(os.path.join(LAYERS_DIR, sub), exist_ok=True)

# ------------------------------------------------------------------
# Palette swapping helper functions with Rich Warm Caramel & Indigo Luster
# ------------------------------------------------------------------
def to_flaxen_brown(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    # Japanese rich caramel milk-tea brown (warm chestnuts in shadows, caramel in highlights)
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
    # Crisp indigo-slate anime black with subtle ambient warmth in shadow
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

# ------------------------------------------------------------------
# 1. Background Layer (Layer 1)
# ------------------------------------------------------------------
print('1. Background Layer...')
bg = Image.open(os.path.join(PHOTOS_DIR, 'clean_restaurant_pixel_bg.jpg')).convert('RGBA')
bg.save(os.path.join(LAYERS_DIR, 'bg/bg_restaurant.png'))

# ------------------------------------------------------------------
# 2. Body Layers (Layer 3) - Tailored Female Shoulders & Seam Highlights
# ------------------------------------------------------------------
print('2. Body Layers (Tailored female shoulder width & rich charcoal uniform)...')
body_configs = [
    ('body_layer_male_normal.png', 'body_male_normal.png', 260, False, False),
    ('body_layer_male_sturdy.png', 'body_male_sturdy.png', 200, True, False),
    ('body_layer_female_normal.png', 'body_female_normal.png', 208, False, True),
    ('body_layer_female_chubby.png', 'body_female_chubby.png', 152, True, True)
]

for src_name, out_name, dy, clean_stub, is_female_body in body_configs:
    b_path = os.path.join(PHOTOS_DIR, src_name)
    if os.path.exists(b_path):
        src = Image.open(b_path).convert('RGBA')
        if clean_stub:
            if 'sturdy' in src_name:
                for y in range(0, 170):
                    for x in range(350, 650):
                        src.putpixel((x, y), (0, 0, 0, 0))
            elif 'chubby' in src_name:
                for y in range(144, 280):
                    for x in range(200, 800):
                        p = src.getpixel((x, y))
                        if p[3] > 0 and (p[0] > p[2] + 25) and p[0] > 140:
                            src.putpixel((x, y), (0, 0, 0, 0))
        flipped = src.transpose(Image.FLIP_LEFT_RIGHT)
        
        # Refine female shoulder width to prevent "football player" silhouette
        if is_female_body:
            w_new = int(flipped.width * 0.935)
            h_new = flipped.height
            scaled_f = flipped.resize((w_new, h_new), Image.Resampling.LANCZOS)
            c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
            paste_x = 512 - w_new // 2
            c.paste(scaled_f, (paste_x, dy), scaled_f)
        else:
            c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
            c.paste(flipped, (0, dy), flipped)
        
        # Add subtle navy-charcoal warmth and lapel rim highlights
        for y in range(dy, min(1024, dy + flipped.height)):
            for x in range(1024):
                p = c.getpixel((x, y))
                if p[3] == 0: continue
                # Slightly tint dark suit pixels towards rich charcoal-navy
                if max(p[:3]) < 75 and abs(p[0] - p[1]) < 6:
                    c.putpixel((x, y), (max(0, p[0] - 2), p[1] + 2, p[2] + 8, p[3]))
        
        c.save(os.path.join(LAYERS_DIR, 'body', out_name))

# ------------------------------------------------------------------
# 3. Face Shapes (Layer 4) - Flawless Porcelain Face Base, Slender Neck, 45deg Chin Shadow
# ------------------------------------------------------------------
print('3. Face Shapes (Flawless porcelain face base, slender neck, warm 45deg chin shadow)...')
for i in range(1, 11):
    is_female = (i in [1, 2, 3, 7, 8, 9, 10])
    for tone in ['natural', 'tan']:
        f_path = os.path.join(PHOTOS_DIR, f'faces/face_{i:02d}_{tone}.jpg')
        if not os.path.exists(f_path):
            continue
        fim = Image.open(f_path)
        hc = fim.crop((10, 15, 258, 355)).convert('RGBA')
        base_skin = hc.getpixel((90, 125)) # Pure forehead base skin
        
        # 1. Extract transparent background first to isolate face contour
        head_rgba = Image.new('RGBA', hc.size, (0, 0, 0, 0))
        for y in range(hc.height):
            for x in range(hc.width):
                r, g, b, _ = hc.getpixel((x, y))
                is_skin_or_line = (r > b + 18) or (r < 100 and g < 100 and b < 100)
                if is_skin_or_line:
                    head_rgba.putpixel((x, y), (r, g, b, 255))
                    
        # 2. Find natural right cheek shadow boundary at y=136 and y=192
        sx136, sx192 = 164, 170
        for x in range(120, 220):
            p = head_rgba.getpixel((x, 136))
            if p[3] > 0 and p[0] < base_skin[0] - 8 and p[0] > 100:
                sx136 = x; break
        for x in range(120, 220):
            p = head_rgba.getpixel((x, 192))
            if p[3] > 0 and p[0] < base_skin[0] - 8 and p[0] > 100:
                sx192 = x; break
                
        # 3. Flawless face wipe: remove all pre-baked eye sockets, old nose outlines and mouth marks
        for y in range(136, 275):
            row_xs = [x for x in range(hc.width) if head_rgba.getpixel((x, y))[3] > 0]
            if not row_xs: continue
            min_x = min(row_xs)
            
            if y <= 192:
                t = (y - 136) / (192 - 136)
                thresh_x = int(sx136 + t * (sx192 - sx136))
            else:
                thresh_x = 168
                for x in range(130, 220):
                    p = head_rgba.getpixel((x, y))
                    if p[3] > 0 and p[0] < base_skin[0] - 8 and p[0] > 100:
                        thresh_x = x; break
                        
            # Clean from inner jawline (min_x + 3) to right cheek shadow (thresh_x)
            for x in range(min_x + 3, thresh_x):
                p = head_rgba.getpixel((x, y))
                if p[3] > 0:
                    head_rgba.putpixel((x, y), base_skin)
                    
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        c.paste(head_rgba, (380, 40), head_rgba)
        
        # Taper neck: Slender swan neck for females (min_x 460, max_x 518)
        for y in range(320, c.height):
            for x in range(c.width):
                p = c.getpixel((x, y))
                if p[3] == 0: continue
                if y > 362:
                    c.putpixel((x, y), (0, 0, 0, 0))
                elif y > 328:
                    t = (y - 328) / (362.0 - 328.0)
                    if is_female:
                        min_neck_x = 460 + t * 25
                        max_neck_x = 518 - t * 13
                    else:
                        min_neck_x = 448 + t * 37
                        max_neck_x = 532 - t * 22
                    if x < min_neck_x or x > max_neck_x:
                        c.putpixel((x, y), (0, 0, 0, 0))

        # Natural 45-degree angled chin shadow with warm subsurface scattering
        chin_apex_x, chin_apex_y = 488, 326
        for y in range(328, 348):
            dy_c = y - chin_apex_y
            sx = chin_apex_x + dy_c * 0.65
            w = max(4.0, 20.0 - dy_c * 0.85)
            vert_factor = 0.76 + 0.22 * (dy_c / 20.0)
            for x in range(int(sx - w), int(sx + w) + 1):
                p = c.getpixel((x, y))
                if p[3] > 0 and p[0] > 150 and p[1] > 100:
                    dist_x = abs(x - sx) / w
                    h_factor = 0.84 + 0.16 * dist_x
                    factor = vert_factor * h_factor
                    nr = min(255, int(p[0] * factor * 1.05))
                    ng = int(p[1] * factor)
                    nb = int(p[2] * factor * 0.95)
                    c.putpixel((x, y), (nr, ng, nb, p[3]))

        # Suprasternal notch (鎖骨窩淺影)
        if is_female:
            for sny in range(354, 362):
                sn_w = (sny - 354) * 0.8
                for snx in range(int(488 - sn_w), int(488 + sn_w) + 1):
                    p = c.getpixel((snx, sny))
                    if p[3] > 0 and p[0] > 140:
                        c.putpixel((snx, sny), (int(p[0] * 0.90), int(p[1] * 0.88), int(p[2] * 0.88), p[3]))

        t_short = 'nat' if tone == 'natural' else 'tan'
        c.save(os.path.join(LAYERS_DIR, f'faces/face_{i:02d}_{t_short}.png'))

# ------------------------------------------------------------------
# 4. Eyes Layer (Layer 7) - Aegyo-sal, Sclera Shadow, Warm Gaze & Refined Lashes
# ------------------------------------------------------------------
print('4. Eyes Layer (Aegyo-sal, watery sparkle, warm focused gaze)...')
eye_cat = Image.open(os.path.join(PHOTOS_DIR, 'eye_styles_14_catalog.jpg'))
eye_cards = [
    # Male 1..6
    ('eye_m01', (29, 132, 333, 230), False),
    ('eye_m02', (359, 132, 663, 230), False),
    ('eye_m03', (690, 132, 994, 230), False),
    ('eye_m04', (29, 350, 333, 448), True),
    ('eye_m05', (359, 350, 663, 448), True),
    ('eye_m06', (690, 350, 994, 448), False),
    # Female 1..8
    ('eye_f01', (29, 623, 254, 719), False),
    ('eye_f02', (275, 623, 501, 719), False),
    ('eye_f03', (522, 623, 748, 719), False),
    ('eye_f04', (768, 623, 994, 719), False),
    ('eye_f05', (29, 842, 255, 937), False),
    ('eye_f06', (275, 842, 501, 937), False),
    ('eye_f07', (522, 842, 748, 937), False),
    ('eye_f08', (768, 842, 994, 937), False),
]

for name, box, is_small in eye_cards:
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
    
    # Specific refinement for eye_f05 (trim spidery lower lashes)
    if name == 'eye_f05':
        for y in range(int(card.height * 0.72), card.height):
            for x in range(card.width):
                p = e_rgba.getpixel((x, y))
                if p[3] > 0 and max(p[:3]) < 90:
                    e_rgba.putpixel((x, y), (0, 0, 0, 0))

    bbox = e_rgba.getbbox()
    if bbox:
        ec = e_rgba.crop(bbox)
        ratio = 120.0 / ec.width
        scaled = ec.resize((int(ec.width * ratio), int(ec.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 480 - scaled.width // 2
        py = 202 - scaled.height // 2
        c.paste(scaled, (px, py), scaled)
        
        # 1. Sclera upper eyelid shadow (cast shadow at top of eyes)
        for y in range(py, py + int(scaled.height * 0.38)):
            for x in range(px, px + scaled.width):
                p = c.getpixel((x, y))
                if p[3] > 0 and min(p[:3]) > 200:
                    c.putpixel((x, y), (int(p[0] * 0.84), int(p[1] * 0.86), int(p[2] * 0.92), p[3]))
        
        # 2. Pupil centers with slight bilateral convergence
        left_cx = 454
        right_cx = 508
        cy = 201
        
        # 3. Sub-surface crescent reflection (月牙反光) at lower iris
        for (pcx, pcy) in [(left_cx, cy), (right_cx, cy)]:
            for dy in range(2, 5):
                for dx in range(-2, 3):
                    p = c.getpixel((pcx + dx, pcy + dy))
                    if p[3] > 0 and max(p[:3]) < 95:
                        c.putpixel((pcx + dx, pcy + dy), (60, 82, 135, 255))
        
        # 4. Specular Catchlights (10 o'clock position on both eyes)
        if is_small:
            for (cx, cy_pt) in [(left_cx, cy), (right_cx, cy)]:
                c.putpixel((cx, cy_pt), (255, 255, 255, 255))
                c.putpixel((cx + 1, cy_pt), (235, 245, 255, 210))
        else:
            for (cx, cy_pt) in [(left_cx, cy), (right_cx, cy)]:
                for dy in range(2):
                    for dx in range(2):
                        c.putpixel((cx + dx, cy_pt + dy), (255, 255, 255, 255))
                c.putpixel((cx + 2, cy_pt + 2), (210, 230, 255, 190))
                c.putpixel((cx - 1, cy_pt + 1), (210, 230, 255, 160))
                
        # 5. Aegyo-sal / Tear Trough (臥蠶陰影 - warm smiling eye curve)
        for (acx, acy, aw) in [(452, 212, 12), (506, 212, 12)]:
            for ax in range(acx - aw, acx + aw + 1):
                curv = math.sin((ax - (acx - aw)) / (2.0 * aw) * math.pi)
                ay = int(acy + curv * 1.5)
                c.putpixel((ax, ay), (170, 115, 105, 110))
                
        c.save(os.path.join(LAYERS_DIR, f'eyes/{name}.png'))

# ------------------------------------------------------------------
# 5. Eyebrows Layer (Layer 8) - Orbital Alignment & Friendly Arch
# ------------------------------------------------------------------
print('5. Eyebrows Layer (Orbital alignment & friendly brow arch)...')
brow_cat = Image.open(os.path.join(PHOTOS_DIR, 'eyebrow_styles_11_catalog.jpg'))
brow_cards = [
    # Male 1..5
    ('brow_m01', (40, 110, 320, 165)),
    ('brow_m02', (350, 110, 630, 165)),
    ('brow_m03', (660, 110, 940, 165)),
    ('brow_m04', (40, 320, 320, 375)),
    ('brow_m05', (350, 320, 630, 375)),
    # Female 1..6
    ('brow_f01', (40, 585, 320, 645)),
    ('brow_f02', (350, 585, 630, 645)),
    ('brow_f03', (660, 585, 940, 645)),
    ('brow_f04', (40, 805, 320, 865)),
    ('brow_f05', (350, 805, 630, 865)),
    ('brow_f06', (660, 805, 940, 865)),
]

for name, box in brow_cards:
    card = brow_cat.crop(box)
    b_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for y in range(card.height):
        if y > 45:
            continue
        for x in range(card.width):
            r, g, b = card.getpixel((x, y))
            if r < 65 and g < 65 and b < 65:
                b_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        ratio = 132.0 / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 480 - scaled.width // 2
        py = 182
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'eyebrows/{name}.png'))

# ------------------------------------------------------------------
# 6. Nose Layer (Layer 6) - Clean Japanese Anime Noses (Aligned with Midline x=480, y=238)
# ------------------------------------------------------------------
print('6. Nose Layer (Clean Japanese anime noses, aligned with midline x=480)...')
def make_nose_01():
    # 01. 小巧點鼻 (Delicate Dot Nose)
    c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    for y in range(233, 237):
        c.putpixel((479, y), (180, 110, 80, 140))
        c.putpixel((480, y), (255, 248, 240, 150))
    c.putpixel((480, 237), (255, 255, 255, 230))
    c.putpixel((479, 237), (145, 75, 55, 210))
    c.putpixel((478, 238), (115, 55, 40, 240))
    c.putpixel((479, 238), (125, 60, 45, 255))
    c.putpixel((480, 238), (160, 95, 75, 200))
    c.putpixel((479, 239), (190, 120, 85, 140))
    c.putpixel((480, 239), (195, 125, 90, 120))
    return c

def make_nose_02():
    # 02. 挺拔直鼻 (Straight High Bridge Nose)
    c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    for y in range(228, 237):
        c.putpixel((479, y), (140, 75, 55, 210))
        c.putpixel((480, y), (255, 250, 245, 170))
    c.putpixel((480, 237), (255, 255, 255, 240))
    c.putpixel((479, 237), (125, 60, 40, 240))
    c.putpixel((477, 238), (110, 50, 35, 230))
    c.putpixel((478, 238), (105, 45, 30, 255))
    c.putpixel((479, 238), (115, 55, 38, 255))
    c.putpixel((480, 238), (150, 85, 65, 210))
    for x in range(478, 482):
        c.putpixel((x, 239), (180, 110, 75, 150))
    return c

def make_nose_03():
    # 03. 微翹水滴鼻 (Upturned Teardrop Nose)
    c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    for y in range(232, 236):
        c.putpixel((479, y), (175, 105, 75, 140))
        c.putpixel((480, y), (255, 248, 242, 140))
    c.putpixel((479, 236), (255, 255, 255, 220))
    c.putpixel((480, 236), (255, 255, 255, 200))
    c.putpixel((478, 237), (135, 68, 48, 220))
    c.putpixel((479, 237), (120, 58, 40, 240))
    c.putpixel((480, 237), (140, 75, 55, 210))
    c.putpixel((481, 237), (180, 110, 85, 150))
    for x in range(478, 481):
        c.putpixel((x, 238), (190, 120, 85, 130))
    return c

def make_nose_04():
    # 04. 寬實肉鼻 (Button / Rounded Nose)
    c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    for y in range(233, 236):
        c.putpixel((479, y), (190, 125, 95, 130))
        c.putpixel((480, y), (255, 248, 240, 140))
    c.putpixel((479, 236), (255, 255, 255, 210))
    c.putpixel((480, 236), (255, 255, 255, 210))
    c.putpixel((476, 237), (145, 78, 55, 200))
    c.putpixel((477, 237), (115, 55, 38, 240))
    c.putpixel((478, 237), (120, 60, 42, 240))
    c.putpixel((479, 237), (130, 68, 48, 240))
    c.putpixel((480, 237), (125, 62, 44, 240))
    c.putpixel((481, 237), (118, 56, 40, 240))
    c.putpixel((482, 237), (145, 78, 55, 200))
    for x in range(477, 482):
        c.putpixel((x, 238), (185, 115, 80, 140))
    return c

make_nose_01().save(os.path.join(LAYERS_DIR, 'noses/nose_01.png'))
make_nose_02().save(os.path.join(LAYERS_DIR, 'noses/nose_02.png'))
make_nose_03().save(os.path.join(LAYERS_DIR, 'noses/nose_03.png'))
make_nose_04().save(os.path.join(LAYERS_DIR, 'noses/nose_04.png'))

# ------------------------------------------------------------------
# 7. Mouth Layer (Layer 5) - Philtrum Dip, Oral Cavity Teeth Depth & Lip Gloss
# ------------------------------------------------------------------
print('7. Mouth Layer (Philtrum dip, oral cavity depth & lip gloss)...')
mouth_cat = Image.open(os.path.join(PHOTOS_DIR, 'mouth_styles_6_catalog.jpg'))
mouth_cards = [
    ('mouth_01', (105, 275, 275, 345)),
    ('mouth_02', (415, 275, 585, 345)),
    ('mouth_03', (725, 275, 895, 345)),
    ('mouth_04', (105, 680, 275, 750)),
    ('mouth_05', (415, 680, 585, 750)),
    ('mouth_06', (725, 680, 895, 750)),
]

for name, box in mouth_cards:
    sub = mouth_cat.crop(box)
    m_rgba = Image.new('RGBA', sub.size, (0, 0, 0, 0))
    for y in range(sub.height):
        for x in range(sub.width):
            r, g, b = sub.getpixel((x, y))
            is_line = (r < 115 and g < 65 and b < 65)
            is_teeth = (r > 240 and g > 240 and b > 240)
            is_lip = (r > 190 and g < 155 and b < 140 and r > g + 40)
            if is_line or is_teeth or is_lip:
                m_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = m_rgba.getbbox()
    if bbox:
        mc = m_rgba.crop(bbox)
        ratio = 56.0 / mc.width
        scaled = mc.resize((int(mc.width * ratio), int(mc.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 480 - scaled.width // 2
        py = 274
        c.paste(scaled, (px, py), scaled)
        
        # Subtle philtrum dip shadow above upper lip
        for fpy in range(268, 273):
            c.putpixel((480, fpy), (170, 110, 95, 140))
            
        # Refine mouth_01 (sweet smile): Add lower lip gloss
        if name == 'mouth_01':
            c.putpixel((480, py + scaled.height - 2), (255, 235, 235, 220))
            c.putpixel((481, py + scaled.height - 2), (255, 235, 235, 220))
            
        # Refine mouth_03 (calm professional smile): upturn corners slightly
        if name == 'mouth_03':
            c.putpixel((px + 1, py + 1), (110, 45, 45, 200))
            c.putpixel((px + scaled.width - 2, py + 1), (110, 45, 45, 200))
            
        # Refine mouth_02 (open teeth smile) to avoid "clenched fake teeth"
        if name == 'mouth_02':
            # Dark oral cavity corners on left and right
            for my in range(py + 7, py + 16):
                for mx in range(px + 2, px + 9):
                    p = c.getpixel((mx, my))
                    if p[3] > 0 and min(p[:3]) > 175:
                        c.putpixel((mx, my), (115, 28, 32, 255))
                for mx in range(px + scaled.width - 9, px + scaled.width - 2):
                    p = c.getpixel((mx, my))
                    if p[3] > 0 and min(p[:3]) > 175:
                        c.putpixel((mx, my), (115, 28, 32, 255))
            # Upper lip shadow across top of teeth
            for my in range(py + 7, py + 11):
                for mx in range(px + 9, px + scaled.width - 9):
                    p = c.getpixel((mx, my))
                    if p[3] > 0 and min(p[:3]) > 195:
                        c.putpixel((mx, my), (210, 192, 192, 255))
            # Center incisor tooth separation line
            c.putpixel((480, py + 10), (185, 160, 160, 240))
            c.putpixel((480, py + 11), (185, 160, 160, 240))
            # Lower lip highlight glint
            c.putpixel((480, py + scaled.height - 2), (255, 238, 238, 210))
            c.putpixel((481, py + scaled.height - 2), (255, 238, 238, 210))
            
        c.save(os.path.join(LAYERS_DIR, f'mouths/{name}.png'))

# ------------------------------------------------------------------
# 8. Bangs Layer (Layer 9) - Tapered Strands, Balanced Skull & High Cranial Dome
# ------------------------------------------------------------------
print('8. Bangs Layer (Tapered hair tips, skull balance & high cranial dome)...')
bangs_cat = Image.open(os.path.join(PHOTOS_DIR, 'bangs_16_catalog.jpg'))
bang_cards = [
    # Male 1..6
    ('bang_01', (130, 60, 285, 230), 235),
    ('bang_02', (415, 60, 575, 230), 235),
    ('bang_03', (695, 60, 876, 230), 248),
    ('bang_04', (135, 280, 290, 450), 235),
    ('bang_05', (415, 280, 585, 450), 238),
    ('bang_06', (710, 280, 865, 450), 235),
    # Female 1..10
    ('bang_07', (38, 542, 208, 715), 245),
    ('bang_08', (222, 542, 402, 735), 245),
    ('bang_09', (425, 542, 585, 715), 235),
    ('bang_10', (615, 542, 780, 715), 235),
    ('bang_11', (805, 542, 975, 715), 240),
    ('bang_12', (42, 770, 205, 945), 235),
    ('bang_13', (228, 770, 398, 945), 240),
    ('bang_14', (420, 770, 585, 945), 240),
    ('bang_15', (610, 770, 775, 945), 240),
    ('bang_16', (805, 770, 970, 945), 235),
]

for name, box, target_w in bang_cards:
    card = bangs_cat.crop(box)
    dark_pixels = set()
    for y in range(card.height):
        if y < 14: continue
        if name == 'bang_08' and y >= card.height - 3: continue
        for x in range(card.width):
            if y < 35 and x < 35: continue
            p = card.getpixel((x, y))
            # skip mannequin ear outline
            if 130 <= x <= 165 and 105 <= y <= 150 and max(p) > 60:
                continue
            # skip neck line at bottom
            if y > 115 and x < 128 and max(p) > 50:
                continue
            # skip center face
            if 0.38 * card.width < x < 0.62 * card.width and y > 0.55 * card.height:
                continue
            # Specifically for bang_05: skip the weird external growth curl on right cheek
            if name == 'bang_05' and x > 135 and y > 100:
                continue
            if max(p) < 140:
                dark_pixels.add((x, y))

    visited = set()
    components = []
    for (x, y) in dark_pixels:
        if (x, y) not in visited:
            comp = []
            q = deque([(x, y)])
            visited.add((x, y))
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0: continue
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) in dark_pixels and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            q.append((nx, ny))
            components.append(comp)

    if not components:
        continue
    components.sort(key=lambda c: len(c), reverse=True)
    main_comp = components[0]

    b_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for (x, y) in main_comp:
        r, g, b = card.getpixel((x, y))
        b_rgba.putpixel((x, y), (r, g, b, 255))

    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        ratio = float(target_w) / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.NEAREST)
        
        c_black = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 480 - scaled.width // 2
        py = 25 # High cranial dome!
        c_black.paste(scaled, (px, py), scaled)
        
        # Clean any remaining stray bits on bang_05 cheek and balance skull
        if name == 'bang_05':
            for cy in range(180, 245):
                for cx in range(536, 600):
                    c_black.putpixel((cx, cy), (0, 0, 0, 0))
                    
        # Refine bang_03 (Character B comma bangs): soften the heavy slug tip
        if name == 'bang_03':
            for cy in range(178, 192):
                for cx in range(458, 468):
                    p = c_black.getpixel((cx, cy))
                    if p[3] > 0 and (cx < 462 or cy > 186):
                        c_black.putpixel((cx, cy), (0, 0, 0, 0))
                        
        # Refine bang_08 (Character A French bangs): remove inner flat neck block and taper tips
        if name == 'bang_08':
            for cy in range(246, 268):
                for cx in range(370, 440):
                    p = c_black.getpixel((cx, cy))
                    if p[3] == 0: continue
                    if cx > 405 + (264 - cy) * 1.6:
                        c_black.putpixel((cx, cy), (0, 0, 0, 0))
        
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'bangs/{name}_black.png'))
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'bangs/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 9. Back Hair Layer (Layer 2) - Balanced Undercut Texture & High Cranial Matching
# ------------------------------------------------------------------
print('9. Back Hair Layer (Balanced undercut texture & high cranial matching)...')
back_cat = Image.open(os.path.join(PHOTOS_DIR, 'back_hair_front_view_catalog.jpg'))
back_cards = [
    # Row 0
    ('back_01_mid_bun', (50, 55, 255, 315), 220),
    ('back_02_low_bun', (290, 90, 485, 315), 220),
    ('back_03_bob_cut', (525, 90, 715, 315), 220),
    ('back_04_claw_clip', (755, 65, 965, 315), 220),
    # Row 1
    ('back_05_high_pony', (60, 395, 280, 625), 220),
    ('back_06_low_pony', (295, 410, 500, 625), 220),
    ('back_07_undercut', (530, 410, 705, 625), 230),
    # Row 2
    ('back_08_wavy_bob', (50, 705, 260, 940), 220),
    ('back_09_half_up', (530, 680, 715, 940), 220),
    ('back_10_layered_pixie', (750, 705, 950, 940), 232),
]

for name, box, target_w in back_cards:
    card = back_cat.crop(box)
    rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for y in range(card.height):
        for x in range(card.width):
            p = card.getpixel((x, y))
            if y > 185: continue
            if 128 <= x <= 165 and 100 <= y <= 155 and max(p) > 60: continue
            if x < 45 and y > 95 and max(p) > 55: continue
            if max(p) < 135:
                rgba.putpixel((x, y), (p[0], p[1], p[2], 255))
    bbox = rgba.getbbox()
    if bbox:
        bc = rgba.crop(bbox)
        ratio = float(target_w) / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.NEAREST)
        
        c_black = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 480 - scaled.width // 2
        py = 26 # Matching cranial dome!
        c_black.paste(scaled, (px, py), scaled)
        
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_black.png'))
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 10. Accessories Layer (Layer 10) - Pure Optical Anti-Glare Japanese Glasses
# ------------------------------------------------------------------
print('10. Accessories Layer (Pure optical anti-glare anime glasses)...')
acc_sq = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_sq = ImageDraw.Draw(acc_sq)

left_box = [(426, 185), (476, 215)]
right_box = [(486, 185), (536, 215)]

# 1. Subtle transparent anti-glare sky-blue lens tint
d_sq.rounded_rectangle(left_box, radius=3, fill=(215, 235, 255, 24))
d_sq.rounded_rectangle(right_box, radius=3, fill=(215, 235, 255, 24))

# 2. Outer dark acetate frame
d_sq.rounded_rectangle(left_box, radius=3, outline=(35, 35, 42, 255), width=3)
d_sq.rounded_rectangle(right_box, radius=3, outline=(35, 35, 42, 255), width=3)

# 3. Top frame subtle metallic edge reflection
d_sq.line([(428, 185), (474, 185)], fill=(115, 120, 135, 255), width=1)
d_sq.line([(488, 185), (534, 185)], fill=(115, 120, 135, 255), width=1)

# 4. Arched nose bridge resting above nose tip (y=191, clear of pupil at y=201)
d_sq.line([(476, 191), (486, 191)], fill=(35, 35, 42, 255), width=3)
d_sq.line([(476, 190), (486, 190)], fill=(115, 120, 135, 255), width=1)

# 5. Temples going back to ears
d_sq.line([(426, 193), (405, 195)], fill=(35, 35, 42, 255), width=3)
d_sq.line([(536, 193), (555, 195)], fill=(35, 35, 42, 255), width=3)
acc_sq.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_square.png'))

acc_rd = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_rd = ImageDraw.Draw(acc_rd)
d_rd.ellipse([(426, 184), (476, 218)], fill=(215, 235, 255, 22), outline=(175, 145, 85, 255), width=3)
d_rd.ellipse([(486, 184), (536, 218)], fill=(215, 235, 255, 22), outline=(175, 145, 85, 255), width=3)
d_rd.arc([(476, 192), (486, 202)], start=180, end=360, fill=(175, 145, 85, 255), width=3)
d_rd.line([(426, 198), (405, 196)], fill=(175, 145, 85, 255), width=3)
d_rd.line([(536, 198), (555, 196)], fill=(175, 145, 85, 255), width=3)
acc_rd.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_round.png'))

print('All 10 layers rebuilt with v138 Ultimate Aesthetic Architecture!')
