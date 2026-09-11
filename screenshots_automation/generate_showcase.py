#!/usr/bin/env python3
"""
generate_showcase.py — Play Store Showcase Graphic & Feature Banner Generator
for Easy Navigator / Navegador fácil
=============================================================================
Creates high-contrast, polished showcase cards for:
- Phone: 1080×1920 px
- 7-inch Tablet: 1080×1920 px
- 10-inch Tablet: 1200×1920 px
- Feature Graphic: 1024×500 px
Across 4 languages: es-ES, en-US, fr-FR, pt-PT.
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Target Dimensions
PHONE_W, PHONE_H = 1080, 1920
TAB7_W, TAB7_H = 1080, 1920
TAB10_W, TAB10_H = 1200, 1920
FEATURE_W, FEATURE_H = 1024, 500

LANGS = ["es-ES", "en-US", "fr-FR", "pt-PT"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw", "phone")
OUT_DIR = os.path.join(SCRIPT_DIR, "output")
ICON_PATH = os.path.join(SCRIPT_DIR, "..", "app", "src", "main", "res", "mipmap-xxxhdpi", "ic_launcher.png")

# Brand Palette (Material 3 Navy / Primary Blue / Fire Accent)
BG_TOP = (11, 19, 43)        # Deep Navy (#0B132B)
BG_BOTTOM = (20, 32, 60)     # Midnight Blue (#14203C)
PRIMARY = (25, 118, 210)     # Primary Blue (#1976D2)
ACCENT_BLUE = (66, 165, 245) # Light Blue (#42A5F5)
FIRE_ACCENT = (255, 87, 34)  # Fire Orange (#FF5722)
WHITE = (255, 255, 255)
MUTED = (176, 190, 205)
CARD_BEZEL = (35, 45, 75)
SHADOW_COLOR = (0, 0, 0, 140)

# Localized Copy Configuration
COPY_DATA = {
    "es-ES": {
        "brand": "NAVEGADOR FÁCIL",
        "screens": [
            {
                "file": "screen1_home.png",
                "tag": "PRIVACIDAD TOTAL",
                "headline": "NAVEGACIÓN 100% EFÍMERA",
                "subtext": "Sin cookies, sin historial y sin rastros en tu dispositivo móvil."
            },
            {
                "file": "screen2_search.png",
                "tag": "BÚSQUEDA INTELIGENTE",
                "headline": "DICTADO POR VOZ Y URL RÁPIDA",
                "subtext": "Habla para buscar o navegar al instante sin teclear."
            },
            {
                "file": "screen3_qr.png",
                "tag": "CÓDIGOS QR",
                "headline": "ESCANEA Y COMPARTE POR QR",
                "subtext": "Abre webs con la cámara o genera un código QR para compartir."
            },
            {
                "file": "screen4_menu.png",
                "tag": "PERSONALIZACIÓN",
                "headline": "MOTORES DE BÚSQUEDA A TU GUSTO",
                "subtext": "Elige Google, DuckDuckGo, Bing, Ecosia o añade tu propio motor."
            },
            {
                "file": "screen5_wipe.png",
                "tag": "SEGURIDAD",
                "headline": "INCINERA TU SESIÓN EN 1 TOQUE",
                "subtext": "Borra todas las pestañas, caché y cookies con el botón de fuego."
            }
        ],
        "feature": {
            "title": "Navegador fácil",
            "tagline": "Navegación Rápida & 100% Efímera",
            "chips": ["Cero Cookies", "Búsqueda por Voz", "Escáner QR", "Incinerar Sesión"]
        }
    },
    "en-US": {
        "brand": "EASY NAVIGATOR",
        "screens": [
            {
                "file": "screen1_home.png",
                "tag": "TOTAL PRIVACY",
                "headline": "100% EPHEMERAL BROWSING",
                "subtext": "Zero cookies, zero history, and no traces on your mobile device."
            },
            {
                "file": "screen2_search.png",
                "tag": "SMART SEARCH",
                "headline": "VOICE DICTATION & FAST URLS",
                "subtext": "Speak to search or navigate instantly without typing."
            },
            {
                "file": "screen3_qr.png",
                "tag": "QR CODES",
                "headline": "SCAN & PEER SHARE VIA QR",
                "subtext": "Open websites using camera or display a QR code to share."
            },
            {
                "file": "screen4_menu.png",
                "tag": "CUSTOMIZATION",
                "headline": "CUSTOMIZABLE SEARCH ENGINES",
                "subtext": "Switch between Google, DuckDuckGo, Bing, Ecosia, or custom URLs."
            },
            {
                "file": "screen5_wipe.png",
                "tag": "SECURITY",
                "headline": "ONE-TAP SESSION INCINERATION",
                "subtext": "Purge all tabs, cache, and cookies with a single tap of the fire icon."
            }
        ],
        "feature": {
            "title": "Easy Navigator",
            "tagline": "Fast, Private & Ephemeral Browser",
            "chips": ["Zero Cookies", "Voice Search", "QR Scanner", "Instant Wipe"]
        }
    },
    "fr-FR": {
        "brand": "NAVIGATEUR FACILE",
        "screens": [
            {
                "file": "screen1_home.png",
                "tag": "CONFIDENTIALITÉ TOTALE",
                "headline": "NAVIGATION 100% ÉPHÉMÈRE",
                "subtext": "Zéro cookie, zéro historique et aucune trace sur votre appareil."
            },
            {
                "file": "screen2_search.png",
                "tag": "RECHERCHE INTELLIGENTE",
                "headline": "DICTÉE VOCALE & URL RAPIDE",
                "subtext": "Parlez pour chercher ou naviguer immédiatement sans clavier."
            },
            {
                "file": "screen3_qr.png",
                "tag": "CODES QR",
                "headline": "SCANNEZ & PARTAGEZ PAR QR",
                "subtext": "Ouvrez des liens avec l'appareil photo ou affichez un code QR."
            },
            {
                "file": "screen4_menu.png",
                "tag": "PERSONNALISATION",
                "headline": "MOTEURS DE RECHERCHE AU CHOIX",
                "subtext": "Choisissez Google, DuckDuckGo, Bing, Ecosia ou une URL personnalisée."
            },
            {
                "file": "screen5_wipe.png",
                "tag": "SÉCURITÉ",
                "headline": "INCINÉREZ LA SESSION EN 1 CLIC",
                "subtext": "Effacez tous les onglets, le cache et les cookies avec le bouton de feu."
            }
        ],
        "feature": {
            "title": "Navigateur facile",
            "tagline": "Navigation Rapide & 100% Éphémère",
            "chips": ["Zéro Cookie", "Recherche Vocale", "Scanner QR", "Effacement Instantané"]
        }
    },
    "pt-PT": {
        "brand": "NAVEGADOR FÁCIL",
        "screens": [
            {
                "file": "screen1_home.png",
                "tag": "PRIVACIDADE TOTAL",
                "headline": "NAVEGAÇÃO 100% EFÊMERA",
                "subtext": "Sem cookies, sem histórico e sem vestígios no seu telemóvel."
            },
            {
                "file": "screen2_search.png",
                "tag": "PESQUISA INTELIGENTE",
                "headline": "DITADO POR VOZ E URL RÁPIDA",
                "subtext": "Fale para pesquisar ou navegar de imediato sem digitar."
            },
            {
                "file": "screen3_qr.png",
                "tag": "CÓDIGOS QR",
                "headline": "ESCANEIE E COMPARTILHE POR QR",
                "subtext": "Abra links com a câmara ou gere um código QR no ecrã."
            },
            {
                "file": "screen4_menu.png",
                "tag": "PERSONALIZAÇÃO",
                "headline": "MOTORES DE PESQUISA À ESCOLHA",
                "subtext": "Alterne entre Google, DuckDuckGo, Bing, Ecosia ou URLs personalizadas."
            },
            {
                "file": "screen5_wipe.png",
                "tag": "SEGURANÇA",
                "headline": "INCINERE A SESSÃO NUM TOQUE",
                "subtext": "Apague todos os separadores, cache e cookies com o botão de fogo."
            }
        ],
        "feature": {
            "title": "Navegador fácil",
            "tagline": "Navegação Rápida & 100% Efêmera",
            "chips": ["Sem Cookies", "Pesquisa por Voz", "Leitor QR", "Limpeza Instantânea"]
        }
    }
}

def get_font(size, bold=True):
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for p in font_candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_vertical_gradient(width, height, top_color, bottom_color):
    base = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / float(height)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox[0]
        if w <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_device_frame(inner_img, target_w, target_h, corner_radius=28):
    border_px = 10
    avail_w = target_w - border_px * 2
    avail_h = target_h - border_px * 2

    scale_w = avail_w / float(inner_img.width)
    scale_h = avail_h / float(inner_img.height)
    scale = min(scale_w, scale_h)

    scaled_w = int(inner_img.width * scale)
    scaled_h = int(inner_img.height * scale)
    resized_screen = inner_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    # Frame dimensions
    frame_w = scaled_w + border_px * 2
    frame_h = scaled_h + border_px * 2

    # Create mask for rounded screen
    mask = Image.new("L", (scaled_w, scaled_h), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([0, 0, scaled_w, scaled_h], radius=corner_radius, fill=255)

    # Device body with rounded border
    frame = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
    draw_frame = ImageDraw.Draw(frame)
    draw_frame.rounded_rectangle(
        [0, 0, frame_w - 1, frame_h - 1],
        radius=corner_radius + 6,
        fill=(28, 36, 56, 255),
        outline=(66, 165, 245, 180),
        width=3
    )
    frame.paste(resized_screen, (border_px, border_px), mask)

    # Add soft drop shadow
    shadow_pad = 32
    shadow_img = Image.new("RGBA", (frame_w + shadow_pad * 2, frame_h + shadow_pad * 2), (0, 0, 0, 0))
    draw_shadow = ImageDraw.Draw(shadow_img)
    draw_shadow.rounded_rectangle(
        [shadow_pad, shadow_pad + 8, shadow_pad + frame_w, shadow_pad + frame_h + 8],
        radius=corner_radius + 8,
        fill=(0, 0, 0, 150)
    )
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(14))
    shadow_img.paste(frame, (shadow_pad, shadow_pad), frame)

    return shadow_img, shadow_pad

def render_showcase_card(screen_info, lang_data, width, height, is_tablet=False):
    card = draw_vertical_gradient(width, height, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(card)

    font_tag = get_font(24 if not is_tablet else 22, bold=True)
    font_hl = get_font(46 if not is_tablet else 42, bold=True)
    font_sub = get_font(28 if not is_tablet else 24, bold=False)

    raw_path = os.path.join(RAW_DIR, screen_info["file"])
    if os.path.exists(raw_path):
        screen_img = Image.open(raw_path).convert("RGBA")
    else:
        # Synthetic screen fallback
        screen_img = Image.new("RGBA", (1080, 2412), (245, 247, 250, 255))
        s_draw = ImageDraw.Draw(screen_img)
        s_draw.rectangle([0, 0, 1080, 180], fill=(25, 118, 210, 255))
        s_draw.text((60, 60), "Easy Navigator", font=get_font(48), fill=(255, 255, 255))

    # Top typography section
    pad_x = 70 if not is_tablet else (80 if width > 1100 else 70)
    start_y = 80 if not is_tablet else 70
    max_w = width - 2 * pad_x

    # Pill Tag
    tag_text = screen_info["tag"].upper()
    bbox = font_tag.getbbox(tag_text)
    tag_w = bbox[2] - bbox[0] + 32
    tag_h = bbox[3] - bbox[1] + 18
    draw.rounded_rectangle([pad_x, start_y, pad_x + tag_w, start_y + tag_h], radius=12, fill=PRIMARY)
    draw.text((pad_x + 16, start_y + 8), tag_text, font=font_tag, fill=WHITE)

    # Headline (multi-line wrapped to avoid clipping)
    hl_y = start_y + tag_h + 22
    hl_lines = wrap_text(screen_info["headline"], font_hl, max_w)
    curr_y = hl_y
    for line in hl_lines:
        draw.text((pad_x, curr_y), line, font=font_hl, fill=WHITE)
        bbox_l = font_hl.getbbox(line)
        curr_y += (bbox_l[3] - bbox_l[1]) + 12

    # Subtext (multi-line wrapped to avoid clipping)
    curr_y += 6
    sub_lines = wrap_text(screen_info["subtext"], font_sub, max_w)
    for line in sub_lines:
        draw.text((pad_x, curr_y), line, font=font_sub, fill=MUTED)
        bbox_s = font_sub.getbbox(line)
        curr_y += (bbox_s[3] - bbox_s[1]) + 10

    # Device placed cleanly below typography with comfortable margins
    device_top_y = curr_y + 35
    bottom_margin = 60
    available_h = height - device_top_y - bottom_margin
    available_w = int(width * 0.86)

    framed, shadow_pad = create_device_frame(screen_img, available_w, available_h)

    pos_x = (width - framed.width) // 2
    pos_y = device_top_y - shadow_pad
    card.paste(framed, (pos_x, pos_y), framed)

    return card

def render_feature_graphic(lang_code, lang_info):
    banner = draw_vertical_gradient(FEATURE_W, FEATURE_H, (10, 20, 50), (22, 38, 80))
    draw = ImageDraw.Draw(banner)

    # Subtle circular ambient glow on background
    glow = Image.new("RGBA", (FEATURE_W, FEATURE_H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([50, -100, 650, 500], fill=(25, 118, 210, 70))
    g_draw.ellipse([600, 100, 1100, 600], fill=(255, 87, 34, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    banner.paste(glow, (0, 0), glow)

    # App Icon with card framing
    if os.path.exists(ICON_PATH):
        icon_img = Image.open(ICON_PATH).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
        # Rounded icon card
        icon_card = Image.new("RGBA", (244, 244), (0, 0, 0, 0))
        ic_draw = ImageDraw.Draw(icon_card)
        ic_draw.rounded_rectangle([0, 0, 243, 243], radius=44, fill=(255, 255, 255, 245))
        icon_card.paste(icon_img, (12, 12), icon_img)
        banner.paste(icon_card, (70, 138), icon_card)

    # Typography
    text_x = 340
    f_title = get_font(56, bold=True)
    f_tagline = get_font(28, bold=False)
    f_chips = get_font(18, bold=True)

    draw.text((text_x, 140), lang_info["feature"]["title"], font=f_title, fill=WHITE)
    draw.text((text_x, 215), lang_info["feature"]["tagline"], font=f_tagline, fill=ACCENT_BLUE)

    # Feature Chips (2x2 grid with vibrant accent dots to guarantee zero emoji tofu boxes)
    row1_y = 265
    row2_y = 320
    chips = lang_info["feature"]["chips"]
    dot_colors = [
        (0, 230, 118),   # Privacy / Zero cookies (Emerald Green)
        (64, 196, 255),  # Voice Search (Sky Blue)
        (255, 215, 0),   # QR Scanner (Vibrant Gold)
        (255, 87, 34)    # Instant Wipe (Fiery Orange)
    ]

    # First row: chips 0 and 1
    curr_x = text_x
    for i in range(min(2, len(chips))):
        chip = chips[i]
        color = dot_colors[i]
        bbox = f_chips.getbbox(chip)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        cw = tw + 52
        ch = th + 18
        draw.rounded_rectangle([curr_x, row1_y, curr_x + cw, row1_y + ch], radius=12, fill=(35, 48, 85, 230), outline=(66, 165, 245, 150), width=1)
        dot_y = row1_y + ch // 2
        draw.ellipse([curr_x + 16, dot_y - 5, curr_x + 26, dot_y + 5], fill=color)
        draw.text((curr_x + 34, row1_y + 8), chip, font=f_chips, fill=WHITE)
        curr_x += cw + 14

    # Second row: chips 2 and 3
    curr_x = text_x
    for i in range(2, min(4, len(chips))):
        chip = chips[i]
        color = dot_colors[i]
        bbox = f_chips.getbbox(chip)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        cw = tw + 52
        ch = th + 18
        draw.rounded_rectangle([curr_x, row2_y, curr_x + cw, row2_y + ch], radius=12, fill=(35, 48, 85, 230), outline=(66, 165, 245, 150), width=1)
        dot_y = row2_y + ch // 2
        draw.ellipse([curr_x + 16, dot_y - 5, curr_x + 26, dot_y + 5], fill=color)
        draw.text((curr_x + 34, row2_y + 8), chip, font=f_chips, fill=WHITE)
        curr_x += cw + 14

    return banner

def main():
    print("=======================================================")
    print(" Easy Navigator — Play Store Showcase Generator")
    print("=======================================================")

    for lang in LANGS:
        print(f"\n==> Generating assets for '{lang}'...")
        lang_data = COPY_DATA[lang]

        # 1. Phone Showcase Cards (1080x1920)
        phone_dir = os.path.join(OUT_DIR, "phone", lang)
        os.makedirs(phone_dir, exist_ok=True)

        # 2. Tablet 7" Showcase Cards (1080x1920)
        tab7_dir = os.path.join(OUT_DIR, "tablet_7", lang)
        os.makedirs(tab7_dir, exist_ok=True)

        # 3. Tablet 10" Showcase Cards (1200x1920)
        tab10_dir = os.path.join(OUT_DIR, "tablet_10", lang)
        os.makedirs(tab10_dir, exist_ok=True)

        for idx, screen in enumerate(lang_data["screens"], start=1):
            # Phone card
            phone_card = render_showcase_card(screen, lang_data, PHONE_W, PHONE_H, is_tablet=False)
            phone_out = os.path.join(phone_dir, f"{idx}_{screen['file']}")
            phone_card.save(phone_out, "PNG", optimize=True)
            print(f"  ✓ Phone card [{idx}/5]: {os.path.basename(phone_out)}")

            # Tablet 7" card
            tab7_card = render_showcase_card(screen, lang_data, TAB7_W, TAB7_H, is_tablet=True)
            tab7_out = os.path.join(tab7_dir, f"{idx}_{screen['file']}")
            tab7_card.save(tab7_out, "PNG", optimize=True)

            # Tablet 10" card
            tab10_card = render_showcase_card(screen, lang_data, TAB10_W, TAB10_H, is_tablet=True)
            tab10_out = os.path.join(tab10_dir, f"{idx}_{screen['file']}")
            tab10_card.save(tab10_out, "PNG", optimize=True)

        # 4. Feature Graphic (1024x500)
        fg_dir = os.path.join(OUT_DIR, "feature_graphics")
        os.makedirs(fg_dir, exist_ok=True)
        feature_img = render_feature_graphic(lang, lang_data)
        feature_out = os.path.join(fg_dir, f"feature_graphic_{lang}.png")
        feature_img.save(feature_out, "PNG", optimize=True)
        print(f"  ✓ Feature Graphic: {os.path.basename(feature_out)}")

    print("\n=======================================================")
    print(" ✅ All Play Store graphics generated successfully!")
    print(f" Output directory: {OUT_DIR}")
    print("=======================================================")

if __name__ == "__main__":
    main()
