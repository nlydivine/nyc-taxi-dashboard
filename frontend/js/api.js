async function fetchTrips(filters = {}) {
  await new Promise(resolve => setTimeout(resolve, 150));

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
}

