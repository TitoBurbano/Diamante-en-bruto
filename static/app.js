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

/* ============ CRUD genérico (joyas, clientes, proveedores, categorías, empleados) ============ */
const ESTADOS_JOYA = ["DISPONIBLE", "VENDIDA", "EMPENADA", "DEVUELTA"];
const rel = (ruta, valor, texto) => ({ ruta, valor, texto }); // select alimentado por la API

const ENTIDADES = {
  joyas: {
    ruta: "/joyas", id: "id_joya", titulo: "Joyas",
    campos: [
      { n: "codigo", t: "Código", tipo: "text", req: true },
      { n: "nombre", t: "Nombre", tipo: "text", req: true },
      { n: "id_categoria", t: "Categoría", tipo: "select", req: true, opciones: rel("/categorias", "id_categoria", "nombre") },
      { n: "id_material", t: "Material", tipo: "select", req: true, opciones: rel("/materiales", "id_material", (m) => `${m.nombre} ${m.pureza}`) },
      { n: "id_proveedor", t: "Proveedor", tipo: "select", opciones: rel("/proveedores", "id_proveedor", "nombre") },
      { n: "peso_gramos", t: "Peso (g)", tipo: "number", req: true },
      { n: "quilates", t: "Quilates", tipo: "number" },
      { n: "precio_compra", t: "Precio de compra", tipo: "number", req: true, dinero: true },
      { n: "precio_venta", t: "Precio de venta", tipo: "number", req: true, dinero: true },
      { n: "estado", t: "Estado", tipo: "select", req: true, opciones: ESTADOS_JOYA },
    ],
    columnas: ["codigo", "nombre", "id_categoria", "id_material", "precio_venta", "estado"],
  },
  clientes: {
    ruta: "/clientes", id: "id_cliente", titulo: "Clientes",
    campos: [
      { n: "documento", t: "Documento", tipo: "text", req: true },
      { n: "nombre", t: "Nombre", tipo: "text", req: true },
      { n: "telefono", t: "Teléfono", tipo: "text" },
      { n: "email", t: "Correo", tipo: "text" },
      { n: "es_vip", t: "Cliente VIP", tipo: "checkbox" },
    ],
    columnas: ["documento", "nombre", "telefono", "email", "es_vip"],
  },
  proveedores: {
    ruta: "/proveedores", id: "id_proveedor", titulo: "Proveedores",
    campos: [
      { n: "nombre", t: "Nombre", tipo: "text", req: true },
      { n: "nit", t: "NIT", tipo: "text", req: true },
      { n: "telefono", t: "Teléfono", tipo: "text" },
      { n: "email", t: "Correo", tipo: "text" },
      { n: "ciudad", t: "Ciudad", tipo: "text" },
    ],
    columnas: ["nombre", "nit", "telefono", "email", "ciudad"],
  },
  categorias: {
    ruta: "/categorias", id: "id_categoria", titulo: "Categorías",
    campos: [
      { n: "nombre", t: "Nombre", tipo: "text", req: true },
      { n: "descripcion", t: "Descripción", tipo: "text" },
    ],
    columnas: ["nombre", "descripcion"],
  },
  empleados: {
    ruta: "/empleados", id: "id_empleado", titulo: "Empleados",
    campos: [
      { n: "nombre", t: "Nombre", tipo: "text", req: true },
      { n: "cargo", t: "Cargo", tipo: "select", req: true, opciones: ["VENDEDOR", "ADMINISTRADOR", "AVALUADOR"] },
      { n: "email", t: "Correo", tipo: "text", req: true },
      { n: "activo", t: "Activo", tipo: "checkbox", def: true },
    ],
    columnas: ["nombre", "cargo", "email", "activo"],
  },
};

async function crud(cfg) {
  // Listas de las tablas relacionadas: llenan los select y permiten mostrar nombres en vez de ids.
  const rels = {};
  for (const c of cfg.campos) {
    if (c.tipo === "select" && !Array.isArray(c.opciones)) rels[c.n] = await api("GET", c.opciones.ruta);
  }
  let filas = [];
  let editando = null;

  const textoRel = (c, o) => (typeof c.opciones.texto === "function" ? c.opciones.texto(o) : o[c.opciones.texto]);

  function celda(c, v) {
    if (v == null) return "—";
    if (c.tipo === "checkbox") return v ? "Sí" : "No";
    if (c.dinero) return dinero(v);
    if (c.tipo === "select" && !Array.isArray(c.opciones)) {
      const o = rels[c.n].find((x) => x[c.opciones.valor] === v);
      return o ? textoRel(c, o) : v;
    }
    return v;
  }

  function campoHtml(c) {
    if (c.tipo === "checkbox") {
      return `<label class="check"><input type="checkbox" name="${c.n}" ${c.def ? "checked" : ""}> ${c.t}</label>`;
    }
    const req = c.req ? "required" : "";
    const titulo = `${c.t}${c.req ? " *" : ""}`;
    if (c.tipo === "select") {
      const vacio = c.req ? "" : "(ninguno)";
      const opciones = Array.isArray(c.opciones)
        ? c.opciones.map((v) => `<option value="${v}">${v}</option>`).join("")
        : opcionesHtml(rels[c.n], c.opciones.valor, (o) => textoRel(c, o));
      return `<label>${titulo}<select name="${c.n}" ${req}>${vacio ? `<option value="">${vacio}</option>` : ""}${opciones}</select></label>`;
    }
    const tipo = c.tipo === "number" ? 'type="number" step="any" min="0"' : 'type="text"';
    return `<label>${titulo}<input name="${c.n}" ${tipo} ${req}></label>`;
  }

  function leerForm(form) {
    const datos = {};
    for (const c of cfg.campos) {
      const el = form.elements[c.n];
      if (c.tipo === "checkbox") datos[c.n] = el.checked;
      else if (c.tipo === "number") datos[c.n] = el.value === "" ? null : Number(el.value);
      else if (c.tipo === "select" && !Array.isArray(c.opciones)) datos[c.n] = el.value === "" ? null : Number(el.value);
      else datos[c.n] = el.value.trim() === "" ? null : el.value.trim();
    }
    return datos;
  }

  async function guardar(ev) {
    ev.preventDefault();
    try {
      const datos = leerForm(ev.target);
      if (editando) {
        await api("PUT", `${cfg.ruta}/${editando}`, datos);
        avisar("Registro actualizado.", "ok");
      } else {
        await api("POST", cfg.ruta, datos);
        avisar("Registro creado.", "ok");
      }
      editando = null;
      await pintar();
    } catch (e) {
      avisar(e.message, "error"); // el formulario se conserva para corregir
    }
  }

  async function pintar() {
    filas = await api("GET", cfg.ruta);
    const columnas = [["ID", (f) => f[cfg.id]]].concat(cfg.columnas.map((n) => {
      const c = cfg.campos.find((x) => x.n === n);
      return [c.t, (f) => celda(c, f[n])];
    }));
    vista.innerHTML = `
      <h2>${cfg.titulo}</h2>
      <form id="form" class="form">
        <h3 id="form-titulo">Nuevo registro</h3>
        <div class="campos">${cfg.campos.map(campoHtml).join("")}</div>
        <div class="botones">
          <button type="submit" class="primario">Guardar</button>
          <button type="button" data-accion="cancelar">Cancelar</button>
        </div>
      </form>
      ${tabla(columnas, filas, (f) => btn("editar", f[cfg.id], "Editar") + btn("eliminar", f[cfg.id], "Eliminar", "peligro"))}`;
    $("#form").addEventListener("submit", guardar);
  }

  acciones = {
    editar: (id) => {
      const fila = filas.find((x) => String(x[cfg.id]) === id);
      const form = $("#form");
      for (const c of cfg.campos) {
        const el = form.elements[c.n];
        if (c.tipo === "checkbox") el.checked = !!fila[c.n];
        else el.value = fila[c.n] ?? "";
      }
      editando = id;
      $("#form-titulo").textContent = `Editando registro #${id}`;
      form.scrollIntoView({ behavior: "smooth" });
    },
    cancelar: () => {
      editando = null;
      $("#form").reset();
      $("#form-titulo").textContent = "Nuevo registro";
    },
    eliminar: async (id) => {
      if (!confirm("¿Eliminar este registro?")) return;
      try {
        await api("DELETE", `${cfg.ruta}/${id}`);
        avisar("Registro eliminado.", "ok");
        await pintar();
      } catch (e) {
        avisar(e.message, "error"); // por ejemplo: 409 si otros registros dependen de este
      }
    },
  };
  await pintar();
}

registrar("joyas", "Joyas", () => crud(ENTIDADES.joyas));
registrar("clientes", "Clientes", () => crud(ENTIDADES.clientes));
registrar("proveedores", "Proveedores", () => crud(ENTIDADES.proveedores));
registrar("categorias", "Categorías", () => crud(ENTIDADES.categorias));
registrar("empleados", "Empleados", () => crud(ENTIDADES.empleados));

/* ===================== Nueva venta (caso de uso principal) ===================== */
async function vistaVender() {
  const [clientes, empleados, joyas] = await Promise.all([
    api("GET", "/clientes"), api("GET", "/empleados"), api("GET", "/joyas"),
  ]);
  const seleccion = new Set(); // ids de las joyas marcadas

  vista.innerHTML = `
    <h2>Nueva venta</h2>
    <form id="form" class="form">
      <div class="campos">
        <label>Cliente *<select name="cliente" required>
          ${opcionesHtml(clientes, "id_cliente", (c) => c.nombre + (c.es_vip ? " ⭐ VIP" : ""))}
        </select></label>
        <label>Empleado *<select name="empleado" required>
          ${opcionesHtml(empleados, "id_empleado", (e) => e.nombre + (e.activo ? "" : " (inactivo)"))}
        </select></label>
      </div>
      <label class="check" style="margin-top:12px">
        <input type="checkbox" id="solo-disp"> Mostrar solo joyas disponibles
      </label>
      <p class="resumen">Con el filtro apagado puedes marcar una joya no disponible para ver cómo la API rechaza la venta completa.</p>
      <div id="lista-joyas"></div>
      <p id="resumen" class="resumen"></p>
      <div class="botones"><button type="submit" class="primario">Registrar venta</button></div>
    </form>`;

  function resumir() {
    const marcadas = joyas.filter((j) => seleccion.has(j.id_joya));
    const subtotal = marcadas.reduce((s, j) => s + j.precio_venta, 0);
    $("#resumen").textContent = marcadas.length
      ? `${marcadas.length} joya(s) · subtotal estimado ${dinero(subtotal)} (el descuento VIP lo calcula la API)`
      : "Selecciona al menos una joya.";
  }

  function pintarJoyas() {
    const soloDisp = $("#solo-disp").checked;
    const visibles = joyas.filter((j) => !soloDisp || j.estado === "DISPONIBLE");
    const filas = visibles.map((j) => `<tr>
      <td><input type="checkbox" data-joya="${j.id_joya}" ${seleccion.has(j.id_joya) ? "checked" : ""}></td>
      <td>${esc(j.codigo)}</td><td>${esc(j.nombre)}</td><td>${dinero(j.precio_venta)}</td>
      <td><span class="estado ${j.estado}">${j.estado}</span></td></tr>`).join("");
    $("#lista-joyas").innerHTML = `<div class="tabla-wrap"><table>
      <thead><tr><th></th><th>Código</th><th>Joya</th><th>Precio</th><th>Estado</th></tr></thead>
      <tbody>${filas}</tbody></table></div>`;
    resumir();
  }

  $("#solo-disp").addEventListener("change", pintarJoyas);
  $("#lista-joyas").addEventListener("change", (e) => {
    const id = Number(e.target.dataset.joya);
    if (e.target.checked) seleccion.add(id); else seleccion.delete(id);
    resumir();
  });
  $("#form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    if (!seleccion.size) return avisar("Selecciona al menos una joya.", "error");
    const f = ev.target.elements;
    try {
      const v = await api("POST", "/ventas", {
        id_cliente: Number(f.cliente.value),
        id_empleado: Number(f.empleado.value),
        ids_joyas: [...seleccion],
      });
      avisar(`Venta #${v.id_venta} registrada. Total: ${dinero(v.total)} (descuento: ${dinero(v.descuento)}).`, "ok");
      await vistaVender(); // recarga la lista con los nuevos estados
    } catch (e) {
      avisar(e.message, "error"); // se conserva la selección; en la base no quedó nada guardado
    }
  });
  pintarJoyas();
}

/* ===================== Historial de ventas ===================== */
async function vistaVentas() {
  const filas = await api("GET", "/ventas");
  vista.innerHTML = `
    <h2>Ventas</h2>
    ${tabla([
      ["ID", (f) => f.id_venta],
      ["Fecha", (f) => f.fecha.replace("T", " ").slice(0, 16)],
      ["Cliente", (f) => f.cliente],
      ["Empleado", (f) => f.empleado],
      ["Descuento", (f) => dinero(f.descuento)],
      ["Total", (f) => dinero(f.total)],
      ["Estado", (f) => f.estado],
    ], filas, (f) => btn("detalle", f.id_venta, "Ver detalle") +
      (f.estado === "COMPLETADA" ? btn("anular", f.id_venta, "Anular", "peligro") : ""))}
    <div id="detalle"></div>`;

  acciones = {
    detalle: async (id) => {
      try {
        const v = await api("GET", `/ventas/${id}`);
        $("#detalle").innerHTML = `<h3>Venta #${v.id_venta}</h3>` +
          (v.motivo_anulacion ? `<p>Motivo de anulación: ${esc(v.motivo_anulacion)}</p>` : "") +
          tabla([["Código", (d) => d.codigo], ["Joya", (d) => d.joya], ["Precio", (d) => dinero(d.precio_unitario)]], v.detalle);
      } catch (e) {
        avisar(e.message, "error");
      }
    },
    anular: async (id) => {
      const motivo = prompt("Motivo de la anulación (mínimo 5 caracteres):");
      if (motivo === null) return;
      try {
        await api("POST", `/ventas/${id}/anular`, { motivo });
        avisar(`Venta #${id} anulada; sus joyas volvieron al inventario.`, "ok");
        await vistaVentas();
      } catch (e) {
        avisar(e.message, "error");
      }
    },
  };
}

registrar("vender", "Nueva venta", vistaVender);
registrar("ventas", "Ventas", vistaVentas);

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