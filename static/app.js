"use strict";

/* ===================== Utilidades ===================== */
const $ = (selector) => document.querySelector(selector);
const vista = $("#vista");
let acciones = {}; // manejadores de los botones de la vista actual (data-accion)

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const dinero = (n) => Number(n).toLocaleString("es-CO",
  { style: "currency", currency: "COP", maximumFractionDigits: 0 });
const MONEDA = /precio|monto|total|descuento|costo|pagado/;

/* Muestra un aviso arriba: verde si salió bien, rojo si la API devolvió un error. */
function avisar(texto, tipo = "ok") {
  const caja = $("#mensaje");
  caja.textContent = texto;
  caja.className = tipo;
  caja.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* Convierte la respuesta de error de la API en un texto legible para el usuario. */
function textoError(estado, datos) {
  let detalle = datos && datos.detail;
  if (Array.isArray(detalle)) { // errores de validación (422) de FastAPI
    detalle = detalle.map((e) => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`).join(" · ");
  }
  return `Error ${estado}: ${detalle || "respuesta inesperada del servidor"}`;
}

/* Llama a la API. Si responde con error, lanza una excepción con el mensaje de la API. */
async function api(metodo, ruta, cuerpo) {
  let resp;
  try {
    resp = await fetch(ruta, {
      method: metodo,
      headers: cuerpo ? { "Content-Type": "application/json" } : {},
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
  } catch {
    throw new Error("No se pudo conectar con la API. ¿Está corriendo el servidor?");
  }
  if (resp.status === 204) return null;
  const datos = await resp.json().catch(() => null);
  if (!resp.ok) throw new Error(textoError(resp.status, datos));
  return datos;
}

/* ===================== Componentes ===================== */
const btn = (accion, id, texto, clase = "") =>
  `<button type="button" class="${clase}" data-accion="${accion}" data-id="${esc(id)}">${texto}</button>`;

/* columnas: [[titulo, (fila) => valor]]; botones: (fila) => html de los botones de la fila */
function tabla(columnas, filas, botones) {
  if (!filas.length) return "<p class='vacio'>No hay registros.</p>";
  const cabecera = columnas.map(([t]) => `<th>${esc(t)}</th>`).join("") + (botones ? "<th></th>" : "");
  const cuerpo = filas.map((f) =>
    "<tr>" + columnas.map(([, valor]) => `<td>${esc(valor(f))}</td>`).join("") +
    (botones ? `<td class="acciones">${botones(f)}</td>` : "") + "</tr>").join("");
  return `<div class="tabla-wrap"><table><thead><tr>${cabecera}</tr></thead><tbody>${cuerpo}</tbody></table></div>`;
}

/* Tabla automática: usa las claves del primer registro como columnas. */
function tablaAuto(filas) {
  if (!filas.length) return "<p class='vacio'>Sin resultados.</p>";
  const formato = (k, v) => {
    if (v == null) return "—";
    if (typeof v === "boolean") return v ? "Sí" : "No";
    if (typeof v === "number" && MONEDA.test(k)) return dinero(v);
    return v;
  };
  return tabla(Object.keys(filas[0]).map((k) => [k.replaceAll("_", " "), (f) => formato(k, f[k])]), filas);
}

const opcionesHtml = (lista, valor, texto, vacio) =>
  (vacio ? `<option value="">${vacio}</option>` : "") +
  lista.map((o) => `<option value="${esc(o[valor])}">${esc(typeof texto === "function" ? texto(o) : o[texto])}</option>`).join("");

/* ===================== Navegación ===================== */
const MENU = [];   // [clave, título] en el orden en que se registran
const VISTAS = {}; // clave -> función que dibuja la sección

function registrar(clave, titulo, funcion) {
  MENU.push([clave, titulo]);
  VISTAS[clave] = funcion;
}

async function ir(clave) {
  if (!VISTAS[clave]) clave = MENU[0][0];
  $("#mensaje").hidden = true;
  acciones = {};
  document.querySelectorAll("#menu button").forEach((b) =>
    b.classList.toggle("activo", b.dataset.vista === clave));
  history.replaceState(null, "", "#" + clave);
  try {
    await VISTAS[clave]();
  } catch (e) {
    avisar(e.message, "error");
  }
}

// ===== ARRANQUE (agrega las secciones nuevas ARRIBA de esta línea) =====
if (MENU.length) {
  $("#menu").innerHTML = MENU.map(([k, t]) => `<button data-vista="${k}">${t}</button>`).join("");
  $("#menu").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-vista]");
    if (b) ir(b.dataset.vista);
  });
  vista.addEventListener("click", (e) => {
    const b = e.target.closest("[data-accion]");
    if (b && acciones[b.dataset.accion]) acciones[b.dataset.accion](b.dataset.id);
  });
  ir(location.hash.slice(1));
} else {
  vista.textContent = "Interfaz en construcción…";
}