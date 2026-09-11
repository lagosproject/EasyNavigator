#!/usr/bin/env python3
"""
upload_playstore_metadata.py — Programmatic Google Play Store Publisher for Easy Navigator
========================================================================================
Publishes or updates localized store listings, phone screenshots,
tablet screenshots, feature graphics, and optionally AAB bundles using the Google Play Developer API.
"""

import os
import sys
import time
import socket
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set default socket timeout to 120 seconds to prevent premature drops during large asset transfers
socket.setdefaulttimeout(120)

PACKAGE_NAME = "appinventor.ai_grmapal2.Navegator"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

DEFAULT_AAB_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "app", "build", "outputs", "bundle", "release", "app-release.aab"))

def execute_with_retry(request_factory, max_retries=5, initial_delay=3):
    """Executes a Google API request with exponential backoff on network errors/timeouts."""
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            req = request_factory()
            return req.execute(num_retries=2)
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"    ⚠️ Request failed ({type(e).__name__}: {e}), retrying in {delay}s (attempt {attempt}/{max_retries})...")
            time.sleep(delay)
            delay *= 2


def find_default_key_file():
    env_key = os.environ.get("PLAY_STORE_JSON_KEY")
    if env_key and os.path.exists(env_key):
        return env_key
    local_key = os.path.join(SCRIPT_DIR, "playstore-key.json")
    if os.path.exists(local_key):
        return local_key
    return None

METADATA = {
    "es-ES": {
        "title": "Easy Navigator",
        "shortDescription": "Navegador web rápido, privado y efímero con búsqueda por voz y lector QR.",
        "fullDescription": (
            "¿Buscas navegar por internet con total rapidez, privacidad y sin dejar rastro? "
            "Easy Navigator es el navegador web ligero y privado diseñado para ofrecerte la experiencia más fluida y segura.\n\n"
            "Olvídate de historiales persistentes, cookies invasivas y rastreadores. Cada sesión es completamente efímera: "
            "al salir o pulsar el botón de borrado rápido, todos tus rastros se esfuman de inmediato.\n\n"
            "Características principales:\n"
            "• Privacidad absoluta y efímera: Modo incógnito permanente por defecto. Sin almacenamiento de cookies, caché en disco ni formularios guardados.\n"
            "• Borrado rápido (Wipe Out): Un toque en el icono de fuego para purgar instantáneamente la sesión actual.\n"
            "• Búsqueda por voz integrada: Dicta cualquier búsqueda cómodamente en la barra de direcciones sin tener que escribir.\n"
            "• Escáner y generador de códigos QR: Abre enlaces al instante escaneando códigos QR con tu cámara, o comparte la página actual generando un código QR en pantalla.\n"
            "• Motores de búsqueda configurables: Alterna fácilmente entre Google, DuckDuckGo, Bing, Ecosia o añade tu motor de búsqueda personalizado favorito.\n"
            "• Navegación inteligente: Barra de herramientas estilizada Material You, botón de avance rápido e historial de navegación reciente accesible con una pulsación prolongada.\n"
            "• Deslizar para refrescar calibrado: Actualiza tus páginas web favoritas de forma intuitiva sin interrupciones accidentales al hacer scroll.\n"
            "• Extremadamente ligero y optimizado: Compatible desde Android 5.0 Lollipop hasta Android 16, garantizando un consumo mínimo de batería y memoria.\n\n"
            "¡Disfruta de una web más limpia, rápida y segura con Easy Navigator!"
        )
    },
    "en-US": {
        "title": "Easy Navigator",
        "shortDescription": "Fast, private, and ephemeral web browser with voice search & QR code scanner.",
        "fullDescription": (
            "Looking for a fast, private, and lightweight way to browse the web without leaving traces? "
            "Easy Navigator is built to give you a fluid, distraction-free, and secure browsing experience.\n\n"
            "Forget about persistent history, intrusive cookies, and trackers. Every session is strictly ephemeral: "
            "when you exit or tap the quick wipe button, your session data vanishes instantly.\n\n"
            "Key Features:\n"
            "• True Ephemeral Privacy: Permanent incognito mode by default. Zero cookie storage, zero disk cache, and no saved credentials or form data.\n"
            "• Instant Session Purge: A single tap on the fire button instantly clears all session data, tabs, and temporary memory.\n"
            "• Integrated Voice Dictation: Speak your searches naturally directly into the search bar without typing.\n"
            "• QR Scanner & Code Generator: Scan QR codes with your camera to open links instantly, or share your current webpage via an on-screen QR code.\n"
            "• Customizable Search Engines: Switch easily between Google, DuckDuckGo, Bing, Ecosia, or define your own custom search provider.\n"
            "• Smart & Modern Navigation: Material You pill design, quick forward button, and a forward history sheet on long-press.\n"
            "• Tuned Pull-to-Refresh: Refresh web pages smoothly with zero accidental triggers when scrolling up or down.\n"
            "• Ultra Lightweight & Fast: Engineered for top performance from Android 5.0 up to Android 16 with minimal battery and RAM footprint.\n\n"
            "Experience a cleaner, faster, and truly private web with Easy Navigator!"
        )
    },
    "fr-FR": {
        "title": "Easy Navigator",
        "shortDescription": "Navigateur web rapide, privé et éphémère avec recherche vocale et lecteur QR.",
        "fullDescription": (
            "Vous recherchez un navigateur web ultra-rapide, privé et léger qui ne laisse aucune trace ? "
            "Easy Navigator est conçu pour vous offrir une expérience de navigation fluide, sécurisée et sans distractions.\n\n"
            "Dites adieu aux historiques persistants, aux cookies intrusifs et aux traqueurs. Chaque session est strictement éphémère : "
            "à la fermeture ou en touchant le bouton d'effacement rapide, toutes vos données disparaissent instantanément.\n\n"
            "Fonctionnalités principales :\n"
            "• Confidentialité absolue et éphémère : Mode navigation privée permanente par défaut. Aucun cookie conservé, aucun cache disque, aucun mot de passe enregistré.\n"
            "• Purge instantanée de session : Un simple clic sur l'icône flamme pour effacer immédiatement toute la session en cours.\n"
            "• Dictée vocale intégrée : Dictez vos recherches directement dans la barre d'adresse sans avoir à taper.\n"
            "• Scanner et générateur QR code : Scannez des codes QR avec votre appareil photo pour ouvrir des liens instantanément, ou partagez votre page web actuelle via un QR code à l'écran.\n"
            "• Moteurs de recherche personnalisables : Choisissez parmi Google, DuckDuckGo, Bing, Ecosia, ou ajoutez facilement votre moteur favori personnalisé.\n"
            "• Navigation intuitive et moderne : Design Material You soigné, bouton d'avance rapide et accès à l'historique par appui long.\n"
            "• Actualisation par glissement calibrée : Rechargez les pages de manière fluide sans déclenchements involontaires lors du défilement.\n"
            "• Ultra-léger et optimisé : Compatible d'Android 5.0 jusqu'à Android 16 pour une consommation minimale de batterie et de mémoire.\n\n"
            "Profitez d'un Web plus pur, plus rapide et véritablement privé avec Easy Navigator !"
        )
    },
    "pt-PT": {
        "title": "Easy Navigator",
        "shortDescription": "Navegador web rápido, privado e efémero com pesquisa por voz e leitor QR.",
        "fullDescription": (
            "Procura navegar na internet com total rapidez, privacidade e sem deixar rastos? "
            "O Easy Navigator é o navegador web leve e seguro concebido para proporcionar uma experiência fluida e sem distrações.\n\n"
            "Esqueça históricos persistentes, cookies invasivos e rastreadores. Cada sessão é estritamente efémera: "
            "ao sair ou ao tocar no botão de limpeza rápida, todos os dados da sessão desaparecem de imediato.\n\n"
            "Principais funcionalidades:\n"
            "• Privacidade total e efémera: Modo incógnito permanente por defeito. Sem armazenamento de cookies, sem cache em disco e sem dados guardados.\n"
            "• Limpeza rápida imediata: Um toque no ícone de fogo para eliminar instantaneamente a sessão atual.\n"
            "• Pesquisa por voz integrada: Dite qualquer termo de pesquisa comodamente na barra de endereços sem necessidade de digitar.\n"
            "• Leitor e gerador de códigos QR: Abra hiperligações num instante lendo códigos QR com a câmara, ou partilhe a página atual exibindo um código QR no ecrã.\n"
            "• Motores de pesquisa configuráveis: Alterne facilmente entre Google, DuckDuckGo, Bing, Ecosia ou defina o seu próprio motor de pesquisa personalizado.\n"
            "• Navegação inteligente e moderna: Design Material You estilizado, botão de avanço rápido e acesso ao histórico com pressão longa.\n"
            "• Puxar para atualizar calibrado: Atualize as suas páginas web intuitivamente sem ativações acidentais durante o scroll.\n"
            "• Extremamente leve e otimizado: Suporta desde o Android 5.0 até ao Android 16, garantindo o menor consumo de bateria e memória.\n\n"
            "Experimente uma web mais rápida, limpa e verdadeiramente privada com o Easy Navigator!"
        )
    }
}

def upload_listing_and_images_for_locale(service, edit_id, lang):
    if lang not in METADATA:
        raise ValueError(f"No metadata found for locale: {lang}")

    print(f"\n=======================================================")
    print(f" Processing Locale: {lang}")
    print(f"=======================================================")

    # 1. Update text listing
    print(f"Updating store listing text for '{lang}'...")
    listing_info = METADATA[lang]
    listing_res = execute_with_retry(lambda: service.edits().listings().update(
        packageName=PACKAGE_NAME,
        editId=edit_id,
        language=lang,
        body={
            "title": listing_info["title"],
            "shortDescription": listing_info["shortDescription"],
            "fullDescription": listing_info["fullDescription"]
        }
    ))
    print(f"  ✓ Updated listing: title='{listing_res.get('title')}'")
    print(f"  ✓ Short description ({len(listing_info['shortDescription'])} chars)")
    print(f"  ✓ Full description ({len(listing_info['fullDescription'])} chars)")

    # Helper to upload images for an imageType
    def upload_images_for_type(image_type, image_paths):
        print(f"\nUploading {image_type} for '{lang}' ({len(image_paths)} images)...")
        try:
            execute_with_retry(lambda: service.edits().images().deleteall(
                packageName=PACKAGE_NAME,
                editId=edit_id,
                language=lang,
                imageType=image_type
            ))
        except Exception as e:
            print(f"  (Notice on deleteall: {e})")

        for idx, img_path in enumerate(image_paths, start=1):
            if not os.path.exists(img_path):
                print(f"  ✗ File missing: {img_path}")
                continue
            def do_upload(path=img_path):
                media = MediaFileUpload(path, mimetype="image/png")
                return service.edits().images().upload(
                    packageName=PACKAGE_NAME,
                    editId=edit_id,
                    language=lang,
                    imageType=image_type,
                    media_body=media
                )
            res = execute_with_retry(do_upload)
            img_id = res.get("image", {}).get("id")
            size_kb = os.path.getsize(img_path) // 1024
            print(f"  ✓ [{idx}/{len(image_paths)}] Uploaded {os.path.basename(img_path)} ({size_kb} KB) -> ID: {img_id}")

    # 2. Phone Screenshots (5 cards)
    phone_dir = os.path.join(OUTPUT_DIR, "phone", lang)
    if os.path.isdir(phone_dir):
        phone_images = sorted([os.path.join(phone_dir, f) for f in os.listdir(phone_dir) if f.endswith(".png")])
        upload_images_for_type("phoneScreenshots", phone_images)
    else:
        print(f"  ✗ Phone screenshots dir missing: {phone_dir}")

    # 3. 7-inch Tablet Screenshots
    tablet7_dir = os.path.join(OUTPUT_DIR, "tablet_7", lang)
    if os.path.isdir(tablet7_dir):
        tablet7_images = sorted([os.path.join(tablet7_dir, f) for f in os.listdir(tablet7_dir) if f.endswith(".png")])
        upload_images_for_type("sevenInchScreenshots", tablet7_images)

    # 4. 10-inch Tablet Screenshots
    tablet10_dir = os.path.join(OUTPUT_DIR, "tablet_10", lang)
    if os.path.isdir(tablet10_dir):
        tablet10_images = sorted([os.path.join(tablet10_dir, f) for f in os.listdir(tablet10_dir) if f.endswith(".png")])
        upload_images_for_type("tenInchScreenshots", tablet10_images)

    # 5. Feature Graphic
    fg_path = os.path.join(OUTPUT_DIR, "feature_graphics", f"feature_graphic_{lang}.png")
    if os.path.exists(fg_path):
        upload_images_for_type("featureGraphic", [fg_path])
    else:
        print(f"  ✗ Feature graphic missing: {fg_path}")


def upload_bundle_to_track(service, edit_id, bundle_path, track_name="internal"):
    if not os.path.exists(bundle_path):
        print(f"  ✗ AAB bundle file not found at: {bundle_path}")
        return None
    print(f"\n[AAB Upload] Uploading App Bundle: {bundle_path}...")
    def do_upload_bundle():
        media = MediaFileUpload(bundle_path, mimetype="application/octet-stream")
        return service.edits().bundles().upload(
            packageName=PACKAGE_NAME,
            editId=edit_id,
            media_body=media
        )
    bundle_res = execute_with_retry(do_upload_bundle)
    version_code = bundle_res.get("versionCode")
    print(f"  ✓ Uploaded AAB bundle! Version code: {version_code}")

    print(f"[Track Update] Assigning bundle {version_code} to track '{track_name}'...")
    track_body = {
        "track": track_name,
        "releases": [
            {
                "name": f"Release {version_code} (18.2)",
                "versionCodes": [str(version_code)],
                "status": "completed",
                "releaseNotes": [
                    {
                        "language": "es-ES",
                        "text": "Actualización v18.2: optimización Edge-to-Edge completa con soporte para recortes de pantalla, eliminación de APIs obsoletas y reducción avanzada de recursos con R8."
                    },
                    {
                        "language": "en-US",
                        "text": "Update v18.2: Full Edge-to-Edge optimization with display cutout support, deprecated API removal, and advanced R8 resource shrinking."
                    },
                    {
                        "language": "fr-FR",
                        "text": "Mise à jour v18.2 : Optimisation Edge-to-Edge avec prise en charge des encoches, suppression des API obsolètes et réduction avancée des ressources R8."
                    },
                    {
                        "language": "pt-PT",
                        "text": "Atualização v18.2: Otimização Edge-to-Edge com suporte a recortes de ecrã, remoção de APIs obsoletas e redução avançada de recursos com R8."
                    }
                ]
            }
        ]
    }
    execute_with_retry(lambda: service.edits().tracks().update(
        packageName=PACKAGE_NAME,
        editId=edit_id,
        track=track_name,
        body=track_body
    ))
    print(f"  ✓ Successfully updated track '{track_name}'")
    return version_code


def main():
    parser = argparse.ArgumentParser(description="Upload Play Store metadata, screenshots and bundles for Easy Navigator")
    parser.add_argument("--lang", default="all", help="Locale to upload ('all', 'es-ES', 'en-US', 'fr-FR', 'pt-PT') (default: all)")
    parser.add_argument("--key", default=find_default_key_file(), help="Path to service account JSON key (default: auto-detected or PLAY_STORE_JSON_KEY)")
    parser.add_argument("--dry-run", action="store_true", help="Perform upload without final commit")
    parser.add_argument("--upload-bundle", action="store_true", help="Upload the release AAB bundle to Play Store")
    parser.add_argument("--bundle-path", default=DEFAULT_AAB_PATH, help=f"Path to release AAB bundle (default: {DEFAULT_AAB_PATH})")
    parser.add_argument("--track", default="internal", choices=["internal", "alpha", "beta", "production"], help="Track to assign the bundle to (default: internal)")
    parser.add_argument("--skip-metadata", action="store_true", help="Skip updating store listings and screenshots")
    args = parser.parse_args()

    if not args.key or not os.path.exists(args.key):
        sys.exit(f"Error: Service account JSON key not found. Looked at '{args.key}'. Specify with --key <path> or set PLAY_STORE_JSON_KEY environment variable.")

    print(f"Key file: {args.key}")
    print(f"Connecting to Google Play Developer API for package '{PACKAGE_NAME}'...")
    credentials = service_account.Credentials.from_service_account_file(
        args.key,
        scopes=["https://www.googleapis.com/auth/androidpublisher"]
    )
    service = build("androidpublisher", "v3", credentials=credentials)

    edit = execute_with_retry(lambda: service.edits().insert(body={}, packageName=PACKAGE_NAME))
    edit_id = edit["id"]
    print(f"Created edit session: {edit_id}")

    try:
        if not args.skip_metadata:
            locales = list(METADATA.keys()) if args.lang == "all" else [args.lang]
            for loc in locales:
                upload_listing_and_images_for_locale(service, edit_id, loc)
        else:
            print("Skipping store listings and screenshots update (--skip-metadata)")

        if args.upload_bundle:
            upload_bundle_to_track(service, edit_id, args.bundle_path, track_name=args.track)

        if args.dry_run:
            print("\n=======================================================")
            print(" [DRY RUN] Aborting edit session without committing changes.")
            print("=======================================================")
            service.edits().delete(packageName=PACKAGE_NAME, editId=edit_id).execute()
        else:
            print(f"\nCommitting edit {edit_id} to Google Play...")
            try:
                commit_res = execute_with_retry(lambda: service.edits().commit(
                    packageName=PACKAGE_NAME,
                    editId=edit_id
                ))
            except Exception as e:
                if "changesNotSentForReview" in str(e):
                    commit_res = execute_with_retry(lambda: service.edits().commit(
                        packageName=PACKAGE_NAME,
                        editId=edit_id,
                        changesNotSentForReview=True
                    ))
                else:
                    raise
            print(f"🎉 Successfully committed edit! Result ID: {commit_res.get('id')}")
            print("👉 In Google Play Console UI, review the new release under the track and click 'Send for review' (Enviar a revisión).")

    except Exception as e:
        print(f"\n❌ Error encountered during Play Store update: {e}")
        try:
            service.edits().delete(packageName=PACKAGE_NAME, editId=edit_id).execute()
            print("Cleaned up edit session.")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
