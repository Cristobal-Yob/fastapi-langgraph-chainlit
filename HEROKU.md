# Publicar Chainlit autenticado desde cero

**Objetivo: Heroku Cedar con buildpacks clásicos y stack heroku-24. No se afirma compatibilidad Fir/CNB.** Las órdenes de esta guía son acciones futuras del propietario: no se ha creado ninguna app, add-on ni despliegue.

> Advertencia: Chainlit está archivado y no recibe mantenimiento ni actualizaciones de seguridad. Este ejemplo de enseñanza solicitado no se recomienda para un servicio de producción.

## 1. Preparar herramientas y cuentas

Necesita Python 3.12, Git, GitHub CLI, Heroku CLI y cuentas propias. Este proyecto es autónomo y debe publicarse en un repositorio GitHub **privado nuevo**, sin importar historial, entornos, `.env`, OAuth ni auth de ejemplos anteriores. Consulte [README](README.md) para entorno y pruebas.

## 2. Configurar el agente

Copie `.env.example` a `.env` solo localmente. Genere `AGENT_API_TOKEN` con `secrets.token_urlsafe(32)`. Elija Google Developer API con `GOOGLE_GENAI_USE_VERTEXAI=false` y una clave propia, o Vertex con proyecto/location y ADC configurado expresamente fuera de Git. No use variables/cuentas de otra aplicación. `MODELO` y `FALLBACK_MODEL` deben ser distintos. Las instrucciones y el fallback son los del agente fuente, sin un responder de demostración.

`PUBLIC_ORIGIN` debe ser la URL HTTPS exacta que obtenga para su app, sin slash final. La excepción de ejecución local es la API base en localhost; los controles de navegador seguros requieren HTTPS local con un proxy de confianza o un túnel **solo si usted lo autoriza**. No desactive la validación de Origin para probarlos.

## Preparación específica

**Chainlit está archivado; no recibe actualizaciones de seguridad.** Consérvelo como material de enseñanza, no como recomendación de producción. Defina `CHAINLIT_AUTH_SECRET` con otro secreto aleatorio de 32 bytes. Genere `CHAINLIT_PASSWORD_SALT` con `secrets.token_hex(16)`. Calcule `CHAINLIT_PASSWORD_HASH` localmente con `hashlib.pbkdf2_hmac('sha256', getpass.getpass().encode(), salt.encode(), 600000).hex()` y configure el mismo salt. La contraseña nunca se escribe en Git. El callback verifica usuario y hash; la aplicación no arranca sin estos valores. El chat usa el core propio por loopback, consulta 202 y responde por WebSocket; no habilita persistencia de chats. Los frames/pings del servidor mantienen el transporte, pero un reinicio corta el chat.

## 3. Verificar antes de publicar

```sh
python -B -m unittest discover -s tests -v
```

En WhatsApp añada `npm test`. Los tests de PostgreSQL se habilitan únicamente contra una base **sintética aislada** con `RUN_DATABASE_TESTS=true`, `DATABASE_URL` y `STATE_ENCRYPTION_KEY` de prueba. Los tests no deben tocar la cuenta/base real. El resultado omitido no equivale a una prueba de durabilidad.

## 4. Crear repositorio privado y app, con aprobación

Revise primero el contenido: solo código, tests, manifiestos y estas guías. No publique `.env`, claves, QR, sesiones, ledgers, uploads, entornos ni node_modules. Inicialice Git **dentro de esta carpeta nueva**, añada el allowlist revisado, haga un commit convencional y cree el repositorio privado mediante `gh repo create <su-organizacion>/<nombre> --private --source=. --remote=origin`. Empuje solo ese historial limpio tras su aprobación. No copie el `.git` original.

Cree explícitamente una aplicación **Cedar** en Heroku con stack `heroku-24`, no Fir. Asigne `heroku/python` como buildpack clásico. Su `Procfile` raíz ejecuta `web: python -B -m cloud.run`; no es un comando de desarrollo ni usa reload. `$PORT` lo lee el supervisor y el proceso público escucha en `0.0.0.0:$PORT`.

Complete las Config Vars desde un canal privado seguro, no desde un archivo versionado ni comandos que queden en capturas. Use la URL de la app en `PUBLIC_ORIGIN`. Las dependencias están fijadas en los manifiestos. No hay add-ons automáticos: use únicamente un PostgreSQL externo previamente autorizado cuando corresponda. Verifique TLS y acceso restringido de esa base con su proveedor.

Solo después de revisar configuración, alcance y coste, conecte la app al repositorio privado y despliegue la rama elegida, o añada el remoto Heroku y haga el push manual aprobado. Escale a **un solo dyno web** y un solo proceso del core. No habilite autoscaling, workers extra ni despliegues automáticos antes de validar seguridad y presupuesto. El filesystem del dyno es efímero; no use SQLite para estado de seguridad.

## 5. Aceptación y operación

1. Consulte `/health`: debe responder sin datos privados. Verifique que una solicitud de chat/control sin autenticación sea rechazada.
2. Pruebe primero una consulta inocua con su propio operador. El cliente debe recibir 202 y consultar estado; no mantenga una petición bloqueada más de 30 segundos.
3. Solo si está autorizado, habilite por separado correo, pairing o sesión pagada y pruebe con destinatario/cuenta propios. Registre aceptación del proveedor separada de recepción humana o reproducción audiovisual.
4. Compruebe reinicio, reservas inciertas y limpieza con datos sintéticos antes de usar un proveedor real. Un restart borra memoria conversacional; **no** borra PostgreSQL.
5. Si hay incertidumbre, detenga operaciones y concilie. No reintente envíos ni creaciones ciegamente. Copias de seguridad y rotación de claves requieren preservar la capacidad de descifrar estado existente.

## Fuentes oficiales

- [Procfile](https://devcenter.heroku.com/articles/procfile), [Python y .python-version](https://devcenter.heroku.com/articles/python-runtimes).
- [Disco efímero y SQLite](https://devcenter.heroku.com/articles/sqlite3), [timeout HTTP](https://devcenter.heroku.com/articles/request-timeout), [apagado](https://devcenter.heroku.com/articles/dyno-shutdown-behavior).
- [Chainlit archivado](https://docs.chainlit.io/get-started/project-status), [Open WebUI](https://docs.openwebui.com/getting-started/quick-start/).

La entrega de estas fuentes no demuestra build Linux, tamaño de slug, rendimiento cloud ni integración con cuentas. Esas comprobaciones requieren un despliegue y autorización separados.
