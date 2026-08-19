# Cómo publicar este repositorio en GitHub

## Opción recomendada: GitHub Desktop

1. Descomprime la carpeta `persimmon-hsi-longitudinal-tracking`.
2. Instala y abre GitHub Desktop.
3. Inicia sesión con tu cuenta de GitHub.
4. Selecciona **File → Add local repository** y elige la carpeta del proyecto.
5. Si GitHub Desktop indica que todavía no es un repositorio Git, crea el repositorio local desde esa carpeta.
6. Revisa cuidadosamente los archivos que se van a incluir. El `.gitignore` ya excluye los cubos HSI, ZIP, BIN/HDR, datos intermedios, checkpoints y exportaciones.
7. Realiza el primer commit con un mensaje como:
   `Initial reproducible manuscript code release`
8. Usa **Publish repository**.
9. Como nombre se recomienda:
   `persimmon-hsi-longitudinal-tracking`
10. Puede mantenerse **Private** durante la revisión interna y cambiarse a **Public** cuando esté listo para citarse en el manuscrito.

## Opción con Git

Crea primero un repositorio vacío en GitHub **sin inicializarlo con README, .gitignore o licencia**, porque esta carpeta ya contiene esos archivos.

Desde una terminal dentro de la carpeta:

```bash
git init -b main
git add .
git commit -m "Initial reproducible manuscript code release"
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

## Antes de hacerlo público

- Confirmar la lista definitiva de autores/colaboradores.
- Elegir la licencia del código de acuerdo con las políticas institucionales.
- Confirmar que no haya claves API, tokens, contraseñas o datos personales.
- Ejecutar `python scripts/verify_repository.py`.
- Verificar que `data/raw/` no contenga `Kaki.zip` ni archivos HSI.
- Cuando el manuscrito quede congelado, crear un release `v1.0-manuscript`.

## Recomendación para la citación

Para el envío, citar una versión congelada. Después de crear `v1.0-manuscript`, puede archivarse el release en Zenodo para obtener un DOI permanente. No cree el DOI hasta que la autoría, el título del repositorio y la versión del manuscrito estén confirmados.
