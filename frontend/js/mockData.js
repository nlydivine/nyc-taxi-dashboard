const BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"];

const ZONES = {
  Manhattan: ["Midtown East", "Upper West Side", "East Village", "Financial District", "Harlem", "Chelsea"],
  Brooklyn: ["Williamsburg", "Park Slope", "DUMBO", "Bushwick", "Sunset Park"],
  Queens: ["Astoria", "LIC", "Flushing", "Jamaica", "JFK Airport"],
  Bronx: ["Fordham", "Concourse", "Riverdale"],
  "Staten Island": ["St. George", "Tottenville"]
};

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randBetween(min, max) {
  return Math.random() * (max - min) + min;
}

function generateTrip(id) {
  const pickupBorough = pick(BOROUGHS);
  const dropoffBorough = pick(BOROUGHS);
  const hour = Math.floor(randBetween(0, 23));
  const day = Math.floor(randBetween(1, 28));
  const distance = +randBetween(0.5, 18).toFixed(2);
  const duration = +Math.max(3, distance * randBetween(2.5, 5)).toFixed(1);
  const fare = +(2.5 + distance * randBetween(2.2, 3.4)).toFixed(2);
  const tip = +(fare * randBetween(0, 0.25)).toFixed(2);

  return {
    id,
    pickup_datetime: `2025-03-${String(day).padStart(2,"0")}T${String(hour).padStart(2,"0")}:00:00`,
    pickup_borough: pickupBorough,
    dropoff_borough: dropoffBorough,
    pickup_zone: pick(ZONES[pickupBorough]),
    dropoff_zone: pick(ZONES[dropoffBorough]),
    trip_distance: distance,
    trip_duration_min: duration,
    fare_amount: fare,
    tip_amount: tip,
    total_amount: +(fare + tip).toFixed(2),
    cost_per_mile: +((fare + tip) / distance).toFixed(2),
    avg_speed_mph: +(distance / (duration / 60)).toFixed(1)
  };
}

window.MOCK_TRIPS = [];
for (let i = 1; i <= 400; i++) {
  window.MOCK_TRIPS.push(generateTrip(i));
}

