<<<<<<< HEAD
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
=======
const BASE_URL = "";

async function fetchTrips(filters = {}) {
  const params = new URLSearchParams();
  params.set("limit", "10000");
  if (filters.borough && filters.borough !== "all") params.set("borough", filters.borough);
  if (filters.minDistance != null) params.set("minDistance", filters.minDistance);
  if (filters.maxDistance != null) params.set("maxDistance", filters.maxDistance);

  try {
    const res = await fetch(`${BASE_URL}/trips?${params.toString()}`);
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    return await res.json();
  } catch (error) {
    console.warn("API unavailable, using mock data:", error);
    let trips = window.MOCK_TRIPS;
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
>>>>>>> Merge frontend+API into one Flask service
  }
}

async function fetchStats() {
  try {
    const res = await fetch(`${BASE_URL}/stats`);
<<<<<<< HEAD
=======
    if (!res.ok) throw new Error(`API returned ${res.status}`);
>>>>>>> Merge frontend+API into one Flask service
    return await res.json();
  } catch (error) {
    return null;
  }
}
