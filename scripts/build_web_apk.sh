#!/usr/bin/env bash
set -euo pipefail

# Crea un APK para pygbag en build/web/navalgame.apk incluyendo solo los archivos
# necesarios para la versión web (evita archivos .mp3 grandes). No modifica los
# archivos originales en /assets.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build/web/tmp_apk"
APK_PATH="$ROOT_DIR/build/web/navalgame.apk"

echo "Preparando APK web reducido en: $APK_PATH"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/assets/assets"
mkdir -p "$BUILD_DIR/assets/templates"

# Copiar main.py y config
cp "$ROOT_DIR/main.py" "$BUILD_DIR/assets/main.py"
cp "$ROOT_DIR/pygbag.config.json" "$BUILD_DIR/assets/pygbag.config.json"

# Copiar plantilla y favicon si existen
[ -d "$ROOT_DIR/templates" ] && cp -r "$ROOT_DIR/templates/"* "$BUILD_DIR/assets/templates/" || true
[ -f "$ROOT_DIR/index.html" ] && cp "$ROOT_DIR/index.html" "$BUILD_DIR/assets/index.html" || true
[ -f "$ROOT_DIR/assets/favicon.ico" ] && cp "$ROOT_DIR/assets/favicon.ico" "$BUILD_DIR/assets/favicon.ico" || true

# Copiar solo los ogg optimizados para pygbag (terminan en -pygbag.ogg) si existen,
# y también copiar las imágenes y png/jpg necesarias.
shopt -s nullglob
for f in "$ROOT_DIR/assets"/*-pygbag.ogg; do
  cp "$f" "$BUILD_DIR/assets/assets/"
done

for f in "$ROOT_DIR/assets"/*.ogg; do
  # si hay ogg sin sufijo -pygbag, cópialos también (fallback)
  cp "$f" "$BUILD_DIR/assets/assets/" || true
done

# Copiar imágenes y otros recursos (png, jpg)
for ext in png jpg jpeg webp svg; do
  for f in "$ROOT_DIR/assets"/*.$ext; do
    cp "$f" "$BUILD_DIR/assets/assets/" || true
  done
done

echo "Archivos copiados a $BUILD_DIR/assets/assets:"
ls -1 "$BUILD_DIR/assets/assets" | sed -n '1,200p' || true

cd "$BUILD_DIR"
zip -r ../navalgame.apk . > /dev/null
cd -

echo "APK creado en: $APK_PATH"
echo "Tamaño:" $(stat -c "%s" "$APK_PATH") bytes

echo "Nota: Este APK evita archivos .mp3. Si quieres incluir mp3 para pruebas locales,
edita este script o copia los mp3 manualmente al directorio assets/assets antes de empaquetar."
