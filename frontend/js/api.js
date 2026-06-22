const BASE_URL = "http://localhost:5000";

async function fetchTrips(filters = {}) {
  try {
    let url = `${BASE_URL}/trips?limit=500`;

    if (filters.borough && filters.borough !== "all") {
      url += `&borough=${filters.borough}`;
    }
    if (filters.minDistance != null) {
      url += `&minDistance=${filters.minDistance}`;
    }
    if (filters.maxDistance != null) {
      url += `&maxDistance=${filters.maxDistance}`;
    }

    const res = await fetch(url);
    const trips = await res.json();
    return trips;
  } catch (error) {
    console.warn("API unavailable, using mock data");
    return window.MOCK_TRIPS;
  }
}

async function fetchStats() {
  try {
    const res = await fetch(`${BASE_URL}/stats`);
    return await res.json();
  } catch (error) {
    return null;
  }
}

