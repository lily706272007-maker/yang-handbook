import os, sys, math
from PIL import Image, ImageDraw, ImageFilter
from collections import deque

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')

for sub in ['bg', 'body', 'faces', 'mouths', 'noses', 'eyes', 'eyebrows', 'bangs', 'back_hair', 'accessories']:
    os.makedirs(os.path.join(LAYERS_DIR, sub), exist_ok=True)

# ------------------------------------------------------------------
# Palette swapping helper functions with Angel Ring sheen
# ------------------------------------------------------------------
def to_flaxen_brown(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    # Japanese rich milky ash-brown with warm caramel sheen
    nr = int(48 + ratio * (232 - 48))
    ng = int(34 + ratio * (198 - 34))
    nb = int(24 + ratio * (162 - 24))
    if ratio > 0.55:
        sheen = (ratio - 0.55) / 0.45
        nr = min(255, int(nr + sheen * 22))
        ng = min(255, int(ng + sheen * 18))
        nb = min(255, int(nb + sheen * 12))
    return nr, ng, nb, a

def to_natural_black(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    # Deep crisp anime slate-indigo black
    nr = int(10 + ratio * (85 - 10))
    ng = int(12 + ratio * (95 - 12))
    nb = int(18 + ratio * (125 - 18))
    if ratio > 0.55:
        sheen = (ratio - 0.55) / 0.45
        nb = min(255, int(nb + sheen * 24))
        ng = min(255, int(ng + sheen * 12))
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
# 2. Body Layers (Layer 3) - Enhanced collar lapel & rim highlights
# ------------------------------------------------------------------
print('2. Body Layers (FLIP_LEFT_RIGHT & unified collar alignment)...')
body_configs = [
    ('body_layer_male_normal.png', 'body_male_normal.png', 260, False),
    ('body_layer_male_sturdy.png', 'body_male_sturdy.png', 200, True),
    ('body_layer_female_normal.png', 'body_female_normal.png', 208, False),
    ('body_layer_female_chubby.png', 'body_female_chubby.png', 152, True)
]

for src_name, out_name, dy, clean_stub in body_configs:
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
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        c.paste(flipped, (0, dy), flipped)
        
        # Add subtle navy-charcoal warmth and lapel rim highlights
        for y in range(dy, min(1024, dy + flipped.height)):
            for x in range(1024):
                p = c.getpixel((x, y))
                if p[3] == 0: continue
                # Slightly tint dark suit pixels towards rich charcoal-navy
                if max(p[:3]) < 70 and p[0] == p[1] == p[2]:
                    c.putpixel((x, y), (p[0], p[1] + 2, p[2] + 6, p[3]))
        
        c.save(os.path.join(LAYERS_DIR, 'body', out_name))

# ------------------------------------------------------------------
# 3. Face Shapes (Layer 4) - Slender Female Neck, Natural 45deg Chin Shadow, Peach Blush
# ------------------------------------------------------------------
print('3. Face Shapes (10 natural + 10 tan clean bases with slender neck, natural chin shadow & peach blush)...')
for i in range(1, 11):
    is_female = (i in [1, 2, 3, 7, 8, 9, 10])
    for tone in ['natural', 'tan']:
        f_path = os.path.join(PHOTOS_DIR, f'faces/face_{i:02d}_{tone}.jpg')
        if not os.path.exists(f_path):
            continue
        fim = Image.open(f_path)
        hc = fim.crop((10, 15, 258, 355)).convert('RGBA')
        skin_color = hc.getpixel((140, 210))
        
        # Smooth nose
        for y in range(185, 231):
            for x in range(72, 115):
                p = hc.getpixel((x, y))
                if p[0] > skin_color[0] + 4 or p[0] < skin_color[0] - 6 or p[1] < skin_color[1] - 6:
                    hc.putpixel((x, y), skin_color)
                    
        # Smooth mouth
        for y in range(231, 255):
            for x in range(80, 130):
                p = hc.getpixel((x, y))
                if p[0] > skin_color[0] + 4 or p[0] < skin_color[0] - 6 or p[1] < skin_color[1] - 6:
                    hc.putpixel((x, y), skin_color)
                    
        # Extract transparent background
        head_rgba = Image.new('RGBA', hc.size, (0, 0, 0, 0))
        for y in range(hc.height):
            for x in range(hc.width):
                r, g, b, _ = hc.getpixel((x, y))
                is_skin_or_line = (r > b + 18) or (r < 100 and g < 100 and b < 100)
                if is_skin_or_line:
                    head_rgba.putpixel((x, y), (r, g, b, 255))
                    
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        c.paste(head_rgba, (380, 40), head_rgba)
        
        # Taper neck: Slender swan neck for females, sturdy neck for males
        for y in range(320, c.height):
            for x in range(c.width):
                p = c.getpixel((x, y))
                if p[3] == 0: continue
                if y > 362:
                    c.putpixel((x, y), (0, 0, 0, 0))
                elif y > 328:
                    t = (y - 328) / (362.0 - 328.0)
                    if is_female:
                        min_x = 458 + t * 27
                        max_x = 522 - t * 15
                    else:
                        min_x = 448 + t * 37
                        max_x = 532 - t * 22
                    if x < min_x or x > max_x:
                        c.putpixel((x, y), (0, 0, 0, 0))

        # Natural 45-degree angled chin shadow (projected from chin to throat)
        # Avoids horizontal band / strangulation mark
        chin_apex_x, chin_apex_y = 488, 326
        for y in range(328, 348):
            dy_c = y - chin_apex_y
            sx = chin_apex_x + dy_c * 0.65
            w = max(4.0, 22.0 - dy_c * 0.9)
            vert_factor = 0.72 + 0.26 * (dy_c / 22.0)
            for x in range(int(sx - w), int(sx + w) + 1):
                p = c.getpixel((x, y))
                if p[3] > 0 and p[0] > 150 and p[1] > 100:
                    dist_x = abs(x - sx) / w
                    h_factor = 0.82 + 0.18 * dist_x
                    factor = vert_factor * h_factor
                    c.putpixel((x, y), (int(p[0] * factor), int(p[1] * factor), int(p[2] * factor), p[3]))

        # Peach blush on cheeks (healthy glow / 氣色)
        blush_color = (255, 125, 115) if tone == 'natural' else (245, 130, 95)
        blush_intensity = 0.22 if is_female else 0.12
        # Left cheek (436, 228), right cheek (506, 230)
        for (cx, cy, rx, ry) in [(436, 228, 16, 10), (506, 230, 16, 10)]:
            for by in range(cy - ry, cy + ry + 1):
                for bx in range(cx - rx, cx + rx + 1):
                    d = ((bx - cx) / rx)**2 + ((by - cy) / ry)**2
                    if d <= 1.0:
                        alpha_w = (1.0 - d) * blush_intensity
                        p = c.getpixel((bx, by))
                        if p[3] > 0 and p[0] > 160:
                            nr = int(p[0] * (1.0 - alpha_w) + blush_color[0] * alpha_w)
                            ng = int(p[1] * (1.0 - alpha_w) + blush_color[1] * alpha_w)
                            nb = int(p[2] * (1.0 - alpha_w) + blush_color[2] * alpha_w)
                            c.putpixel((bx, by), (nr, ng, nb, p[3]))

        t_short = 'nat' if tone == 'natural' else 'tan'
        c.save(os.path.join(LAYERS_DIR, f'faces/face_{i:02d}_{t_short}.png'))

# ------------------------------------------------------------------
# 4. Eyes Layer (Layer 7) - Watery Catchlights, Sclera Shadow, Crescent Glow & Convergence
# ------------------------------------------------------------------
print('4. Eyes Layer (14 styles with watery catchlights, sclera shadow & crescent glow)...')
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
        for y in range(int(card.height * 0.74), card.height):
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
                if p[3] > 0 and min(p[:3]) > 200: # sclera
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
        
        # 4. Specular Catchlights (Primary star sparkle + soft secondary glint)
        if is_small:
            for (cx, cy_pt) in [(left_cx, cy), (right_cx, cy)]:
                c.putpixel((cx, cy_pt), (255, 255, 255, 255))
                c.putpixel((cx + 1, cy_pt), (235, 245, 255, 210))
        else:
            for (cx, cy_pt) in [(left_cx, cy), (right_cx, cy)]:
                # 2x2 primary bright sparkle
                for dy in range(2):
                    for dx in range(2):
                        c.putpixel((cx + dx, cy_pt + dy), (255, 255, 255, 255))
                # secondary soft sparkle
                c.putpixel((cx + 2, cy_pt + 2), (210, 230, 255, 190))
                c.putpixel((cx - 1, cy_pt + 1), (210, 230, 255, 160))
                
        c.save(os.path.join(LAYERS_DIR, f'eyes/{name}.png'))

# ------------------------------------------------------------------
# 5. Eyebrows Layer (Layer 8) - Moved Down 8px to orbital rim
# ------------------------------------------------------------------
print('5. Eyebrows Layer (11 styles moved down 8px to orbit)...')
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
        py = 182 # Down 8px from 174, perfect match with orbital ridge!
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'eyebrows/{name}.png'))

# ------------------------------------------------------------------
# 6. Nose Layer (Layer 6) - L-Shaped Anime Nose with Bridge Highlight & Soft Subnasal Shadow
# ------------------------------------------------------------------
print('6. Nose Layer (4 styles with bridge highlight & soft subnasal shadow)...')
nose_cat = Image.open(os.path.join(PHOTOS_DIR, 'nose_styles_4_catalog.jpg'))
nose_cards = [
    ('nose_01', (180, 220, 370, 420)),
    ('nose_02', (650, 220, 840, 420)),
    ('nose_03', (180, 660, 370, 860)),
    ('nose_04', (650, 660, 840, 860)),
]

for name, box in nose_cards:
    sub = nose_cat.crop(box)
    n_rgba = Image.new('RGBA', sub.size, (0, 0, 0, 0))
    for y in range(sub.height):
        for x in range(sub.width):
            r, g, b = sub.getpixel((x, y))
            if r > 150 and g < 130 and b > 105:
                continue
            is_outline = (r < 110 and g < 65 and b < 60)
            is_shadow = (r < 165 and g < 115 and b < 95 and r > b + 35)
            is_highlight = (r > 248 and g > 240 and b > 230)
            if is_outline or is_shadow or is_highlight:
                n_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = n_rgba.getbbox()
    if bbox:
        nc = n_rgba.crop(bbox)
        ratio = 30.0 / nc.width
        scaled = nc.resize((int(nc.width * ratio), int(nc.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 468
        py = 232
        c.paste(scaled, (px, py), scaled)
        
        # Subtle warm nose bridge highlight
        for by in range(224, 235):
            c.putpixel((480, by), (255, 246, 240, 160))
        # Crisp nose tip highlight point
        c.putpixel((481, 236), (255, 255, 255, 220))
        c.putpixel((482, 236), (255, 255, 255, 180))
        
        # Soften sub-nasal shadow to warm amber-brown, removing ink blob
        for sy in range(238, 242):
            for sx in range(478, 484):
                p = c.getpixel((sx, sy))
                if p[3] > 0 and max(p[:3]) < 70:
                    c.putpixel((sx, sy), (145, 95, 75, 210))
                    
        c.save(os.path.join(LAYERS_DIR, f'noses/{name}.png'))

# ------------------------------------------------------------------
# 7. Mouth Layer (Layer 5) - Up 8px, Philtrum Dip, Oral Cavity Corners for Smile
# ------------------------------------------------------------------
print('7. Mouth Layer (6 styles, up 8px with oral cavity depth)...')
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
        py = 274 # Up 8px from 282, golden ratio 1:2 lower face balance!
        c.paste(scaled, (px, py), scaled)
        
        # Subtle philtrum dip shadow above upper lip
        for fpy in range(268, 273):
            c.putpixel((480, fpy), (170, 110, 95, 140))
            
        # Refine mouth_02 (open teeth smile) to avoid "clenched fake teeth"
        if name == 'mouth_02':
            # Dark oral cavity corners on left and right
            for my in range(py + 8, py + 16):
                for mx in range(px + 2, px + 8):
                    p = c.getpixel((mx, my))
                    if p[3] > 0 and min(p[:3]) > 180:
                        c.putpixel((mx, my), (115, 30, 35, 255))
                for mx in range(px + scaled.width - 8, px + scaled.width - 2):
                    p = c.getpixel((mx, my))
                    if p[3] > 0 and min(p[:3]) > 180:
                        c.putpixel((mx, my), (115, 30, 35, 255))
            # Upper lip shadow across top of teeth
            for my in range(py + 8, py + 11):
                for mx in range(px + 8, px + scaled.width - 8):
                    p = c.getpixel((mx, my))
                    if p[3] > 0 and min(p[:3]) > 200:
                        c.putpixel((mx, my), (210, 195, 195, 255))
            # Lower lip highlight glint
            c.putpixel((480, py + scaled.height - 2), (255, 235, 235, 200))
            c.putpixel((481, py + scaled.height - 2), (255, 235, 235, 200))
            
        c.save(os.path.join(LAYERS_DIR, f'mouths/{name}.png'))

# ------------------------------------------------------------------
# 8. Bangs Layer (Layer 9) - High Cranial Vault, Angel Ring Sheen & Clean Cheek Contours
# ------------------------------------------------------------------
print('8. Bangs Layer (16 styles x 2 colors, high cranial vault & angel ring)...')
bangs_cat = Image.open(os.path.join(PHOTOS_DIR, 'bangs_16_catalog.jpg'))
bang_cards = [
    # Male 1..6
    ('bang_01', (130, 60, 285, 230), 235),
    ('bang_02', (415, 60, 575, 230), 235),
    ('bang_03', (695, 60, 876, 230), 248),
    ('bang_04', (135, 280, 290, 450), 235),
    ('bang_05', (415, 280, 585, 450), 235),
    ('bang_06', (710, 280, 865, 450), 235),
    # Female 1..10
    ('bang_07', (38, 542, 208, 715), 245),
    ('bang_08', (222, 542, 402, 726), 245),
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
        py = 26 # Up 8px from 34, creating fluffy high cranial vault!
        c_black.paste(scaled, (px, py), scaled)
        
        # Clean any remaining stray bits on bang_05 cheek
        if name == 'bang_05':
            for cy in range(180, 245):
                for cx in range(538, 600):
                    c_black.putpixel((cx, cy), (0, 0, 0, 0))
        
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'bangs/{name}_black.png'))
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'bangs/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 9. Back Hair Layer (Layer 2) - High Cranial Matching & Clean Silhouette
# ------------------------------------------------------------------
print('9. Back Hair Layer (10 styles x 2 colors, matching cranial height)...')
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
    ('back_10_layered_pixie', (750, 705, 950, 940), 230),
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
        py = 27 # Up 8px to match bangs high cranial dome!
        c_black.paste(scaled, (px, py), scaled)
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_black.png'))
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 10. Accessories Layer (Layer 10) - High-Tech Transparent Japanese Anime Glasses
# ------------------------------------------------------------------
print('10. Accessories Layer (Transparent sky-blue reflection lenses)...')
acc_sq = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_sq = ImageDraw.Draw(acc_sq)

left_box = [(426, 185), (476, 215)]
right_box = [(486, 185), (536, 215)]

# 1. Semi-transparent sky-blue glass lens
d_sq.rounded_rectangle(left_box, radius=3, fill=(215, 235, 255, 32))
d_sq.rounded_rectangle(right_box, radius=3, fill=(215, 235, 255, 32))

# 2. Diagonal glass sheen / glare lines
d_sq.line([(434, 187), (446, 213)], fill=(255, 255, 255, 65), width=2)
d_sq.line([(494, 187), (506, 213)], fill=(255, 255, 255, 65), width=2)

# 3. Outer dark acetate frame
d_sq.rounded_rectangle(left_box, radius=3, outline=(35, 35, 42, 255), width=3)
d_sq.rounded_rectangle(right_box, radius=3, outline=(35, 35, 42, 255), width=3)

# 4. Top frame subtle rim highlight
d_sq.line([(428, 185), (474, 185)], fill=(110, 115, 130, 255), width=1)
d_sq.line([(488, 185), (534, 185)], fill=(110, 115, 130, 255), width=1)

# 5. Arched nose bridge resting above nose tip (y=191, clear of pupil at y=201)
d_sq.line([(476, 191), (486, 191)], fill=(35, 35, 42, 255), width=3)
d_sq.line([(476, 190), (486, 190)], fill=(110, 115, 130, 255), width=1)

# 6. Temples going back to ears
d_sq.line([(426, 193), (405, 195)], fill=(35, 35, 42, 255), width=3)
d_sq.line([(536, 193), (555, 195)], fill=(35, 35, 42, 255), width=3)
acc_sq.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_square.png'))

acc_rd = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_rd = ImageDraw.Draw(acc_rd)
d_rd.ellipse([(426, 184), (476, 218)], fill=(215, 235, 255, 28), outline=(175, 145, 85, 255), width=3)
d_rd.ellipse([(486, 184), (536, 218)], fill=(215, 235, 255, 28), outline=(175, 145, 85, 255), width=3)
d_rd.line([(435, 187), (447, 215)], fill=(255, 255, 255, 60), width=2)
d_rd.line([(495, 187), (507, 215)], fill=(255, 255, 255, 60), width=2)
d_rd.arc([(476, 192), (486, 202)], start=180, end=360, fill=(175, 145, 85, 255), width=3)
d_rd.line([(426, 198), (405, 196)], fill=(175, 145, 85, 255), width=3)
d_rd.line([(536, 198), (555, 196)], fill=(175, 145, 85, 255), width=3)
acc_rd.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_round.png'))

print('All 10 layers rebuilt with v137 Ultimate Aesthetic Architecture!')
