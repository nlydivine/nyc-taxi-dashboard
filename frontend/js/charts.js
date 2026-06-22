const chartInstances = {};

const COLORS = {
  accent: "#F4B400",
  grid: "#E8E0C8",
  text: "#6B6B6B",
  palette: ["#F4B400", "#5B8DEF", "#5BC98D", "#E0607E", "#9B7BD6"]
};

const baseOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: "#FFFDF5",
      borderColor: "#E8E0C8",
      borderWidth: 1,
      titleColor: "#1C1C1C",
      bodyColor: "#1C1C1C",
      titleFont: { family: "JetBrains Mono", size: 11 },
      bodyFont: { family: "JetBrains Mono", size: 11 }
    }
  },
  scales: {
    x: {
      ticks: { color: COLORS.text, font: { family: "JetBrains Mono", size: 10 } },
      grid: { color: COLORS.grid }
    },
    y: {
      ticks: { color: COLORS.text, font: { family: "JetBrains Mono", size: 10 } },
      grid: { color: COLORS.grid }
    }
  }
};

function renderHourlyChart(trips) {
  const counts = new Array(24).fill(0);
  trips.forEach(t => {
    const hour = parseInt(t.pickup_datetime.split("T")[1].split(":")[0], 10);
    counts[hour]++;
  });
  const labels = counts.map((_, h) => `${String(h).padStart(2,"0")}:00`);
  const ctx = document.getElementById("chartHourly");
  if (chartInstances.hourly) {
    chartInstances.hourly.data.datasets[0].data = counts;
    chartInstances.hourly.update();
    return;
  }
  chartInstances.hourly = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ data: counts, backgroundColor: COLORS.accent, borderRadius: 3, barThickness: 10 }]
    },
    options: baseOptions
  });
}

function renderFareByBoroughChart(trips) {
  const boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island", "Unknown"];
  const totals = {};
  const counts = {};
  boroughs.forEach(b => { totals[b] = 0; counts[b] = 0; });
  trips.forEach(t => {
    totals[t.pickup_borough] += t.fare_amount;
    counts[t.pickup_borough]++;
  });
  const data = boroughs.map(b => counts[b] ? +(totals[b] / counts[b]).toFixed(2) : 0);
  const ctx = document.getElementById("chartFareByBorough");
  if (chartInstances.fare) {
    chartInstances.fare.data.datasets[0].data = data;
    chartInstances.fare.update();
    return;
  }
  chartInstances.fare = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Isl."],
      datasets: [{ data, backgroundColor: COLORS.palette, borderRadius: 3 }]
    },
    options: { ...baseOptions, indexAxis: "y" }
  });
}

function renderDistanceChart(trips) {
  const buckets = [0,1,2,4,6,9,12,16];
  const labels = ["0-1","1-2","2-4","4-6","6-9","9-12","12-16","16+"];
  const counts = new Array(labels.length).fill(0);
  trips.forEach(t => {
    for (let i = 0; i < buckets.length - 1; i++) {
      if (t.trip_distance >= buckets[i] && t.trip_distance < buckets[i+1]) {
        counts[i]++;
        return;
      }
    }
    counts[counts.length - 1]++;
  });
  const ctx = document.getElementById("chartDistanceDist");
  if (chartInstances.distance) {
    chartInstances.distance.data.datasets[0].data = counts;
    chartInstances.distance.update();
    return;
  }
  chartInstances.distance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        data: counts,
        borderColor: COLORS.accent,
        backgroundColor: "rgba(244,180,0,0.15)",
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointBackgroundColor: COLORS.accent
      }]
    },
    options: baseOptions
  });
}

function renderTopZonesChart(trips) {
  const zoneCounts = {};
  trips.forEach(t => {
    zoneCounts[t.pickup_zone] = (zoneCounts[t.pickup_zone] || 0) + 1;
  });
  const sorted = Object.entries(zoneCounts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  const ctx = document.getElementById("chartTopZones");
  if (chartInstances.zones) {
    chartInstances.zones.data.labels = sorted.map(([z]) => z);
    chartInstances.zones.data.datasets[0].data = sorted.map(([,c]) => c);
    chartInstances.zones.update();
    return;
  }
  chartInstances.zones = new Chart(ctx, {
    type: "bar",
    data: {
      labels: sorted.map(([z]) => z),
      datasets: [{ data: sorted.map(([,c]) => c), backgroundColor: COLORS.accent, borderRadius: 3, barThickness: 18 }]
    },
    options: baseOptions
  });
}

function renderAllCharts(trips) {
  renderHourlyChart(trips);
  renderFareByBoroughChart(trips);
  renderDistanceChart(trips);
  renderTopZonesChart(trips);
}

