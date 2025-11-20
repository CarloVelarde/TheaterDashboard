// Base API path (assuming frontend served under same origin as FastAPI)
const API_BASE = "/api";

// Simple helper to show Bootstrap alerts at top
function showGlobalAlert(message, type = "info", timeoutMs = 4000) {
  const container = document.getElementById("global-alert-container");
  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      <span>${message}</span>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  const alertEl = wrapper.firstElementChild;
  container.appendChild(alertEl);

  if (timeoutMs) {
    setTimeout(() => {
      alertEl.classList.remove("show");
      alertEl.addEventListener("transitionend", () => alertEl.remove(), {
        once: true,
      });
    }, timeoutMs);
  }
}

// Generic JSON fetch wrapper
async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function apiPost(path, bodyObj) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyObj),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await res.text();
    }
    throw new Error(detail);
  }
  return res.json();
}

// Section navigation
function initNavigation() {
  const nav = document.getElementById("nav-sections");
  const links = nav.querySelectorAll(".nav-link");
  const sections = document.querySelectorAll(".app-section");

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("data-section");

      // nav active state
      links.forEach((l) => l.classList.remove("active"));
      link.classList.add("active");

      // sections
      sections.forEach((sec) => {
        if (sec.id === targetId) {
          sec.classList.add("active");
        } else {
          sec.classList.remove("active");
        }
      });
    });
  });
}

// ----------- OVERVIEW SECTION -----------

async function loadNowPlaying() {
  try {
    const movies = await apiGet("/movies/now-playing");
    const tbody = document.getElementById("table-now-playing");
    tbody.innerHTML = "";

    if (!movies.length) {
      tbody.innerHTML = `<tr><td colspan="3" class="text-muted">No active movies.</td></tr>`;
      return;
    }

    for (const m of movies) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${m.title}</td>
        <td>${m.genre}</td>
        <td>${m.runtime} min</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(
      `Failed to load now playing movies: ${err.message}`,
      "danger"
    );
  }
}

async function loadUpcomingMovies() {
  try {
    const movies = await apiGet("/movies/upcoming");
    const tbody = document.getElementById("table-upcoming");
    tbody.innerHTML = "";

    if (!movies.length) {
      tbody.innerHTML = `<tr><td colspan="3" class="text-muted">No upcoming movies.</td></tr>`;
      return;
    }

    for (const m of movies) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${m.title}</td>
        <td>${m.genre}</td>
        <td>${m.release_date}</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(`Failed to load upcoming movies: ${err.message}`, "danger");
  }
}

async function loadAllMovies() {
  try {
    const movies = await apiGet("/movies");
    const tbody = document.getElementById("table-all-movies");
    tbody.innerHTML = "";

    if (!movies.length) {
      tbody.innerHTML = `<tr><td colspan="3" class="text-muted">No movies found.</td></tr>`;
      return;
    }

    for (const m of movies) {
      const tr = document.createElement("tr");
      const activeBadge = m.is_active
        ? `<span class="badge bg-success">Yes</span>`
        : `<span class="badge bg-secondary">No</span>`;
      tr.innerHTML = `
        <td>${m.title}</td>
        <td>${m.genre}</td>
        <td>${activeBadge}</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(`Failed to load all movies: ${err.message}`, "danger");
  }
}

function initOverviewSection() {
  document
    .getElementById("btn-refresh-now-playing")
    .addEventListener("click", loadNowPlaying);
  document
    .getElementById("btn-refresh-upcoming")
    .addEventListener("click", loadUpcomingMovies);
  document
    .getElementById("btn-refresh-all-movies")
    .addEventListener("click", loadAllMovies);
}

// ----------- SHARED DROPDOWN DATA (customers, showtimes, movies) -----------

async function loadCustomersIntoSelect(selectId) {
  try {
    const customers = await apiGet("/customers");
    const select = document.getElementById(selectId);
    select.innerHTML = `<option value="">Select a customer...</option>`;
    for (const c of customers) {
      const opt = document.createElement("option");
      opt.value = c.customer_id;
      opt.textContent = `${c.customer_id} — ${c.fname} ${c.lname ?? ""}`.trim();
      select.appendChild(opt);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(`Failed to load customers: ${err.message}`, "danger");
  }
}

async function loadShowtimesIntoSelect(selectId) {
  try {
    const showtimes = await apiGet("/showtimes");
    const movies = await apiGet("/movies"); // to map movie titles

    const moviesById = {};
    movies.forEach((m) => {
      moviesById[m.movie_id] = m.title;
    });

    const select = document.getElementById(selectId);
    select.innerHTML = `<option value="">Select a showtime...</option>`;
    for (const s of showtimes) {
      const movieTitle = moviesById[s.movie_id] || `Movie ${s.movie_id}`;
      const label = `${s.showtime_id} — ${movieTitle} @ ${s.start_time} (Aud ${s.theater_id})`;
      const opt = document.createElement("option");
      opt.value = s.showtime_id;
      opt.textContent = label;
      select.appendChild(opt);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(`Failed to load showtimes: ${err.message}`, "danger");
  }
}

async function loadMoviesIntoSelect(selectId) {
  try {
    const movies = await apiGet("/movies");
    const select = document.getElementById(selectId);
    select.innerHTML = `<option value="">Select a movie...</option>`;
    for (const m of movies) {
      const opt = document.createElement("option");
      opt.value = m.movie_id;
      opt.textContent = `${m.movie_id} — ${m.title}`;
      select.appendChild(opt);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(
      `Failed to load movies for dropdown: ${err.message}`,
      "danger"
    );
  }
}

// ----------- TICKET OPERATIONS -----------

function initTicketPurchaseForm() {
  const form = document.getElementById("form-purchase-ticket");
  const resultDiv = document.getElementById("purchase-ticket-result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultDiv.innerHTML = "";

    const customerId = document.getElementById("select-customer").value;
    const showtimeId = document.getElementById("select-showtime").value;

    if (!customerId || !showtimeId) {
      showGlobalAlert("Please select both customer and showtime.", "warning");
      return;
    }

    try {
      const res = await apiPost("/tickets/purchase", {
        customer_id: parseInt(customerId, 10),
        showtime_id: parseInt(showtimeId, 10),
      });

      resultDiv.innerHTML = `
        <div class="alert alert-success mb-0" role="alert">
          ${res.message}
        </div>
      `;
      showGlobalAlert("Ticket purchase succeeded.", "success");
    } catch (err) {
      console.error(err);
      resultDiv.innerHTML = `
        <div class="alert alert-danger mb-0" role="alert">
          ${err.message}
        </div>
      `;
      showGlobalAlert(`Ticket purchase failed: ${err.message}`, "danger");
    }
  });
}

async function loadTicketsToday() {
  try {
    const tickets = await apiGet("/tickets/today");
    const tbody = document.getElementById("table-tickets-today");
    tbody.innerHTML = "";

    if (!tickets.length) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-muted">No tickets sold today.</td></tr>`;
      return;
    }

    for (const t of tickets) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${t.ticket_sale_id}</td>
        <td>${t.customer_id}</td>
        <td>${t.showtime_id}</td>
        <td>$${t.ticket_price.toFixed(2)}</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(`Failed to load today's tickets: ${err.message}`, "danger");
  }
}

async function loadAllTickets() {
  try {
    const tickets = await apiGet("/tickets");
    const tbody = document.getElementById("table-all-tickets");
    tbody.innerHTML = "";

    if (!tickets.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-muted">No tickets found.</td></tr>`;
      return;
    }

    for (const t of tickets) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${t.ticket_sale_id}</td>
        <td>${t.customer_id}</td>
        <td>${t.showtime_id}</td>
        <td>$${t.ticket_price.toFixed(2)}</td>
        <td>${t.time_ticket_sold}</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error(err);
    showGlobalAlert(`Failed to load all tickets: ${err.message}`, "danger");
  }
}

function initTicketsSection() {
  // Purchase form
  initTicketPurchaseForm();

  // Tickets today
  document
    .getElementById("btn-refresh-tickets-today")
    .addEventListener("click", loadTicketsToday);

  // All tickets
  document
    .getElementById("btn-refresh-all-tickets")
    .addEventListener("click", loadAllTickets);

  // Customer ticket history
  const selectHistoryCustomer = document.getElementById(
    "select-history-customer"
  );
  selectHistoryCustomer.addEventListener("change", async () => {
    const customerId = selectHistoryCustomer.value;
    const tbody = document.getElementById("table-customer-history");
    tbody.innerHTML = "";
    if (!customerId) return;

    try {
      const history = await apiGet(`/tickets/customers/${customerId}/tickets`);
      if (!history.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-muted">No tickets for this customer.</td></tr>`;
        return;
      }

      for (const row of history) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.ticket_sale_id}</td>
          <td>${row.movie_title}</td>
          <td>${row.showtime_id}</td>
          <td>$${row.ticket_price.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      console.error(err);
      showGlobalAlert(
        `Failed to load customer ticket history: ${err.message}`,
        "danger"
      );
    }
  });
}

// ----------- REPORTS SECTION -----------

function initReportsSection() {
  // Query 1: movie showtimes by date
  const formQ1 = document.getElementById("form-report-movie-showtimes");
  formQ1.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("report-q1-title").value.trim();
    const date = document.getElementById("report-q1-date").value;
    const tbody = document.getElementById("table-report-q1");
    tbody.innerHTML = "";

    if (!title || !date) return;

    try {
      const data = await apiGet(
        `/reports/movie-showtimes?title=${encodeURIComponent(
          title
        )}&date=${encodeURIComponent(date)}`
      );
      if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-muted">No showtimes found.</td></tr>`;
        return;
      }
      for (const row of data) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.title}</td>
          <td>${row.showtime_id}</td>
          <td>${row.theater_id}</td>
          <td>${row.start_time}</td>
          <td>${row.end_time}</td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      console.error(err);
      showGlobalAlert(`Query 1 failed: ${err.message}`, "danger");
    }
  });

  // Query 2: showtime availability
  const formQ2 = document.getElementById("form-report-showtime-availability");
  formQ2.addEventListener("submit", async (e) => {
    e.preventDefault();
    const showtimeId = document.getElementById("report-q2-showtime-id").value;
    const resultDiv = document.getElementById("report-q2-result");
    resultDiv.innerHTML = "";

    if (!showtimeId) return;

    try {
      const data = await apiGet(
        `/reports/showtime-availability?showtime_id=${encodeURIComponent(
          showtimeId
        )}`
      );
      resultDiv.innerHTML = `
        <div class="alert alert-success mb-0" role="alert">
          <div><strong>Showtime:</strong> ${data.showtime_id}</div>
          <div><strong>Capacity:</strong> ${data.seat_capacity}</div>
          <div><strong>Tickets Sold:</strong> ${data.tickets_sold}</div>
          <div><strong>Seats Remaining:</strong> ${data.seats_remaining}</div>
        </div>
      `;
    } catch (err) {
      console.error(err);
      showGlobalAlert(`Query 2 failed: ${err.message}`, "danger");
    }
  });

  // Query 3: concession revenue by category
  const formQ3 = document.getElementById("form-report-concession-revenue");
  formQ3.addEventListener("submit", async (e) => {
    e.preventDefault();
    const limitVal = document.getElementById("report-q3-limit").value;
    const tbody = document.getElementById("table-report-q3");
    tbody.innerHTML = "";

    let url = "/reports/concessions/top-categories";
    if (limitVal) {
      url += `?limit=${encodeURIComponent(limitVal)}`;
    }

    try {
      const data = await apiGet(url);
      if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="2" class="text-muted">No concession sales found.</td></tr>`;
        return;
      }
      for (const row of data) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.category}</td>
          <td>$${row.total_revenue.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      console.error(err);
      showGlobalAlert(`Query 3 failed: ${err.message}`, "danger");
    }
  });

  // Query 4: lifetime ticket sales for a movie
  const formQ4 = document.getElementById("form-report-movie-lifetime");
  formQ4.addEventListener("submit", async (e) => {
    e.preventDefault();
    const movieId = document.getElementById("report-q4-movie-id").value;
    const resultDiv = document.getElementById("report-q4-result");
    resultDiv.innerHTML = "";

    if (!movieId) return;

    try {
      const data = await apiGet(
        `/reports/movie-lifetime-sales?movie_id=${encodeURIComponent(movieId)}`
      );
      resultDiv.innerHTML = `
        <div class="alert alert-info mb-0" role="alert">
          <div><strong>Movie:</strong> ${data.title} (ID ${data.movie_id})</div>
          <div><strong>Lifetime Ticket Sales:</strong> ${data.lifetime_ticket_sales}</div>
        </div>
      `;
    } catch (err) {
      console.error(err);
      showGlobalAlert(`Query 4 failed: ${err.message}`, "danger");
    }
  });

  // Query 5: upcoming showtimes (view)
  const formQ5 = document.getElementById("form-report-upcoming-showtimes");
  formQ5.addEventListener("submit", async (e) => {
    e.preventDefault();
    const days = document.getElementById("report-q5-days-ahead").value;
    const tbody = document.getElementById("table-report-q5");
    tbody.innerHTML = "";

    let url = "/reports/upcoming-showtimes";
    if (days) {
      url += `?days_ahead=${encodeURIComponent(days)}`;
    }

    try {
      const data = await apiGet(url);
      if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-muted">No upcoming showtimes found.</td></tr>`;
        return;
      }
      for (const row of data) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.showtime_id}</td>
          <td>${row.movie_title}</td>
          <td>${row.theater_id}</td>
          <td>${row.start_time}</td>
          <td>${row.dynamic_status}</td>
        `;
        tbody.appendChild(tr);
      }
    } catch (err) {
      console.error(err);
      showGlobalAlert(`Query 5 failed: ${err.message}`, "danger");
    }
  });

  // Optional: daily ticket sales (function)
  const formDaily = document.getElementById("form-report-daily-sales");
  formDaily.addEventListener("submit", async (e) => {
    e.preventDefault();
    const dateVal = document.getElementById("report-daily-date").value;
    const resultDiv = document.getElementById("report-daily-result");
    resultDiv.innerHTML = "";
    if (!dateVal) return;

    try {
      const data = await apiGet(
        `/reports/daily-ticket-sales?date=${encodeURIComponent(dateVal)}`
      );
      resultDiv.innerHTML = `
        <div class="alert alert-dark mb-0" role="alert">
          <div><strong>Date:</strong> ${data.report_date}</div>
          <div><strong>Ticket Sales:</strong> ${data.tickets_sold}</div>
        </div>
      `;
    } catch (err) {
      console.error(err);
      showGlobalAlert(
        `Daily ticket sales query failed: ${err.message}`,
        "danger"
      );
    }
  });

  // Optional: movie profit (function)
  const formProfit = document.getElementById("form-report-movie-profit");
  formProfit.addEventListener("submit", async (e) => {
    e.preventDefault();
    const movieId = document.getElementById("report-profit-movie-id").value;
    const resultDiv = document.getElementById("report-profit-result");
    resultDiv.innerHTML = "";
    if (!movieId) return;

    try {
      const data = await apiGet(
        `/reports/movies/${encodeURIComponent(movieId)}/profit`
      );
      resultDiv.innerHTML = `
        <div class="alert alert-dark mb-0" role="alert">
          <div><strong>Movie:</strong> ${data.title} (ID ${data.movie_id})</div>
          <div><strong>Net Profit:</strong> $${data.net_profit.toFixed(2)}</div>
        </div>
      `;
    } catch (err) {
      console.error(err);
      showGlobalAlert(`Movie profit query failed: ${err.message}`, "danger");
    }
  });
}

// ----------- INITIALIZATION -----------

async function initApp() {
  initNavigation();
  initOverviewSection();
  initTicketsSection();
  initReportsSection();

  // Initial loads
  await Promise.all([
    loadNowPlaying(),
    loadUpcomingMovies(),
    loadAllMovies(),
    loadCustomersIntoSelect("select-customer"),
    loadCustomersIntoSelect("select-history-customer"),
    loadShowtimesIntoSelect("select-showtime"),
    loadShowtimesIntoSelect("report-q2-showtime-id"),
    loadMoviesIntoSelect("report-q4-movie-id"),
    loadMoviesIntoSelect("report-profit-movie-id"),
  ]);

  // Optionally preload today's tickets
  loadTicketsToday();
}

document.addEventListener("DOMContentLoaded", () => {
  initApp().catch((err) => {
    console.error("Failed to initialize app:", err);
    showGlobalAlert(`Failed to initialize app: ${err.message}`, "danger", 0);
  });
});
