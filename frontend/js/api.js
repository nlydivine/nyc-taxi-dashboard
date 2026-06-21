const BASE_URL = "http://localhost:5000";

async function fetchTrips(filters = {}) {
  try {
    const res = await fetch(`${BASE_URL}/trips?limit=500`);
    let trips = await res.json();

    if (filters.borough && filters.borough !== "all") {
      trips = trips.filter(t => t.pickup_borough === filters.borough);
    }
    if (filters.minDistance != null) {
      trips = trips.filter(t => t.trip_distance >= filters.minDistance);
    }
    if (filters.maxDistance != null) {
      trips = trips.filter(t => t.trip_distance <= filters.maxDistance);
    }

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

