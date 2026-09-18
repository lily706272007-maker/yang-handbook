import os, sys
from PIL import Image, ImageDraw

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
# 2. Body Layers (Layer 3)
# ------------------------------------------------------------------
print('2. Body Layers...')
for b_name, out_name in [
    ('body_layer_male_normal.png', 'body_male_normal.png'),
    ('body_layer_male_sturdy.png', 'body_male_sturdy.png'),
    ('body_layer_female_normal.png', 'body_female_normal.png'),
    ('body_layer_female_chubby.png', 'body_female_chubby.png')
]:
    b_path = os.path.join(PHOTOS_DIR, b_name)
    if os.path.exists(b_path):
        src = Image.open(b_path).convert('RGBA')
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        c.paste(src, (0, 180), src)
        c.save(os.path.join(LAYERS_DIR, 'body', out_name))

# ------------------------------------------------------------------
# 3. Face Shapes (Layer 4)
# Full ear width x: 12..258 to prevent ear clipping
# ------------------------------------------------------------------
print('3. Face Shapes (10 natural + 10 tan)...')
for i in range(1, 11):
    for tone in ['natural', 'tan']:
        f_path = os.path.join(PHOTOS_DIR, f'faces/face_{i:02d}_{tone}.jpg')
        if not os.path.exists(f_path):
            continue
        fim = Image.open(f_path)
        head_mask = Image.new('RGBA', (fim.width, fim.height), (0, 0, 0, 0))
        for y in range(15, 385):
            for x in range(10, 258):
                r, g, b = fim.getpixel((x, y))
                # Card background is grey (low saturation, r ~ g ~ b)
                # Face skin has saturation: r > b + 18 or dark outline
                is_skin_or_line = (r > b + 18) or (r < 100 and g < 100 and b < 100)
                if is_skin_or_line:
                    head_mask.putpixel((x, y), (r, g, b, 255))
        hc = head_mask.crop((10, 15, 258, 385))
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        c.paste(hc, (377, 40), hc)
        t_short = 'nat' if tone == 'natural' else 'tan'
        c.save(os.path.join(LAYERS_DIR, f'faces/face_{i:02d}_{t_short}.png'))

# ------------------------------------------------------------------
# 4. Eyes Layer (Layer 7)
# ------------------------------------------------------------------
print('4. Eyes Layer (14 styles)...')
eye_cat = Image.open(os.path.join(PHOTOS_DIR, 'eye_styles_14_catalog.jpg'))
eye_cards = [
    # Male 1..6
    ('eye_m01', (29, 132, 333, 230)),
    ('eye_m02', (359, 132, 663, 230)),
    ('eye_m03', (690, 132, 994, 230)),
    ('eye_m04', (29, 350, 333, 448)),
    ('eye_m05', (359, 350, 663, 448)),
    ('eye_m06', (690, 350, 994, 448)),
    # Female 1..8
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
            is_skin = (r > 225 and g > 195 and b > 180 and (r - b > 25) and (g - b > 8))
            is_shadow_skin = (r > 200 and g > 170 and b > 150 and (r - b > 30))
            if not (is_skin or is_shadow_skin):
                e_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = e_rgba.getbbox()
    if bbox:
        ec = e_rgba.crop(bbox)
        ratio = 120.0 / ec.width
        scaled = ec.resize((int(ec.width * ratio), int(ec.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 483 - scaled.width // 2
        py = 194
        c.paste(scaled, (px, py), scaled)
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
        px = 485 - scaled.width // 2
        py = 168
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'eyebrows/{name}.png'))

# ------------------------------------------------------------------
# 6. Nose Layer (Layer 6)
# Completely clean extraction without magenta guidelines or face contours
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
            # Strict magenta check
            is_magenta = (r > 150 and g < 130 and b > 105)
            if is_magenta:
                continue
            # Dark nose outline & nostril
            is_outline = (r < 110 and g < 65 and b < 60)
            # Subtle nostril shadow
            is_shadow = (r < 165 and g < 115 and b < 95 and r > b + 35)
            # Subtle nose highlight
            is_highlight = (r > 248 and g > 240 and b > 230)
            if is_outline or is_shadow or is_highlight:
                n_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = n_rgba.getbbox()
    if bbox:
        nc = n_rgba.crop(bbox)
        ratio = 32.0 / nc.width
        scaled = nc.resize((int(nc.width * ratio), int(nc.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 485 - scaled.width // 2
        py = 232
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'noses/{name}.png'))

# ------------------------------------------------------------------
# 7. Mouth Layer (Layer 5)
# Extract only smile line, teeth, and lips; transparent skin
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
            # Smile line & lip contour
            is_line = (r < 115 and g < 65 and b < 65)
            # Teeth
            is_teeth = (r > 240 and g > 240 and b > 240)
            # Lip color
            is_lip = (r > 190 and g < 155 and b < 140 and r > g + 40)
            if is_line or is_teeth or is_lip:
                m_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = m_rgba.getbbox()
    if bbox:
        mc = m_rgba.crop(bbox)
        ratio = 56.0 / mc.width
        scaled = mc.resize((int(mc.width * ratio), int(mc.height * ratio)), Image.Resampling.NEAREST)
        c = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 485 - scaled.width // 2
        py = 295
        c.paste(scaled, (px, py), scaled)
        c.save(os.path.join(LAYERS_DIR, f'mouths/{name}.png'))

# ------------------------------------------------------------------
# 8. Bangs Layer (Layer 9)
# Tightly bounded crops, zero top labels, clean center face
# ------------------------------------------------------------------
print('8. Bangs Layer (16 styles x 2 colors)...')
bangs_cat = Image.open(os.path.join(PHOTOS_DIR, 'bangs_16_catalog.jpg'))
bang_cards = [
    # Male 1..6
    ('bang_01', (130, 68, 280, 230)),
    ('bang_02', (420, 68, 570, 230)),
    ('bang_03', (710, 68, 860, 230)),
    ('bang_04', (145, 288, 285, 450)),
    ('bang_05', (420, 288, 580, 450)),
    ('bang_06', (715, 288, 855, 450)),
    # Female 1..10 (crop starts at y=565 and y=795 to avoid title texts)
    ('bang_07', (40, 565, 200, 720)),
    ('bang_08', (235, 565, 395, 720)),
    ('bang_09', (430, 565, 575, 720)),
    ('bang_10', (625, 565, 775, 720)),
    ('bang_11', (815, 565, 960, 720)),
    ('bang_12', (50, 795, 190, 950)),
    ('bang_13', (235, 795, 395, 950)),
    ('bang_14', (425, 795, 585, 950)),
    ('bang_15', (615, 795, 775, 950)),
    ('bang_16', (815, 795, 960, 950)),
]

for name, box in bang_cards:
    card = bangs_cat.crop(box)
    b_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    for y in range(card.height):
        for x in range(card.width):
            r, g, b = card.getpixel((x, y))
            # Hair pixels are dark (max < 160)
            if max(r, g, b) < 160:
                # Remove face center marks (nostril/chin in lower center face)
                if abs(x - card.width * 0.5) < 35 and y > card.height * 0.52 and y < card.height * 0.85:
                    continue
                # Remove jaw outline at very bottom center
                if abs(x - card.width * 0.5) < 45 and y > card.height * 0.85:
                    continue
                b_rgba.putpixel((x, y), (r, g, b, 255))
    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        ratio = 215.0 / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.NEAREST)
        
        # Black
        c_black = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 485 - scaled.width // 2
        py = 40
        c_black.paste(scaled, (px, py), scaled)
        c_black_rec = recolor_image(c_black, to_natural_black)
        c_black_rec.save(os.path.join(LAYERS_DIR, f'bangs/{name}_black.png'))
        
        # Flaxen Brown
        c_flaxen = recolor_image(c_black, to_flaxen_brown)
        c_flaxen.save(os.path.join(LAYERS_DIR, f'bangs/{name}_flaxen.png'))

# ------------------------------------------------------------------
# 9. Back Hair Layer (Layer 2)
# Strictly obeying user constraint: only protruding peripheries visible!
# ------------------------------------------------------------------
print('9. Back Hair Layer (10 styles x 2 colors, periphery-only)...')
back_cat = Image.open(os.path.join(PHOTOS_DIR, 'back_hair_front_view_catalog.jpg'))
back_cards = [
    # Row 0 (starts below header text y=55)
    ('back_01_mid_bun', (50, 55, 255, 315)),
    ('back_02_low_bun', (290, 90, 485, 315)),
    ('back_03_bob_cut', (525, 90, 715, 315)),
    ('back_04_claw_clip', (755, 65, 965, 315)),
    # Row 1
    ('back_05_high_pony', (60, 395, 280, 625)),
    ('back_06_low_pony', (295, 410, 500, 625)),
    ('back_07_undercut', (530, 410, 705, 625)),
    # Row 2
    ('back_08_wavy_bob', (50, 705, 260, 940)),
    ('back_09_half_up', (530, 680, 715, 940)),
    ('back_10_layered_pixie', (750, 705, 950, 940)),
]

for name, box in back_cards:
    card = back_cat.crop(box)
    b_rgba = Image.new('RGBA', card.size, (0, 0, 0, 0))
    cat_bg = back_cat.getpixel((10, 10))
    for y in range(card.height):
        for x in range(card.width):
            p = card.getpixel((x, y))
            diff_bg = max(abs(p[0] - cat_bg[0]), abs(p[1] - cat_bg[1]), abs(p[2] - cat_bg[2]))
            is_face_skin = (p[0] > 225 and p[1] > 225 and p[2] > 225)
            if diff_bg > 18 and not is_face_skin:
                b_rgba.putpixel((x, y), (p[0], p[1], p[2], 255))
    bbox = b_rgba.getbbox()
    if bbox:
        bc = b_rgba.crop(bbox)
        ratio = 220.0 / bc.width
        scaled = bc.resize((int(bc.width * ratio), int(bc.height * ratio)), Image.Resampling.NEAREST)
        
        c_black = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        px = 485 - scaled.width // 2
        py = 40
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
d_sq.line([(430, 200), (410, 196)], fill=(40, 40, 45, 255), width=3)
d_sq.line([(535, 200), (555, 196)], fill=(40, 40, 45, 255), width=3)
acc_sq.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_square.png'))

acc_rd = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
d_rd = ImageDraw.Draw(acc_rd)
d_rd.ellipse([(430, 190), (476, 222)], outline=(180, 150, 90, 255), width=3)
d_rd.ellipse([(489, 190), (535, 222)], outline=(180, 150, 90, 255), width=3)
d_rd.arc([(476, 196), (489, 208)], start=180, end=360, fill=(180, 150, 90, 255), width=3)
d_rd.line([(430, 204), (410, 198)], fill=(180, 150, 90, 255), width=3)
d_rd.line([(535, 204), (555, 198)], fill=(180, 150, 90, 255), width=3)
acc_rd.save(os.path.join(LAYERS_DIR, 'accessories/acc_glasses_round.png'))

print('All 10 layers rebuilt with high precision!')
