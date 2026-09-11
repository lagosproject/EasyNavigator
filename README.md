<p align="center">
  <img src="assets/icon.png" alt="Easy Navigator Logo" width="140" height="140" style="border-radius: 24%;" /><br>
  <h1 align="center">Easy Navigator</h1>
  <p align="center"><b>Navegación web rápida, privada y 100% efímera para tu día a día.</b></p>
</p>

<p align="center">
  <a href="https://play.google.com/store/apps/details?id=appinventor.ai_grmapal2.Navegator">
    <img src="https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png" alt="Disponible en Google Play" height="58" />
  </a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="https://developer.android.com"><img src="https://img.shields.io/badge/Android-5.0%2B%20%7C%20Target%2016-green.svg" alt="Android Support" /></a>
  <a href="https://kotlinlang.org"><img src="https://img.shields.io/badge/Kotlin-2.0.20-7F52FF.svg" alt="Kotlin" /></a>
  <img src="https://img.shields.io/badge/Privacy-100%25%20Ephemeral-success.svg" alt="Privacy First" />
</p>

---

## 🌟 ¿Qué es Easy Navigator?

**Easy Navigator** es un navegador web ultra-ligero diseñado para cualquier persona que desee consultar páginas de internet de forma inmediata sin preocuparse por rastreadores ni publicidad invasiva. A diferencia de los navegadores convencionales que acumulan historiales eternos y contraseñas en tu teléfono, Easy Navigator funciona en modo efímero continuo: cada vez que sales de la aplicación o pulsas su botón de purga, todos los rastros, archivos temporales y cookies se eliminan por completo al instante.

Es la herramienta perfecta para búsquedas rápidas, abrir enlaces compartidos por WhatsApp o redes sociales, leer noticias y escanear menús o códigos QR de forma limpia, sin dejar huella en tu dispositivo.

---

## ✨ Características Principales (Diseñadas para ti)

- 🛡️ **Privacidad Absoluta y Efímera:** Navega con tranquilidad. No almacena historial persistente, no guarda tus contraseñas ni deja rastro en la memoria de tu móvil.
- 🔥 **Botón de Incineración Rápida:** Con solo tocar el icono de fuego en la esquina superior, limpias al instante la página abierta, las cookies y la memoria temporal.
- 🎙️ **Búsqueda por Voz Integrada:** Olvídate de teclear en pantallas pequeñas. Toca el micrófono, di lo que estás buscando y accede a los resultados de inmediato.
- 📷 **Lector y Generador de Códigos QR:**
  - **Escanea:** Apunta tu cámara hacia cualquier código QR de un restaurante, evento o cartel para entrar en la página web automáticamente.
  - **Comparte:** Genera un código QR de la página que estás viendo en tu pantalla para que otra persona lo escanee con su teléfono al instante.
- 🔍 **Tus Buscadores Favoritos:** Alterna fácilmente entre Google, DuckDuckGo, Bing, Ecosia o añade el buscador que más te guste.
- ⚡ **Rápido y Amigable con tu Batería:** Desarrollado para abrirse al instante, sin procesos pesados que ralenticen tu móvil o consuman tu batería en segundo plano.
- 🖥️ **Modo Ordenador / Escritorio:** Si alguna web no se visualiza bien en formato móvil, activa el modo escritorio con un solo toque en el menú.
- 🔄 **Deslizar para Actualizar:** Recarga cualquier página web cómodamente deslizando el dedo hacia abajo.

---

## 📱 Capturas de Pantalla

<p align="center">
  <img src="assets/banner.png" alt="Easy Navigator Banner" width="100%" />
</p>

| 🏠 Pantalla de Inicio | 🔍 Búsqueda y Voz | 📷 Compartir con QR | ⚙️ Menú de Opciones | 🔥 Purgar Sesión |
| :---: | :---: | :---: | :---: | :---: |
| <img src="assets/screenshots/screen1_home.png" width="185" alt="Inicio" /> | <img src="assets/screenshots/screen2_search.png" width="185" alt="Búsqueda" /> | <img src="assets/screenshots/screen3_qr.png" width="185" alt="QR Share" /> | <img src="assets/screenshots/screen4_menu.png" width="185" alt="Menú" /> | <img src="assets/screenshots/screen5_wipe.png" width="185" alt="Wipe" /> |

---

<details>
<summary><b>🛠️ Guía Técnica para Desarrolladores & Arquitectura (Click para desplegar)</b></summary>
<br>

### 🏗️ Arquitectura y Tecnologías

Easy Navigator está desarrollado en **Kotlin nativo**, siguiendo las mejores prácticas de la plataforma Android moderna:

- **Lenguaje:** Kotlin 2.0.20 con JVM Target 17.
- **SDK Targets:** `minSdk = 21` (Android 5.0 Lollipop), `compileSdk = 36` / `targetSdk = 36` (Android 16).
- **UI / Rendering:** Android ViewBinding, AndroidX Edge-to-Edge (`enableEdgeToEdge`), Material Design 3 Components.
- **WebView Engine:** AndroidX WebKit (`androidx.webkit:webkit:1.12.1`) configurado con políticas estrictas de privacidad:
  - `cacheMode = LOAD_NO_CACHE`
  - `saveFormData = false`, `savePassword = false`
  - `geolocationEnabled = false`, `databaseEnabled = false`
  - `allowFileAccess = false`, `allowContentAccess = false`
  - `mixedContentMode = MIXED_CONTENT_NEVER_ALLOW`
  - Limpieza forzada de `CookieManager` y `WebStorage` al salir o invocar `wipeSession()`.
- **Código QR:** Integración con biblioteca ZXing (`zxing-android-embedded` y `zxing:core`).
- **Dictado por Voz:** `SpeechRecognizer` nativo con contrato de actividad moderno `ActivityResultContracts`.

### 📋 Requisitos Previos

- **JDK:** Java Development Kit 17 o superior.
- **Android SDK:** Android SDK Build-Tools 36.0.0 y Platform API 36 instalados.
- **Gradle:** Wrapper Gradle 8.11.1 incluido en el proyecto (`./gradlew`).

### 🚀 Compilación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/lagosproject/EasyNavigator.git
   cd EasyNavigator
   ```

2. **Configurar el entorno local:**
   - Copia el archivo de ejemplo para configurar la ruta de tu SDK:
     ```bash
     cp local.properties.example local.properties
     # Edita local.properties indicando la ruta de tu Android SDK si no la detecta automáticamente
     ```

3. **Compilar en modo Debug:**
   ```bash
   ./gradlew assembleDebug
   ```

4. **Instalar en un dispositivo o emulador conectado:**
   ```bash
   ./gradlew installDebug
   ```

5. **Compilar versión Release:**
   Para firmar la versión de producción, define las variables en tu entorno o en `keystore.properties`:
   ```bash
   cp keystore.properties.example keystore.properties
   # O exporta KEYSTORE_PATH, KEYSTORE_PASSWORD, KEY_ALIAS, KEY_PASSWORD
   ./gradlew assembleRelease
   ```

### 🤖 Automatización de Capturas y Publicación

El repositorio incluye herramientas automáticas en la carpeta `screenshots_automation/`:
- `capture_device_screens.sh`: Captura las pantallas del dispositivo mediante comandos ADB.
- `generate_showcase.py`: Genera los gráficos de muestra para teléfonos, tabletas de 7", tabletas de 10" y banner destacado en 4 idiomas (`es-ES`, `en-US`, `fr-FR`, `pt-PT`).
- `upload_playstore_metadata.py`: Publica los metadatos y gráficos en Google Play Store a través de la Google Play Developer API usando una cuenta de servicio.

</details>

---

## 🤝 Cómo Contribuir

¡Las contribuciones son bienvenidas! Si deseas reportar un error, sugerir mejoras o aportar código:
1. Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para conocer las pautas de desarrollo.
2. Consulta nuestra [Política de Seguridad](SECURITY.md) para reportar vulnerabilidades de privacidad.
3. Abre un Issue o envía un Pull Request siguiendo nuestras convenciones de Conventional Commits.

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

Desarrollado y mantenido con ❤️ por **[lagosproject](https://github.com/lagosproject)**.
