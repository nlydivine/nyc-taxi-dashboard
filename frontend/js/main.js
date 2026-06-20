async function refreshDashboard() {
  const borough = document.getElementById("boroughFilter").value;
  const minDistance = document.getElementById("minDistance").value;
  const maxDistance = document.getElementById("maxDistance").value;

  const filters = {};
  if (borough !== "all") filters.borough = borough;
  if (minDistance !== "") filters.minDistance = parseFloat(minDistance);
  if (maxDistance !== "") filters.maxDistance = parseFloat(maxDistance);

  let trips = await fetchTrips(filters);
  trips = applySort(trips);

  document.getElementById("tripCountValue").textContent = trips.length.toLocaleString();

  updateStats(trips);
  renderTable(trips);
  renderAllCharts(trips);
}

function applySort(trips) {
  const sortBy = document.getElementById("sortBy").value;
  const sorted = [...trips];
  if (sortBy === "fare_desc") sorted.sort((a, b) => b.fare_amount - a.fare_amount);
  if (sortBy === "fare_asc") sorted.sort((a, b) => a.fare_amount - b.fare_amount);
  if (sortBy === "distance_desc") sorted.sort((a, b) => b.trip_distance - a.trip_distance);
  return sorted;
}

function updateStats(trips) {
  if (trips.length === 0) {
    document.getElementById("statAvgFare").textContent = "$0.00";
    document.getElementById("statAvgDistance").textContent = "0 mi";
    document.getElementById("statAvgSpeed").textContent = "0 mph";
    document.getElementById("statCostPerMile").textContent = "$0.00";
    return;
  }

  const avg = key => trips.reduce((acc, t) => acc + t[key], 0) / trips.length;

  document.getElementById("statAvgFare").textContent = `$${avg("fare_amount").toFixed(2)}`;
  document.getElementById("statAvgDistance").textContent = `${avg("trip_distance").toFixed(1)} mi`;
  document.getElementById("statAvgSpeed").textContent = `${avg("avg_speed_mph").toFixed(1)} mph`;
  document.getElementById("statCostPerMile").textContent = `$${avg("cost_per_mile").toFixed(2)}`;
}

function renderTable(trips) {
  const tbody = document.getElementById("tripsTableBody");
  const rows = trips.slice(0, 50);

  tbody.innerHTML = rows.map(t => `
    <tr>
      <td>${t.pickup_datetime.replace("T", " ")}</td>
      <td>${t.pickup_zone}</td>
      <td>${t.dropoff_zone}</td>
      <td>${t.trip_distance} mi</td>
      <td>$${t.fare_amount.toFixed(2)}</td>
      <td>${t.avg_speed_mph} mph</td>
    </tr>
  `).join("");

  document.getElementById("tableCount").textContent = `(showing ${rows.length} of ${trips.length})`;
}

function resetFilters() {
  document.getElementById("boroughFilter").value = "all";
  document.getElementById("minDistance").value = "";
  document.getElementById("maxDistance").value = "";
  document.getElementById("sortBy").value = "none";
  refreshDashboard();
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("applyFilters").addEventListener("click", refreshDashboard);
  document.getElementById("resetFilters").addEventListener("click", resetFilters);
  document.getElementById("sortBy").addEventListener("change", refreshDashboard);
  refreshDashboard();
});


