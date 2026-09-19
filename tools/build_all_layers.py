import os, sys
from PIL import Image, ImageDraw, ImageFilter
from collections import deque

WORKSPACE = '/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa'
LAYERS_DIR = os.path.join(WORKSPACE, 'photos/layers')
PHOTOS_DIR = os.path.join(WORKSPACE, 'photos')

for sub in ['bg', 'body', 'faces', 'mouths', 'noses', 'eyes', 'eyebrows', 'bangs', 'back_hair', 'accessories']:
    os.makedirs(os.path.join(LAYERS_DIR, sub), exist_ok=True)

# ------------------------------------------------------------------
# Palette swapping helper functions
# ------------------------------------------------------------------
def to_flaxen_brown(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    nr = int(45 + ratio * (215 - 45))
    ng = int(32 + ratio * (192 - 32))
    nb = int(20 + ratio * (158 - 20))
    return nr, ng, nb, a

def to_natural_black(r, g, b, a):
    if a < 30:
        return 0, 0, 0, 0
    v = max(r, g, b) / 255.0
    ratio = min(1.0, max(0.0, (v - 0.05) / 0.40))
    nr = int(12 + ratio * (95 - 12))
    ng = int(12 + ratio * (98 - 12))
    nb = int(15 + ratio * (110 - 15))
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
# 2. Body Layers (Layer 3) - Standardized collar alignment
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
        c.save(os.path.join(LAYERS_DIR, 'body', out_name))

# ------------------------------------------------------------------
# 3. Face Shapes (Layer 4) - Tapered Neck & 3D Chin Contact Shadow
# ------------------------------------------------------------------
print('3. Face Shapes (10 natural + 10 tan clean smooth bases with tapered neck & chin shadow)...')
for i in range(1, 11):
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
        
        # Taper neck so it tucks gracefully into the collar V opening
        for y in range(320, c.height):
            for x in range(c.width):
                p = c.getpixel((x, y))
                if p[3] == 0: continue
                if y > 362:
                    c.putpixel((x, y), (0, 0, 0, 0))
                elif y > 328:
                    t = (y - 328) / (362.0 - 328.0)
                    min_x = 445 + t * 40
                    max_x = 535 - t * 25
                    if x < min_x or x > max_x:
                        c.putpixel((x, y), (0, 0, 0, 0))

        # Add 3D chin contact shadow on throat
        for y in range(330, 345):
            factor = 0.68 + 0.30 * ((y - 330) / 15.0)
            for x in range(458, 522):
                p = c.getpixel((x, y))
                if p[3] > 0 and (p[0] > 160 and p[1] > 110):
                    c.putpixel((x, y), (int(p[0]*factor), int(p[1]*factor), int(p[2]*factor), p[3]))

        t_short = 'nat' if tone == 'natural' else 'tan'
        c.save(os.path.join(LAYERS_DIR, f'faces/face_{i:02d}_{t_short}.png'))

# ------------------------------------------------------------------
# 4. Eyes Layer (Layer 7) - Crisp with Specular Glint Catchlights
# ------------------------------------------------------------------
print('4. Eyes Layer (14 styles with catchlights)...')
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
            is_sclera = (r > 220 and g > 220 and b > 220 and abs(r - b) < 18)
            is_dark = (r < 140 and g < 100 and b < 100) or (max(r, g, b) < 90)
            is_highlight = (r > 245 and g > 245 and b > 245)
            if is_sclera or is_dark or is_highlight:
                e_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = e_rgba.getbbox()
    if bbox:
        ec = e_rgba.crop(bbox)
        ratio = 120.0 / ec.width
        scaled = ec.resize((int(ec.width * ratio), int(ec.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 480 - scaled.width // 2
        py = 202 - scaled.height // 2
        c.paste(scaled, (px, py), scaled)
        
        # Add catchlights
        if is_small:
            for (cx, cy) in [(454, 202), (508, 202)]:
                c.putpixel((cx, cy), (255, 255, 255, 255))
                c.putpixel((cx+1, cy), (240, 240, 255, 220))
        else:
            for (cx, cy) in [(453, 201), (509, 201)]:
                for dy in range(2):
                    for dx in range(2):
                        c.putpixel((cx + dx, cy + dy), (255, 255, 255, 255))
                c.putpixel((cx - 1, cy + 2), (210, 225, 255, 180))
                
        c.save(os.path.join(LAYERS_DIR, f'eyes/{name}.png'))

# ------------------------------------------------------------------
# 5. Eyebrows Layer (Layer 8)
# ------------------------------------------------------------------
print('5. Eyebrows Layer (11 styles)...')
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
        py = 174
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'eyebrows/{name}.png'))

# ------------------------------------------------------------------
# 6. Nose Layer (Layer 6)
# ------------------------------------------------------------------
print('6. Nose Layer (4 styles)...')
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
        c.save(os.path.join(LAYERS_DIR, f'noses/{name}.png'))

# ------------------------------------------------------------------
# 7. Mouth Layer (Layer 5)
# ------------------------------------------------------------------
print('7. Mouth Layer (6 styles)...')
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
        py = 282
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'mouths/{name}.png'))

# ------------------------------------------------------------------
# 8. Bangs Layer (Layer 9) - Full Cranial Coverage & Connected Components
# ------------------------------------------------------------------
print('8. Bangs Layer (16 styles x 2 colors via connected components)...')
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
        py = 34
        c_black.paste(scaled, (px, py), scaled)
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'bangs/{name}_black.png'))
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'bangs/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 9. Back Hair Layer (Layer 2) - Clean Head Silhouette
# ------------------------------------------------------------------
print('9. Back Hair Layer (10 styles x 2 colors)...')
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
        py = 35
        c_black.paste(scaled, (px, py), scaled)
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_black.png'))
        
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'back_hair/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 10. Accessories Layer (Layer 10)
# ------------------------------------------------------------------
print('10. Accessories Layer...')
acc_sq = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_sq = ImageDraw.Draw(acc_sq)
d_sq.rounded_rectangle([(430, 192), (475, 218)], radius=4, outline=(40, 40, 45, 255), width=3)
d_sq.rounded_rectangle([(490, 192), (535, 218)], radius=4, outline=(40, 40, 45, 255), width=3)
d_sq.line([(475, 202), (490, 202)], fill=(40, 40, 45, 255), width=3)
d_sq.line([(430, 200), (415, 196)], fill=(40, 40, 45, 255), width=3)
d_sq.line([(535, 200), (560, 196)], fill=(40, 40, 45, 255), width=3)
acc_sq.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_square.png'))

acc_rd = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_rd = ImageDraw.Draw(acc_rd)
d_rd.ellipse([(430, 190), (476, 222)], outline=(180, 150, 90, 255), width=3)
d_rd.ellipse([(489, 190), (535, 222)], outline=(180, 150, 90, 255), width=3)
d_rd.arc([(476, 196), (489, 208)], start=180, end=360, fill=(180, 150, 90, 255), width=3)
d_rd.line([(430, 204), (415, 198)], fill=(180, 150, 90, 255), width=3)
d_rd.line([(535, 204), (560, 198)], fill=(180, 150, 90, 255), width=3)
acc_rd.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_round.png'))

print('All 10 layers rebuilt with Ultimate Aesthetic Architecture!')
