const SHELL_LINKS = [
	{ href: "dashboard.html", label: "Dashboard" },
	{ href: "data-form.html", label: "Register" },
	{ href: "admin.html", label: "Admin" },
	{ href: "jobs.html", label: "Jobs" },
];

function syncSessionTokenFromBody() {
	const token = document.body?.dataset?.sessionToken;
	if (token) localStorage.setItem("authToken", token);
}

const counties = [
	{
		name: "Mombasa",
		code: 1,
	},
	{
		name: "Kwale",
		code: 2,
	},
	{
		name: "Kilifi",
		code: 3,
	},
	{
		name: "Tana River",
		code: 4,
	},
	{
		name: "Lamu",
		code: 5,
	},
	{
		name: "Taita-Taveta",
		code: 6,
		capital: "Voi",
	},
	{
		name: "Garissa",
		code: 7,
	},
	{
		name: "Wajir",
		code: 8,
	},
	{
		name: "Mandera",
		code: 9,
	},
	{
		name: "Marsabit",
		code: 10,
	},
	{
		name: "Isiolo",
		code: 11,
	},
	{
		name: "Meru",
		code: 12,
	},
	{
		name: "Tharaka-Nithi",
		code: 13,
	},
	{
		name: "Embu",
		code: 14,
	},
	{
		name: "Kitui",
		code: 15,
	},
	{
		name: "Machakos",
		code: 16,
	},
	{
		name: "Makueni",
		code: 17,
	},
	{
		name: "Nyandarua",
		code: 18,
	},
	{
		name: "Nyeri",
		code: 19,
	},
	{
		name: "Kirinyaga",
		code: 20,
	},
	{
		name: "Murang'a",
		code: 21,
	},
	{
		name: "Kiambu",
		code: 22,
	},
	{
		name: "Turkana",
		code: 23,
	},
	{
		name: "West Pokot",
		code: 24,
	},
	{
		name: "Samburu",
		code: 25,
	},
	{
		name: "Trans-Nzoia",
		code: 26,
	},
	{
		name: "Uasin Gishu",
		code: 27,
	},
	{
		name: "Elgeyo-Marakwet",
		code: 28,
	},
	{
		name: "Nandi",
		code: 29,
	},
	{
		name: "Baringo",
		code: 30,
	},
	{
		name: "Laikipia",
		code: 31,
	},
	{
		name: "Nakuru",
		code: 32,
	},
	{
		name: "Narok",
		code: 33,
	},
	{
		name: "Kajiado",
		code: 34,
	},
	{
		name: "Kericho",
		code: 35,
	},
	{
		name: "Bomet",
		code: 36,
	},
	{
		name: "Kakamega",
		code: 37,
	},
	{
		name: "Vihiga",
		code: 38,
	},
	{
		name: "Bungoma",
		code: 39,
	},
	{
		name: "Busia",
		code: 40,
	},
	{
		name: "Siaya",
		code: 41,
	},
	{
		name: "Kisumu",
		code: 42,
	},
	{
		name: "Homa Bay",
		code: 43,
	},
	{
		name: "Migori",
		code: 44,
	},
	{
		name: "Kisii",
		code: 45,
	},
	{
		name: "Nyamira",
		code: 46,
	},
	{
		name: "Nairobi",
		code: 47,
	},
];

const countries = [
	{ value: "KE", label: "Kenya" },
	{ value: "AF", label: "Afghanistan" },
	{ value: "AX", label: "Åland Islands" },
	{ value: "AL", label: "Albania" },
	{ value: "DZ", label: "Algeria" },
	{ value: "AS", label: "American Samoa" },
	{ value: "AD", label: "Andorra" },
	{ value: "AO", label: "Angola" },
	{ value: "AI", label: "Anguilla" },
	{ value: "AQ", label: "Antarctica" },
	{ value: "AG", label: "Antigua and Barbuda" },
	{ value: "AR", label: "Argentina" },
	{ value: "AM", label: "Armenia" },
	{ value: "AW", label: "Aruba" },
	{ value: "AU", label: "Australia" },
	{ value: "AT", label: "Austria" },
	{ value: "AZ", label: "Azerbaijan" },
	{ value: "BS", label: "Bahamas" },
	{ value: "BH", label: "Bahrain" },
	{ value: "BD", label: "Bangladesh" },
	{ value: "BB", label: "Barbados" },
	{ value: "BY", label: "Belarus" },
	{ value: "BE", label: "Belgium" },
	{ value: "BZ", label: "Belize" },
	{ value: "BJ", label: "Benin" },
	{ value: "BM", label: "Bermuda" },
	{ value: "BT", label: "Bhutan" },
	{ value: "BO", label: "Bolivia, Plurinational State of" },
	{ value: "BQ", label: "Bonaire, Sint Eustatius and Saba" },
	{ value: "BA", label: "Bosnia and Herzegovina" },
	{ value: "BW", label: "Botswana" },
	{ value: "BV", label: "Bouvet Island" },
	{ value: "BR", label: "Brazil" },
	{ value: "IO", label: "British Indian Ocean Territory" },
	{ value: "BN", label: "Brunei Darussalam" },
	{ value: "BG", label: "Bulgaria" },
	{ value: "BF", label: "Burkina Faso" },
	{ value: "BI", label: "Burundi" },
	{ value: "KH", label: "Cambodia" },
	{ value: "CM", label: "Cameroon" },
	{ value: "CA", label: "Canada" },
	{ value: "CV", label: "Cape Verde" },
	{ value: "KY", label: "Cayman Islands" },
	{ value: "CF", label: "Central African Republic" },
	{ value: "TD", label: "Chad" },
	{ value: "CL", label: "Chile" },
	{ value: "CN", label: "China" },
	{ value: "CX", label: "Christmas Island" },
	{ value: "CC", label: "Cocos (Keeling) Islands" },
	{ value: "CO", label: "Colombia" },
	{ value: "KM", label: "Comoros" },
	{ value: "CG", label: "Congo" },
	{ value: "CD", label: "Congo, the Democratic Republic of the" },
	{ value: "CK", label: "Cook Islands" },
	{ value: "CR", label: "Costa Rica" },
	{ value: "CI", label: "Côte d'Ivoire" },
	{ value: "HR", label: "Croatia" },
	{ value: "CU", label: "Cuba" },
	{ value: "CW", label: "Curaçao" },
	{ value: "CY", label: "Cyprus" },
	{ value: "CZ", label: "Czech Republic" },
	{ value: "DK", label: "Denmark" },
	{ value: "DJ", label: "Djibouti" },
	{ value: "DM", label: "Dominica" },
	{ value: "DO", label: "Dominican Republic" },
	{ value: "EC", label: "Ecuador" },
	{ value: "EG", label: "Egypt" },
	{ value: "SV", label: "El Salvador" },
	{ value: "GQ", label: "Equatorial Guinea" },
	{ value: "ER", label: "Eritrea" },
	{ value: "EE", label: "Estonia" },
	{ value: "ET", label: "Ethiopia" },
	{ value: "FK", label: "Falkland Islands (Malvinas)" },
	{ value: "FO", label: "Faroe Islands" },
	{ value: "FJ", label: "Fiji" },
	{ value: "FI", label: "Finland" },
	{ value: "FR", label: "France" },
	{ value: "GF", label: "French Guiana" },
	{ value: "PF", label: "French Polynesia" },
	{ value: "TF", label: "French Southern Territories" },
	{ value: "GA", label: "Gabon" },
	{ value: "GM", label: "Gambia" },
	{ value: "GE", label: "Georgia" },
	{ value: "DE", label: "Germany" },
	{ value: "GH", label: "Ghana" },
	{ value: "GI", label: "Gibraltar" },
	{ value: "GR", label: "Greece" },
	{ value: "GL", label: "Greenland" },
	{ value: "GD", label: "Grenada" },
	{ value: "GP", label: "Guadeloupe" },
	{ value: "GU", label: "Guam" },
	{ value: "GT", label: "Guatemala" },
	{ value: "GG", label: "Guernsey" },
	{ value: "GN", label: "Guinea" },
	{ value: "GW", label: "Guinea-Bissau" },
	{ value: "GY", label: "Guyana" },
	{ value: "HT", label: "Haiti" },
	{ value: "HM", label: "Heard Island and McDonald Islands" },
	{ value: "VA", label: "Holy See (Vatican City State)" },
	{ value: "HN", label: "Honduras" },
	{ value: "HK", label: "Hong Kong" },
	{ value: "HU", label: "Hungary" },
	{ value: "IS", label: "Iceland" },
	{ value: "IN", label: "India" },
	{ value: "ID", label: "Indonesia" },
	{ value: "IR", label: "Iran, Islamic Republic of" },
	{ value: "IQ", label: "Iraq" },
	{ value: "IE", label: "Ireland" },
	{ value: "IM", label: "Isle of Man" },
	{ value: "IL", label: "Israel" },
	{ value: "IT", label: "Italy" },
	{ value: "JM", label: "Jamaica" },
	{ value: "JP", label: "Japan" },
	{ value: "JE", label: "Jersey" },
	{ value: "JO", label: "Jordan" },
	{ value: "KZ", label: "Kazakhstan" },
	{ value: "KI", label: "Kiribati" },
	{ value: "KP", label: "Korea, Democratic People's Republic of" },
	{ value: "KR", label: "Korea, Republic of" },
	{ value: "KW", label: "Kuwait" },
	{ value: "KG", label: "Kyrgyzstan" },
	{ value: "LA", label: "Lao People's Democratic Republic" },
	{ value: "LV", label: "Latvia" },
	{ value: "LB", label: "Lebanon" },
	{ value: "LS", label: "Lesotho" },
	{ value: "LR", label: "Liberia" },
	{ value: "LY", label: "Libya" },
	{ value: "LI", label: "Liechtenstein" },
	{ value: "LT", label: "Lithuania" },
	{ value: "LU", label: "Luxembourg" },
	{ value: "MO", label: "Macao" },
	{ value: "MK", label: "Macedonia, the Former Yugoslav Republic of" },
	{ value: "MG", label: "Madagascar" },
	{ value: "MW", label: "Malawi" },
	{ value: "MY", label: "Malaysia" },
	{ value: "MV", label: "Maldives" },
	{ value: "ML", label: "Mali" },
	{ value: "MT", label: "Malta" },
	{ value: "MH", label: "Marshall Islands" },
	{ value: "MQ", label: "Martinique" },
	{ value: "MR", label: "Mauritania" },
	{ value: "MU", label: "Mauritius" },
	{ value: "YT", label: "Mayotte" },
	{ value: "MX", label: "Mexico" },
	{ value: "FM", label: "Micronesia, Federated States of" },
	{ value: "MD", label: "Moldova, Republic of" },
	{ value: "MC", label: "Monaco" },
	{ value: "MN", label: "Mongolia" },
	{ value: "ME", label: "Montenegro" },
	{ value: "MS", label: "Montserrat" },
	{ value: "MA", label: "Morocco" },
	{ value: "MZ", label: "Mozambique" },
	{ value: "MM", label: "Myanmar" },
	{ value: "NA", label: "Namibia" },
	{ value: "NR", label: "Nauru" },
	{ value: "NP", label: "Nepal" },
	{ value: "NL", label: "Netherlands" },
	{ value: "NC", label: "New Caledonia" },
	{ value: "NZ", label: "New Zealand" },
	{ value: "NI", label: "Nicaragua" },
	{ value: "NE", label: "Niger" },
	{ value: "NG", label: "Nigeria" },
	{ value: "NU", label: "Niue" },
	{ value: "NF", label: "Norfolk Island" },
	{ value: "MP", label: "Northern Mariana Islands" },
	{ value: "NO", label: "Norway" },
	{ value: "OM", label: "Oman" },
	{ value: "PK", label: "Pakistan" },
	{ value: "PW", label: "Palau" },
	{ value: "PS", label: "Palestine, State of" },
	{ value: "PA", label: "Panama" },
	{ value: "PG", label: "Papua New Guinea" },
	{ value: "PY", label: "Paraguay" },
	{ value: "PE", label: "Peru" },
	{ value: "PH", label: "Philippines" },
	{ value: "PN", label: "Pitcairn" },
	{ value: "PL", label: "Poland" },
	{ value: "PT", label: "Portugal" },
	{ value: "PR", label: "Puerto Rico" },
	{ value: "QA", label: "Qatar" },
	{ value: "RE", label: "Réunion" },
	{ value: "RO", label: "Romania" },
	{ value: "RU", label: "Russian Federation" },
	{ value: "RW", label: "Rwanda" },
	{ value: "BL", label: "Saint Barthélemy" },
	{ value: "SH", label: "Saint Helena, Ascension and Tristan da Cunha" },
	{ value: "KN", label: "Saint Kitts and Nevis" },
	{ value: "LC", label: "Saint Lucia" },
	{ value: "MF", label: "Saint Martin (French part)" },
	{ value: "PM", label: "Saint Pierre and Miquelon" },
	{ value: "VC", label: "Saint Vincent and the Grenadines" },
	{ value: "WS", label: "Samoa" },
	{ value: "SM", label: "San Marino" },
	{ value: "ST", label: "Sao Tome and Principe" },
	{ value: "SA", label: "Saudi Arabia" },
	{ value: "SN", label: "Senegal" },
	{ value: "RS", label: "Serbia" },
	{ value: "SC", label: "Seychelles" },
	{ value: "SL", label: "Sierra Leone" },
	{ value: "SG", label: "Singapore" },
	{ value: "SX", label: "Sint Maarten (Dutch part)" },
	{ value: "SK", label: "Slovakia" },
	{ value: "SI", label: "Slovenia" },
	{ value: "SB", label: "Solomon Islands" },
	{ value: "SO", label: "Somalia" },
	{ value: "ZA", label: "South Africa" },
	{ value: "GS", label: "South Georgia and the South Sandwich Islands" },
	{ value: "SS", label: "South Sudan" },
	{ value: "ES", label: "Spain" },
	{ value: "LK", label: "Sri Lanka" },
	{ value: "SD", label: "Sudan" },
	{ value: "SR", label: "Suriname" },
	{ value: "SJ", label: "Svalbard and Jan Mayen" },
	{ value: "SZ", label: "Swaziland" },
	{ value: "SE", label: "Sweden" },
	{ value: "CH", label: "Switzerland" },
	{ value: "SY", label: "Syrian Arab Republic" },
	{ value: "TW", label: "Taiwan, Province of China" },
	{ value: "TJ", label: "Tajikistan" },
	{ value: "TZ", label: "Tanzania, United Republic of" },
	{ value: "TH", label: "Thailand" },
	{ value: "TL", label: "Timor-Leste" },
	{ value: "TG", label: "Togo" },
	{ value: "TK", label: "Tokelau" },
	{ value: "TO", label: "Tonga" },
	{ value: "TT", label: "Trinidad and Tobago" },
	{ value: "TN", label: "Tunisia" },
	{ value: "TR", label: "Turkey" },
	{ value: "TM", label: "Turkmenistan" },
	{ value: "TC", label: "Turks and Caicos Islands" },
	{ value: "TV", label: "Tuvalu" },
	{ value: "UG", label: "Uganda" },
	{ value: "UA", label: "Ukraine" },
	{ value: "AE", label: "United Arab Emirates" },
	{ value: "GB", label: "United Kingdom" },
	{ value: "US", label: "United States" },
	{ value: "UM", label: "United States Minor Outlying Islands" },
	{ value: "UY", label: "Uruguay" },
	{ value: "UZ", label: "Uzbekistan" },
	{ value: "VU", label: "Vanuatu" },
	{ value: "VE", label: "Venezuela, Bolivarian Republic of" },
	{ value: "VN", label: "Viet Nam" },
	{ value: "VG", label: "Virgin Islands, British" },
	{ value: "VI", label: "Virgin Islands, U.S." },
	{ value: "WF", label: "Wallis and Futuna" },
	{ value: "EH", label: "Western Sahara" },
	{ value: "YE", label: "Yemen" },
	{ value: "ZM", label: "Zambia" },
	{ value: "ZW", label: "Zimbabwe" },
];

async function ensureAuthenticated() {
	syncSessionTokenFromBody();
	const headers = {};
	const token = localStorage.getItem("authToken");
	if (token) headers.Authorization = `Bearer ${token}`;
	try {
		const res = await fetch("/api/auth/me/", { headers, credentials: "same-origin" });
		if (res.ok) return true;
	} catch {
		/* fall through to redirect */
	}
	localStorage.removeItem("authToken");
	window.location.href = "/login";
	return false;
}

function renderSidebar(activeHref) {
	return `
    <div class="sidebar-logo">
      <div class="logo-name">Professionals Databank</div>
      <button class="sidebar-close" id="sidebarClose" aria-label="Close menu">✕</button>
    </div>
    <nav class="sidebar-nav">
      ${SHELL_LINKS.map(
			(link) => `
        <a href="/${link.href.replace(".html", "")}"
           class="nav-item ${link.href === activeHref ? "active" : ""}"
           data-route="${link.href}">${link.label}</a>
      `,
		).join("")}
    </nav>
    <div class="sidebar-footer">Professionals Databank</div>
  `;
}

function initMobileNav() {
	const hamburger = document.getElementById("hamburgerBtn");
	const overlay = document.getElementById("sidebarOverlay");
	const sidebar = document.querySelector(".sidebar");

	function open() {
		sidebar.style.removeProperty("display");
		sidebar?.classList.add("open");
		overlay?.classList.add("show");
		document.body.style.overflow = "hidden";
	}
	function close() {
		sidebar?.classList.remove("open");
		overlay?.classList.remove("show");
		document.body.style.overflow = "";
	}

	hamburger?.addEventListener("click", open);
	document.getElementById("sidebarClose")?.addEventListener("click", close);
	overlay?.addEventListener("click", close);
	// Close on nav tap (mobile)
	sidebar?.querySelectorAll("a").forEach((a) =>
		a.addEventListener("click", () => {
			if (window.innerWidth < 900) close();
		}),
	);
}

async function loadCurrentUser() {
	syncSessionTokenFromBody();
	const headers = {};
	const token = localStorage.getItem("authToken");
	if (token) headers.Authorization = `Bearer ${token}`;
	try {
		const res = await fetch("/api/auth/me/", { headers, credentials: "same-origin" });
		if (!res.ok) throw new Error("Unauthorized");
		const data = await res.json();
		window.currentUser = data.user;
		const node = document.getElementById("authUserName");
		if (node) node.textContent = data.user.name || "Member";
		return data.user;
	} catch {
		localStorage.removeItem("authToken");
		window.location.href = "/login";
		return null;
	}
}

/**
 * Populates the primary "Country of Residence" select with just two choices:
 * Kenya and Diaspora. Used for registration and edit forms.
 * @param {HTMLSelectElement} selectElement
 * @param {string} [selectedValue] - 'KE' pre-selects Kenya; anything else pre-selects Diaspora
 */
function populateResidenceSelect(selectElement, selectedValue) {
	if (!selectElement) return;
	selectElement.innerHTML = "";
	const placeholder = document.createElement("option");
	placeholder.value = "";
	placeholder.disabled = true;
	placeholder.textContent = "— Select —";
	if (!selectedValue) placeholder.selected = true;
	selectElement.appendChild(placeholder);

	const kenya = document.createElement("option");
	kenya.value = "KE";
	kenya.textContent = "Kenya";
	if (selectedValue === "KE") kenya.selected = true;
	selectElement.appendChild(kenya);

	const diaspora = document.createElement("option");
	diaspora.value = "diaspora";
	diaspora.textContent = "Diaspora";
	if (selectedValue && selectedValue !== "KE") diaspora.selected = true;
	selectElement.appendChild(diaspora);
}

/**
 * Populates a select with all countries except Kenya (for diaspora members).
 * @param {HTMLSelectElement} selectElement
 * @param {string} [selectedValue] - ISO code to pre-select
 */
function populateDiasporaSelect(selectElement, selectedValue) {
	if (!selectElement) return;
	selectElement.innerHTML = "";
	const placeholder = document.createElement("option");
	placeholder.value = "";
	placeholder.disabled = true;
	placeholder.textContent = "— Select country —";
	if (!selectedValue) placeholder.selected = true;
	selectElement.appendChild(placeholder);
	countries.forEach(function (c) {
		if (c.value === "KE") return;
		const opt = document.createElement("option");
		opt.value = c.value;
		opt.textContent = c.label;
		if (selectedValue && c.value === selectedValue) opt.selected = true;
		selectElement.appendChild(opt);
	});
}

/**
 * Populates a given HTMLSelectElement with the full list of countries.
 * Used for filter dropdowns only (not the residence form field).
 * @param {HTMLSelectElement} selectElement
 * @param {string} [placeholder]
 * @param {string} [selectedValue]
 */
function populateCountrySelect(selectElement, placeholder, selectedValue) {
	placeholder = placeholder || "— Any country —";
	if (!selectElement) return;
	selectElement.innerHTML = "";
	let o = document.createElement("option");
	o.value = "";
	o.textContent = placeholder;
	if (!selectedValue) o.selected = true;
	selectElement.appendChild(o);
	countries.forEach(function (c) {
		let opt = document.createElement("option");
		opt.value = c.value;
		opt.textContent = c.label;
		if (selectedValue && c.value === selectedValue) opt.selected = true;
		selectElement.appendChild(opt);
	});
}

/**
 * Populates a given HTMLSelectElement with the list of Kenyan counties.
 * @param {HTMLSelectElement} selectElement
 * @param {string} [placeholder]
 * @param {string} [selectedValue] - county name to pre-select
 */
function populateCountySelect(selectElement, placeholder, selectedValue) {
	placeholder = placeholder || "— Select county —";
	if (!selectElement) return;
	selectElement.innerHTML = "";
	let o = document.createElement("option");
	o.value = "";
	o.disabled = true;
	o.textContent = placeholder;
	if (!selectedValue) o.selected = true;
	selectElement.appendChild(o);
	counties.forEach(function (c) {
		let opt = document.createElement("option");
		opt.value = c.name;
		opt.textContent = c.name;
		if (selectedValue && c.name === selectedValue) opt.selected = true;
		selectElement.appendChild(opt);
	});
}
function logout() {
	localStorage.removeItem("authToken");
	window.location.href = "/login";
}

/* ── App Overlay (alerts, confirms, success) ───────── */
window.AppOverlay = (function () {
  let overlay = null;

  function ensureEl() {
    if (overlay) return overlay;
    overlay = document.createElement("div");
    overlay.className = "app-overlay";
    overlay.id = "appOverlay";
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) hide();
    });
    document.body.appendChild(overlay);
    return overlay;
  }

  function buildIcon(type) {
    if (type === "success") return "✓";
    if (type === "error") return "✕";
    return "?";
  }

  function show({ type = "success", title, message, actions = [] }) {
    const el = ensureEl();
    el.className = `app-overlay ${type}`;

    const btns = actions
      .map(
        (a) =>
          `<button class="app-overlay-btn ${a.class || "primary"}" data-action="${a.label}">${a.label}</button>`
      )
      .join("");

    el.innerHTML = `
      <div class="app-overlay-card ${type}">
        <div class="app-overlay-icon">${buildIcon(type)}</div>
        <h3>${title || ""}</h3>
        ${message ? `<p>${message}</p>` : ""}
        ${actions.length ? `<div class="app-overlay-actions">${btns}</div>` : ""}
      </div>
    `;

    el.querySelectorAll(".app-overlay-btn").forEach((btn, i) => {
      btn.addEventListener("click", () => actions[i]?.onClick?.());
    });

    // Force reflow so the animation plays
    void el.offsetWidth;
    el.classList.add("show");
  }

  function hide() {
    if (!overlay) return;
    overlay.classList.remove("show");
  }

  return {
    show,
    hide,
    success(title, message, closeLabel = "OK") {
      return show({
        type: "success",
        title,
        message,
        actions: [{ label: closeLabel, class: "success", onClick: hide }],
      });
    },
    error(title, message, closeLabel = "Dismiss") {
      return show({
        type: "error",
        title,
        message,
        actions: [{ label: closeLabel, class: "danger", onClick: hide }],
      });
    },
    confirm(title, message) {
      return new Promise((resolve) => {
        show({
          type: "confirm",
          title,
          message,
          actions: [
            { label: "Cancel", class: "secondary", onClick: () => { hide(); resolve(false); } },
            { label: "Confirm", class: "danger", onClick: () => { hide(); resolve(true); } },
          ],
        });
      });
    },
  };
})();

function initServerShell() {
	initMobileNav();
}

document.addEventListener("DOMContentLoaded", () => {
	syncSessionTokenFromBody();
	if (document.querySelector(".layout") && !document.getElementById("shared-shell")) {
		initServerShell();
	}
});

async function renderProtectedPage({ title, activeHref, contentHtml, onMount, topbarHtml }) {
	document.title = `${title} — Professionals Databank`;
	const shell = document.getElementById("shared-shell");
	if (!shell) return;

	const authOk = await ensureAuthenticated();
	if (!authOk) return;

	shell.innerHTML = `
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    <div class="layout">
      <aside class="sidebar">${renderSidebar(activeHref)}</aside>
      <div class="main">
        <div class="topbar">
          <button class="topbar-hamburger" id="hamburgerBtn" aria-label="Open menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <line x1="3" y1="6"  x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div class="page-title" id="pageTitle">${title}</div>
          ${topbarHtml || ""}
          <div class="auth-user">
            <span id="authUserName">…</span>
            <button id="logoutButton" type="button">Log out</button>
          </div>
        </div>
        <main class="page-content" id="pageContent">${contentHtml}</main>
      </div>
    </div>
  `;

	document.getElementById("logoutButton")?.addEventListener("click", logout);
	initMobileNav();
	await loadCurrentUser();
	if (typeof onMount === "function") onMount();
}
