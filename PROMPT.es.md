# El prompt

Pega esto en Claude Code (u otro asistente de programación con acceso al shell) en una computadora que esté
en la misma red Wi-Fi que el televisor. Funciona en televisores Android TV / Google TV (Xiaomi, TCL, Hisense, Sony,
OnePlus, Realme, Nvidia Shield y la mayoría de los demás). No funciona en Samsung Tizen, LG webOS ni
Fire TV. Para Samsung, LG, Roku y otros televisores que no son Android, usá https://cleanyour.tv/not-android:
desactiva el rastreo con el control remoto. Si clonaste este repositorio, mencionalo: el asistente puede reutilizar `tools/` y `launcher/`
en lugar de escribirlos desde cero, y solo necesita editar `launcher/.../values/config.xml`.

Antes de empezar, en el televisor: Configuración → Preferencias del dispositivo → Acerca de → presioná OK en "Versión de compilación" 7 veces,
luego volvé → Opciones para desarrolladores → activá la depuración USB (y la depuración de red/ADB si tu televisor
la muestra). Dejá el televisor encendido. Algunos decodificadores cortan la energía del puerto USB mientras la depuración USB está activa, así que un
parlante USB o un disco conectado a ese puerto se apaga hasta que desactivás la depuración. Un adaptador USB Ethernet
en ese puerto puede caerse de la misma manera, así que planeá hacer toda la sesión de una sola vez.

---

Quiero eliminar el bloatware de mi Android TV y reemplazar su launcher con una pantalla de inicio limpia estilo Apple TV.
Mi modelo de TV es: <NOMBRE DEL MODELO AQUÍ>. Trabajá en el dispositivo real, paso a paso, y verificá todo lo que
hacés con capturas de pantalla tomadas del televisor. Preguntame antes de hacer cualquier cosa que dependa de mis preferencias.
Donde estos pasos mencionan un archivo bajo `tools/`, `docs/` o `examples/` que no está en tu carpeta de trabajo,
estás ejecutando sin este repositorio: clonalo primero con
`git clone https://github.com/Gathin23/cleanyourtv` y trabajá desde allí, para que `tools/disable.sh` y el
resto mantengan sus controles de seguridad, en lugar de detenerte o escribir los tuyos propios.

## Conectar

- Encontrá el televisor en mi red (hostname, tabla ARP, o pedime la IP) y conectate por ADB en el puerto 5555.
  Si el televisor está en otra casa, te daré su dirección Tailscale (docs/REMOTE.md): usala,
  no escanees mi red local.
- Si el binario estándar `adb` falla con "No route to host" en macOS aunque el puerto esté abierto, es la
  privacidad de red local de macOS bloqueando adb. No lo depures: usá el paquete Python `adb-shell` en un venv
  como cliente ADB en su lugar. Si su push de archivos se cuelga con archivos grandes, transferí los archivos como chunks en base64
  a través del shell y verificá el md5.
- Si tus propios comandos no pueden alcanzar el televisor mientras responde desde una terminal ordinaria (un sandbox que
  bloquea la red local), pedime que ejecute `tools/relay.py <ip del tv>` en una terminal y lo deje corriendo, luego
  usá `TV_HOST=127.0.0.1 TV_PORT=15555` (`tools/relay.md`).
- Si el puerto 5555 permanece cerrado, el televisor puede ofrecer solo Wireless debugging (los televisores Google TV a menudo lo hacen): buscá
  `_adb-tls-connect._tcp` con `dns-sd -B` o `adb mdns services`, pedime el código y puerto bajo
  Opciones para desarrolladores → Wireless debugging → Vincular dispositivo con código de emparejamiento, luego `adb pair`, `adb connect`
  y `adb tcpip 5555`. Android desactiva Wireless debugging cuando el Wi-Fi se corta.
  Algunos firmwares ejecutan ADB de red en otro puerto fijo (un proyector usó el 5877): si 5555 rechaza y
  nada anuncia Wireless debugging, escaneá los puertos TCP del televisor y probá cada uno abierto con `TV_PORT`.
- Si el televisor resulta no ser Android TV / Google TV (sin puerto ADB en absoluto, o se identifica como Tizen,
  webOS, Roku OS, VIDAA o SmartCast), detente y decime que use https://cleanyour.tv/not-android, que
  desactiva el rastreo con el control remoto. Nada en este repositorio aplica a ese dispositivo.
- Avisame cuándo aparecerá el mensaje "¿Permitir depuración USB?" en el televisor para que pueda aceptarlo.
- Si `adb install` se cuelga en Android 14, está esperando una confirmación en pantalla; empujá el APK y ejecutá
  `pm install -r` a través del shell en su lugar.

## Hacer copia de seguridad primero

- Guardá la lista completa de paquetes, la lista de paquetes deshabilitados, la salida de getprop y todas las configuraciones en una carpeta de respaldo
  antes de cambiar cualquier cosa, y escribí un script de restauración que vuelva a habilitar todo lo que deshabilites.
- Preguntame qué está conectado a los puertos USB del televisor, y preguntame por separado si la red del televisor pasa
  por un adaptador USB Ethernet: "nada conectado" puede ser verdad mientras la red misma está en ese
  puerto. Algunos dispositivos cortan la energía mientras la depuración USB está activa, así que avisame, y recordame desactivar la
  depuración una vez que hayas terminado. En un televisor que alcanza la red por USB Ethernet, verificá antes de cambiar
  cualquier cosa: `dumpsys usb | grep host_connected` (`host_connected=false` no prueba que el adaptador
  no está: algunos televisores leen false con él aún activo como `eth0`, así que guíate por la siguiente verificación) y
  `dumpsys connectivity | grep -o 'Transports: [A-Z]*'` (`WIFI` en un televisor que llamo cableado significa que el dispositivo
  hizo fallback, y ADB está corriendo por Wi-Fi). Terminá el trabajo completo en una sola sesión: el
  puerto solo vuelve con la depuración USB desactivada, y eso cierra el puerto 5555 también. Preferí Wireless
  debugging si el televisor lo tiene.
- Cuando termines, cerrá el ADB de red en lugar de dejarlo abierto: desactivá Wireless debugging y
  la depuración de red/ADB en el televisor (según cuál tenga), y también la depuración USB a menos que te pida mantenerla,
  y revocá las autorizaciones de depuración USB. Wireless debugging tiene su propio puerto y puede
  quedar abierto cuando se desactiva la depuración USB: anotá ese puerto desde `adb mdns services`
  (`_adb-tls-connect._tcp`) antes de desactivarlo, y verificalo con
  `tools/adb-closed.py <ip del tv> <puerto>` inmediatamente después, antes del reinicio, porque toma un nuevo puerto
  cada vez que arranca. Luego reiniciá, verificá con `tools/adb-closed.py <ip del tv>` que el puerto 5555 rechaza
  la conexión, y confirmá que Wireless debugging sigue desactivado. Si 5555 sigue respondiendo mientras
  la depuración USB permanece activa, ese toggle es lo que lo mantiene abierto en este televisor: desactivalo también y verificá
  de nuevo. Solo cuenta que la herramienta diga que el puerto está cerrado, no cómo se ven los toggles ni una conexión
  que se cortó. Si la red del televisor vino por un adaptador USB Ethernet, desconectá y reconectá el adaptador
  una vez que la depuración esté desactivada —el puerto vuelve con él— y pedime confirmar que el televisor está en Ethernet
  de nuevo, no en Wi-Fi. No confíes en `nc` en macOS: la privacidad de red local también puede bloquearlo, y su "No
  route to host" no prueba nada; solo "Connection refused" prueba algo. El puerto 5555 es texto plano, y en
  firmware con `ro.adb.secure=0` (o sin configurar, en una build de depuración o Android 4.4) cualquier dispositivo en
  la LAN puede obtener un shell.

## Eliminar bloatware

- Listá los paquetes instalados y ordénalos en: telemetría/analytics del fabricante, servicios de contenido
  y publicidad del fabricante (PatchWall, filas de recomendaciones, proveedores de contenido), servicios en segundo plano que probablemente
  no necesito (duplicados de share/cast, limpiadores), apps preinstaladas, y apps de streaming.
- Deshabilitá las primeras categorías con `pm disable-user --user 0`, nunca desinstales paquetes del sistema.
- Nunca deshabilites lo que el televisor necesita para funcionar: la app de TV en vivo y los servicios de entrada que reproducen HDMI y el
  sintonizador, el menú de entrada/fuente, los servicios de control remoto y emparejamiento Bluetooth, el teclado en pantalla,
  Google Play Store y Play Services. Los nombres de paquetes del fabricante a menudo no dicen qué hace un
  paquete: verificá sus actividades y servicios con `dumpsys package` primero, y preguntame si aún no está claro.
- Nunca deshabilites los paquetes principales propios de Android, o el televisor puede no volver a arrancar: el controlador de permisos,
  el instalador de paquetes, ext services y ext shared, module metadata (cada uno como `com.android.*` o
  `com.google.android.*`, y ext services y ext shared también como el simple `android.ext.services` y
  `android.ext.shared`), `com.google.android.overlay.modules*`, `com.android.providers.*` (calendario,
  contactos, diccionario de usuario y números bloqueados aparte), `com.android.systemui`, `com.android.shell`,
  `com.android.phone`, `com.android.settings`, `com.android.tv.settings` y `android`, ni el middleware de TV
  (`com.cltv.mal`, `com.mediatek.tis`, `com.mediatek.tv.service`, `com.mediatek.tv.agent`:
  un televisor Haier reiniciaba en bucle con `com.cltv.mal` desactivado,
  [#1578](https://github.com/Gathin23/cleanyourtv/issues/1578)). Un Mi TV Stick original nunca volvió a arrancar después de que una lista tomó los primeros seis
  ([#884](https://github.com/Gathin23/cleanyourtv/issues/884)); `tools/disable.sh` rechaza tal lista.
- Antes de tocar apps de streaming, el asistente de voz, Chromecast, Miracast o el servicio de actualización, preguntame
  cuáles uso con una pregunta de lista de verificación y deshabilitá solo lo que no marco.
- Ejecutá los comandos `pm` uno por llamada al shell; los comandos encadenados pueden detenerse silenciosamente después del primero.
- Si `pm disable-user` es rechazado para todos los paquetes, detente y avisame: algunos firmwares (Fire OS 5 en un
  Fire TV Box, por ejemplo) rechazan `pm disable-user` con un `SecurityException`, `pm uninstall --user 0`
  con `DELETE_FAILED_INTERNAL_ERROR`, y `pm hide` reporta éxito sin cambiar nada. Verificá
  con `pm list packages -d` en lugar del código de salida, y no gastes la sesión reintentando — no hay
  nada para debloatear en ese dispositivo, así que recurrimos a sus propios toggles de privacidad y bloqueo DNS
  (`docs/TROUBLESHOOTING.md`).
- No lances un paquete cuyo nombre diga factory, production, AT o fac menu (`com.cvte.tv.hkcfac`,
  `com.cvte.tv.fac.menu`, `com.at.factory.*`, `mediatek.factorymenu.ui` y similares) para ver qué hace, ni siquiera en modo de solo lectura:
  en placas Haier/CVTE abrir uno activa un flag de modo fábrica que mata la tecla de Entrada y CEC, y
  hace que el próximo arranque deshabilite Play Services, Netflix y Chromecast — que el shell luego no puede
  volver a habilitar. `dumpsys package <nombre>` te dice qué es un paquete sin iniciarlo, y
  `docs/TROUBLESHOOTING.md` tiene la salida si uno ya fue abierto.
- Deshabilitá en lotes pequeños y tomá capturas entre ellos: un lote puede llevarse algo importante con
  él y no podés saber cuál.
- Después del último lote, esperá unos 15 segundos antes de reiniciar — Android escribe el estado de los paquetes en
  disco unos diez segundos después de un cambio (`WRITE_SETTINGS_DELAY`, `docs/TROUBLESHOOTING.md`), así que un
  reinicio enviado inmediatamente después del lote arranca con el estado anterior y lo que volvió se lee como
  firmware re-habilitando paquetes que nunca re-habilitó. `adb shell sync` primero también funciona. Luego reiniciá
  una vez y comparé `pm list packages -d` con lo que deshabilitaste: algunos
  firmwares vuelven a habilitar paquetes en cada arranque desde su propia lista (TCL Android 9 hace esto para su
  centro de usuarios). Anotá esos en el encabezado de la lista en lugar de deshabilitarlos de nuevo después de cada arranque. Si
  setupwraith o el launcher del sistema volvió y el Inicio está negro, revisá `logcat | grep
  RecoveryActivity` y volvé a habilitar el launcher del sistema antes que cualquier otra cosa
  (`docs/devices/acer-r4g.md`).
- Ofreceme DNS con bloqueo de publicidad como extra opcional: en Android 9 y más nuevo, DNS privado configurado en un
  resolvedor con bloqueo de anuncios (`settings put global private_dns_specifier dns.adguard-dns.com`, luego
  `settings put global private_dns_mode hostname`). Avisame que no bloquea los anuncios de YouTube, verificá que una app
  sigue reproduciendo después, y anotá el deshacer (`private_dns_mode opportunistic`) en el README.
  Preguntame primero si mi router ya filtra o enruta el tráfico por dominio a través de su propio DNS
  (Pi-hole, AdGuard Home, una VPN con listas de dominios, un proxy fake-IP): DNS privado lo evita, así que esas
  reglas dejan de aplicarse al televisor, y el bloqueo en el router es la mejor opción en ese caso.

## Launcher

- Verificá que el televisor acepta APKs antes de construir cualquier cosa. Algunos televisores del mercado chino responden a cada
  sideload con `INSTALL_FAILED_VERIFICATION_FAILURE` — `adb install`, `pm install`, un instalador iniciado a mano e incluso los propios APKs del fabricante fallan todos — y otros rechazan cualquier paquete que
  declare `android.intent.category.HOME` a menos que lleve la firma del fabricante. Si
  encontrás esto, hacé la parte de debloat, decí claramente que la parte del launcher es imposible aquí, y detené
  los reintentos de instalación. El encabezado del `examples/` correspondiente dice cuál caso es tu televisor.
- Verificá también el nivel de SDK del televisor antes de prometer el launcher: `tools/tv.py 'getprop
  ro.build.version.sdk'` contra `grep minSdk launcher/app/build.gradle` (26 = Android 8.0). Un televisor
  por debajo de ese responde `INSTALL_FAILED_OLDER_SDK`; bajar `minSdk` es un cambio de código fuente que luego
  tenés que mantener vos, y un APK reconstruido en otro lugar es algo que este repositorio no puede verificar. En esos televisores ofrecé
  la parte de debloat y decí que el launcher no puede instalarse. Sin launcher al que transferir el control, el
  del sistema se queda: `cmd package` no existe antes de Android 7, así que `tools/disable.sh` pregunta a `dumpsys
  activity` por el Inicio allí y advierte cuando ninguno responde — esa advertencia significa que nada fue verificado,
  y un televisor sin recuperación no tiene manera de volver (#795).
- No instales un launcher de terceros que cobre por funciones básicas como fondos de pantalla. Construí un pequeño launcher nativo
  de Android TV en su lugar (Java, AndroidX RecyclerView, minSdk que coincida con el televisor, la build de depuración está bien),
  instalalo por ADB, configuralo como home predeterminado y deshabilitá el launcher del sistema. Si varias apps reclaman
  el intent HOME, listalas con `cmd package query-activities -a android.intent.action.MAIN -c
  android.intent.category.HOME` y configurá el predeterminado con `cmd package set-home-activity`. Esos dos
  comandos pueden nombrar tu launcher mientras Inicio sigue abriendo otra cosa: en algunas builds de Google TV
  `set-home-activity` imprime `Success` y no cambia nada, y la `.RecoveryActivity` de setupwraith
  sigue manteniendo la tecla. Confirmá con `dumpsys activity activities | grep mFocusedApp` antes de decirme que
  la toma de control funcionó.
- Antes de deshabilitar el launcher del sistema, verificá qué otras apps reclaman HOME: en Google TV el asistente de configuración
  (`com.google.android.tungsten.setupwraith`) toma el control incluso después de que el launcher del sistema está deshabilitado, y
  el encabezado del `examples/` correspondiente dice qué hacer. Antes de deshabilitar setupwraith, ejecutá
  `dumpsys wifi | grep -o 'cname=[^ ]*'`: una red Wi-Fi guardada durante la configuración inicial le pertenece, y
  Android borra esa red en el momento en que es deshabilitado, lo que saca el televisor del Wi-Fi y ADB. Si
  ocurre, pedime que olvide la red y la vuelva a conectar en Configuración primero.
- En una placa CVTE (cualquier paquete `com.cvte.*`), dejá el launcher del sistema habilitado (`com.cvte.tv.launcher.*`)
  a menos que la carpeta `examples/` para ese modelo exacto lo deshabilite: hacé que tu launcher sea el Home con
  `set-home-activity`, reiniciá una vez, y confirmá que el Home y ADB vuelvan antes que cualquier otra cosa. No habilites un
  ayudante de teclas remotas en el mismo paso. Un JVC LT-43N7115 (`TP.SK706S.PC822`, Android 11) se quedó colgado en su animación de arranque con ADB perdido después de que ambos se hicieron antes de un reinicio (#741).
- En Google TV el launcher del sistema también responde a los botones de apps del control remoto (Netflix, YouTube y similares),
  Entrada y los botones de Configuración/panel, así que después de deshabilitarlo pedime que presione cada uno, y remapeá los que
  no hacen nada con los servicios de teclas del launcher: `input_key_keycodes` y `app_keys` con
  INPUT_KEY_SERVICE=1, `settings_key_keycodes` con HOME_KEY_SERVICE=1 (`config.xml` o el tema).
  Habilitar cualquiera de los ayudantes puede costar más que los botones que mapea: en una build TCL G09 (Google TV 12) pedime
  que mantenga presionado el volumen arriba antes y después, porque un servicio de filtrado de teclas vinculado allí descarta las repeticiones de teclas —
  un volumen que aumenta progresivamente se convierte en un paso por presión, uno o ambos ayudantes, todo o nada — así que decí cuál estoy
  sacrificando en lugar de habilitarlo silenciosamente (`docs/devices/tcl-55p71b-g09-key-repeat.md` tiene el bisect y
  las tres salidas). En otros televisores esto no fue medido; si mantener presionado un botón deja de repetir una vez que
  un ayudante está activo, es el mismo intercambio y no un control remoto roto.
  Un botón que el televisor registra como `KEY_UNKNOWN` o `KEY_PROGRAM` no puede ser emparejado por keycode, ya que todos los
  botones sin mapear lo comparten: leé el scancode con `getevent -lt` y usá `settings_key_scancodes`,
  que solo `config.xml` lleva (un tema puede configurar keycodes, no scancodes).
- Después del primer reinicio con el nuevo Home, verificá qué abre el televisor al encenderse
  (`logcat -b events -d | grep wm_set_resumed_activity`). Si el firmware pone la app de TV en vivo en pantalla por
  sí solo, preguntame en cuál quiero aterrizar, Home o TV en vivo: Home es `power_on_home` con HOME_KEY_SERVICE=1,
  TV en vivo es `boot_to_live_tv` (`config.xml` o el tema). Nunca configures ambos.
- En Android 11 y más nuevo el launcher debe declarar `<queries>` para `android.intent.category.LEANBACK_LAUNCHER`,
  o la visibilidad de paquetes oculta silenciosamente todas las apps y la grilla aparece vacía; apuntá a un SDK reciente, algunos
  televisores Google TV 14 rechazan targets más viejos en la instalación.
- Si escribís el launcher vos mismo, hacé que su tema sea explícitamente opaco (`windowIsTranslucent`,
  `windowIsFloating` y `windowSwipeToDismiss` en false): en algunos firmwares `Theme.DeviceDefault` resulta
  translúcido, la app de TV sigue corriendo bajo el Home, y después de una entrada HDMI la imagen se queda en pantalla.
- Preguntame cuántos slots del dock quiero (4, 5, 6 o 7), qué apps, y su orden; usá cuatro si no tengo
  preferencia. El launcher de referencia ya soporta esto: usá `columns` y `dock_apps` en
  `launcher/app/src/main/res/values/config.xml` o el `config.json` de un tema, sin agregar un nuevo layout.
- Diseño estilo Apple TV 4K: fondo negro puro; una fila de dock en la parte inferior de la pantalla dentro de una
  banda redondeada levemente más clara que sostiene las apps que elijo; el resto de las apps en una grilla con el mismo
  número de columnas debajo que se desplaza hacia arriba cuando presiono Abajo; un resaltado translúcido de "vidrio" que
  salta de tile en tile en lugar de bordes por tile; el tile enfocado escala levemente y
  muestra su nombre debajo; encima del dock, el nombre de la app del dock enfocada en letras grandes y claras con un
  resplandor ambiental en un color muestreado de su banner; botones de píldora "esmerilados" arriba a la derecha para Entradas, Wi-Fi
  (mostrando el nombre de la red) y Configuración; un saludo, un reloj grande y fino y la fecha arriba a la izquierda en una
  tipografía de licencia abierta descargada como Outfit. Entradas abre un menú desplegable de vidrio compacto bajo la píldora
  listando los puertos HDMI, AV y TV en vivo, cambiando a través del framework de entrada de TV.
- Hacé que la navegación con el D-pad sea determinista: Arriba/Abajo mueven exactamente una fila, Arriba desde el dock va a la barra superior,
  los extremos de la barra superior no caen hacia los tiles. Recordá el último tile enfocado.
- Mantenerlo liviano: el televisor tiene alrededor de 1 GB de RAM. Sin blur, sin video, sin polling de red.

## Verificar

- Después de cada cambio, inyectá pulsaciones de teclas remotas por ADB, tomá una captura de pantalla del televisor y mirala:
  `tools/tv.py --screenshot shots/01-después.png DPAD_RIGHT` presiona la tecla, luego captura en el televisor y
  la descarga como PNG (dejá las teclas fuera para capturar lo que ya está en pantalla).
  Arreglá lo que veas antes de continuar.
- TV en vivo, HDMI y algunas apps de streaming (Netflix) dan capturas de pantalla vacías (0 bytes); eso es el televisor, no un
  debloat roto, y `--screenshot` sale con 1 con ese mensaje. Verificá
  `dumpsys activity activities | grep -i ResumedActivity` en su lugar (algunas builds no imprimen línea `topResumedActivity`
  pero sí imprimen `mResumedActivity`; ver `docs/TROUBLESHOOTING.md`).
- Si las capturas de pantalla siguen mostrando una app que ya dejaste, byte a byte, `screencap` está devolviendo su último
  fotograma: confirmá `mCurrentFocus` en `dumpsys window`, forzá el cierre de esa app y capturá de nuevo.
- Si la pantalla se ve agrandada y recortada después de una instalación o un reinicio, verificá las anulaciones de pantalla
  antes de editar la grilla del launcher: `wm size` y `wm density` muestran un valor físico junto a una
  anulación, y una anulación sobrante de un experimento de resolución anterior, o una densidad que vuelve
  incorrecta en algunos firmwares Sony MediaTek, no es un bug del launcher. Un
  `settings get secure display_density_forced` vacío es el valor predeterminado normal, no un daño — leé los tres
  valores primero y volvelos a poner si deshacés (`docs/TROUBLESHOOTING.md`).
- Si un botón del control remoto depende de un ayudante de accesibilidad, verificá que el servicio esté habilitado y vinculado
  para el usuario actual, luego pedime que presione el botón real; una tecla inyectada no es prueba (ver
  `docs/TROUBLESHOOTING.md`).
- Cuando termines, dame un script de restauración, un script de construcción e instalación, y un README que explique cómo
  volver a habilitar cualquier app y cómo cambiar el orden del dock o el fondo de pantalla.

---

Esperá responder tres o cuatro preguntas de lista de verificación (qué apps usás, el tamaño del dock y el orden de las apps,
si querés mantener el asistente de voz, Chromecast y las actualizaciones de firmware). Todo es reversible.

