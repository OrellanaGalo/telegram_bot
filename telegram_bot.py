from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timedelta, time
from contrasenias import TOKEN

fechas_importantes = {}
recordatorios = []

async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    mensaje_bienvenida = "¡Bienvenido al Bot de Recordatorios!\n\n"
    mensaje_bienvenida += "Este bot te permite guardar eventos importantes y establecer recordatorios para esas fechas.\n\n"
    mensaje_bienvenida += "Puedes usar los siguientes comandos:\n"
    mensaje_bienvenida += "/guardar <fecha> <evento>: Guarda un evento para una fecha específica (formato: DD-MM-YYYY).\n"
    mensaje_bienvenida += "/fecha: Muestra las fechas guardadas y sus eventos asociados.\n"
    mensaje_bienvenida += "/borrar <fecha>: Elimina todos los eventos para una fecha específica (formato: DD-MM-YYYY).\n"
    mensaje_bienvenida += "/recordatorio <hora> <mensaje>: Establece un recordatorio para una hora específica (formato: HH:MM).\n"
    mensaje_bienvenida += "/ver_recordatorios: Muestra la lista de recordatorios establecidos.\n"
    mensaje_bienvenida += "/borrar_recordatorio <indice>: Elimina un recordatorio específico por su índice en la lista.\n"
    mensaje_bienvenida += "¡Espero que encuentres útil este bot! 😊"

    await update.message.reply_text(mensaje_bienvenida)

async def guardar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	# Obtener los argumentos del mensaje.
	args = context.args

	# Verificar si se proporcionaron argumentos.
	if len(args) < 2:
		await update.message.reply_text("Formato incorrecto. Uso: /guardar <fecha> <evento>")
		return

	# Parsea la fecha y el evento.
	fecha_str = args[0]
	evento = ' '.join(args[1:])

	try:
		# Parsea la fecha en el formato DD-MM-YYYY
		fecha = datetime.strptime(fecha_str, "%d-%m-%Y").date()

		# Verifica si la fecha es futura y no esta en el pasado
		hoy = datetime.now().date()

		if fecha >= hoy:
		# Guarda el evento para la fecha
			if fecha not in fechas_importantes:
				fechas_importantes[fecha] = []
			fechas_importantes[fecha].append(evento)

			await update.message.reply_text(f'Evento {evento} guardado para la fecha: {fecha_str}.')
		else:
			await update.message.reply_text("No podes guardar eventos en fechas pasadas.")
	except ValueError:
		await update.message.reply_text("Formato de fecha incorrecto. Uso: DD-MM-YYYY")

async def fecha(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
	# Ordenar fechas por proximidad a la fecha actual
	fechas_ordenadas = sorted(fechas_importantes.keys())

	# Verifica si hay fechas guardadas
	if not fechas_importantes:
		await update.message.reply_text('No hay fechas guardadas.')
		return

	# Construye el mesaje con las fechas guardadas
	mensaje = 'Fechas guardadas:\n'
	for fecha in fechas_ordenadas:
		eventos = fechas_importantes[fecha]
		mensaje += f'{fecha.strftime("%d-%m-%Y")}:\n'
		for evento in eventos:
			mensaje += f'  - {evento}\n'

	await update.message.reply_text(mensaje)

async def limpiar_fechas_pasadas(context: ContextTypes.DEFAULT_TYPE) -> None:
	hoy = datetime.now().date()
	fecha_limite = hoy - timedelta(days=30)
	fechas_a_eliminar = [fecha for fecha in fechas_importantes if fecha < fecha_limite]
	for fecha in fechas_a_eliminar:
		del fechas_importantes[fecha]

async def verificar_eventos_hoy(context: ContextTypes.DEFAULT_TYPE) -> None:
	hoy = datetime.now().date()
	if hoy in fechas_importantes:
		eventos_hoy = fechas_importantes[hoy]
		mensaje = f'Eventos para hoy ({hoy.strftime("%d-%m-%Y")}):\n'
		for evento in eventos_hoy:
			mensaje += f'- {evento}\n'
		await context.bot.send_message(chat_id=context.job.context, text=mensaje)

async def borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	# Obtener el argumento del mensaje.
	fecha_str = context.args[0]

	try:
		# Parsea la fecha en el formato DD-MM-YYYY
		fecha = datetime.strptime(fecha_str, "%d-%m-%Y").date()

		# Verifica si la fecha esta en el diccionario y la elimina.
		if fecha in fechas_importantes:
			del fechas_importantes[fecha]
			await update.message.reply_text(f'Todos los eventos para la fecha {fecha_str} fueron eliminados.')
		else:
			await update.message.reply_text(f'Fecha {fecha_str} no encontrada.')
	except ValueError:
		await update.message.reply_text("Formato de fecha incorrecto. Uso: DD-MM-YYYY")

async def establecer_recordatorio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Obtener los argumentos del mensaje
    args = context.args

    # Verificar si se proporcionaron argumentos.
    if len(args) < 2:
        await update.message.reply_text("Formato incorrecto. Uso: /recordatorio <hora> <mensaje>")
        return

    # Parsea la hora y el mensaje del recordatorio.
    hora_str = args[0]
    mensaje = ' '.join(args[1:])

    try:
        # Parsea la hora en el formato HH:MM
        hora = datetime.strptime(hora_str, "%H:%M").time()

        # Establece el recordatorio para la hora especificada
        recordatorio = (hora, mensaje)
        recordatorios.append(recordatorio)

        await update.message.reply_text(f'Recordatorio establecido para las {hora_str} - {mensaje}')
    except ValueError:
        await update.message.reply_text("Formato de hora incorrecto. Uso: HH-MM")

async def enviar_recordatorios(context: ContextTypes.DEFAULT_TYPE) -> None:
	ahora = datetime.now().date()

	# Verificar si ya pasaron al menos 2 horas desde el ultimo recordatorio.
	if recordatorios and ahora.hour % 2 == 0 and ahora.minute == 0:
		mensaje = recordatorios.pop(0) # Obtener el primer recordatorio de la lista.
		await context.bot.send_message(chat_id=context.job.context, text=f'Recordatorio: {mensaje}')

async def ver_recordatorios(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if recordatorios:
        mensaje = "Lista de recordatorios:\n"
        for indice, (horario, recordatorio) in enumerate(recordatorios, start=1):
            mensaje += f"[{indice}]: {horario.strftime('%H:%M')} - {recordatorio}\n"
        await update.message.reply_text(mensaje)
    else:
        mensaje = "No hay recordatorios guardados."
        await update.message.reply_text(mensaje)

async def borrar_recordatorio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	# Obtener el argumento del mensaje.
	args = context.args

	# Verificar si se proporciono un argumento.
	if not args:
		await update.message.reply_text("Formato incorrecto. Uso: /borrar_argumento <indice>")
		return

	try:
		# Parsear el indice del argumento.
		indice = int(args[0])

		# Verificar si el indice es valido.
		if 1 <= indice <= len(recordatorios):
			# Eliminar el recordatorio del indice especificado.
			mensaje_borrado = recordatorios.pop(indice - 1)
			await update.message.reply_text(f'Recordatorio "{mensaje_borrado}" eliminado.')
		else:
			await update.message.reply_text("Indice invalido. No se encontro ningun recordatorio con ese indice.")
	except ValueError:
		await update.message.reply_text("Formato de indice incorrecto. Debe ser un numero entero.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("guardar", guardar))
app.add_handler(CommandHandler("fecha", fecha))
app.add_handler(CommandHandler("borrar", borrar))
app.add_handler(CommandHandler("recordatorio", establecer_recordatorio))
app.add_handler(CommandHandler("borrar_recordatorio", borrar_recordatorio))
app.add_handler(CommandHandler("ver_recordatorios", ver_recordatorios))

hora_limpiar = time(hour=0, minute=0, second=0)
hora_verificar = time(hour=1, minute=0, second=0)
hora_enviar = time(hour=2, minute=0, second=0)

# Configurar un trabajo programado para limpiar eventos pasados cada día
app.job_queue.run_daily(limpiar_fechas_pasadas, time=hora_limpiar)
app.job_queue.run_daily(verificar_eventos_hoy, time=hora_verificar)
app.job_queue.run_daily(enviar_recordatorios, time=hora_enviar)

app.run_polling()
