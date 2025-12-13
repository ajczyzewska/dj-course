package availability

import (
	"fmt"
	"math/rand"
	"strings"
	"time"

	"tms-data-generator/generator/drivers"
	"tms-data-generator/generator/vehicles"
)

// GenerateDriverAvailability generates availability records for all drivers
func GenerateDriverAvailability(driversList []drivers.Driver, daysAhead int) []DriverAvailability {
	var result []DriverAvailability
	id := 1
	startDate := time.Now().UTC().Truncate(24 * time.Hour) // Start at midnight

	for _, driver := range driversList {
		currentDate := startDate

		for currentDate.Before(startDate.AddDate(0, 0, daysAhead)) {
			// Weekday logic
			isWeekend := currentDate.Weekday() == time.Saturday || currentDate.Weekday() == time.Sunday

			if isWeekend {
				// Weekend - full day REST
				result = append(result, DriverAvailability{
					ID:         id,
					DriverID:   driver.ID,
					StartTime:  time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 0, 0, 0, 0, time.UTC),
					EndTime:    time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 23, 59, 59, 0, time.UTC),
					ReasonCode: ReasonRest,
					Details:    "Weekend rest period",
				})
				id++
			} else {
				// Weekday - different scenarios
				randomChance := rand.Float64()

				if randomChance < 0.03 { // 3% chance of holiday
					result = append(result, DriverAvailability{
						ID:         id,
						DriverID:   driver.ID,
						StartTime:  time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 0, 0, 0, 0, time.UTC),
						EndTime:    time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 23, 59, 59, 0, time.UTC),
						ReasonCode: ReasonHoliday,
						Details:    "Planned vacation",
					})
					id++
				} else if randomChance < 0.05 { // Additional 2% chance of sick leave
					result = append(result, DriverAvailability{
						ID:         id,
						DriverID:   driver.ID,
						StartTime:  time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 0, 0, 0, 0, time.UTC),
						EndTime:    time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 23, 59, 59, 0, time.UTC),
						ReasonCode: ReasonSick,
						Details:    "Medical leave",
					})
					id++
				} else if randomChance < 0.06 { // 1% chance of training
					result = append(result, DriverAvailability{
						ID:         id,
						DriverID:   driver.ID,
						StartTime:  time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 8, 0, 0, 0, time.UTC),
						EndTime:    time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 16, 0, 0, 0, time.UTC),
						ReasonCode: ReasonTraining,
						Details:    "Safety and compliance training",
					})
					id++
				} else {
					// Normal working day - create shift pattern
					// Early shift: 6:00-16:00 or late shift: 14:00-00:00
					isEarlyShift := rand.Float64() < 0.7 // 70% early shift, 30% late shift

					var startHour, endHour int
					var shiftType string

					if isEarlyShift {
						startHour = 6
						endHour = 16
						shiftType = "Morning shift"
					} else {
						startHour = 14
						endHour = 24
						shiftType = "Evening shift"
					}

					startShift := time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), startHour, 0, 0, 0, time.UTC)
					var endShift time.Time
					if endHour == 24 {
						endShift = time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 23, 59, 59, 0, time.UTC)
					} else {
						endShift = time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), endHour, 0, 0, 0, time.UTC)
					}

					result = append(result, DriverAvailability{
						ID:         id,
						DriverID:   driver.ID,
						StartTime:  startShift,
						EndTime:    endShift,
						ReasonCode: ReasonWorking,
						Details:    shiftType,
					})
					id++
				}
			}

			currentDate = currentDate.AddDate(0, 0, 1)
		}
	}

	return result
}

// GenerateVehicleAvailability generates availability records for all vehicles
func GenerateVehicleAvailability(vehiclesList []vehicles.Vehicle, daysAhead int) []VehicleAvailability {
	var result []VehicleAvailability
	id := 1
	startDate := time.Now().UTC().Truncate(24 * time.Hour)

	for _, vehicle := range vehiclesList {
		currentDate := startDate
		endDate := startDate.AddDate(0, 0, daysAhead)

		// Determine maintenance schedule for this vehicle
		// Each vehicle gets maintenance every 30-60 days
		maintenanceInterval := 30 + rand.Intn(31) // 30-60 days
		nextMaintenance := startDate.AddDate(0, 0, rand.Intn(maintenanceInterval))

		// Track current availability period
		currentPeriodStart := currentDate
		currentReason := ReasonReady
		currentDetails := "Vehicle ready for dispatch"

		for currentDate.Before(endDate) {
			// Check if it's time for maintenance
			if currentDate.Equal(nextMaintenance) && currentDate.Before(endDate.AddDate(0, 0, -1)) {
				// End current ready period
				if currentPeriodStart.Before(currentDate) {
					result = append(result, VehicleAvailability{
						ID:         id,
						VehicleID:  vehicle.ID,
						StartTime:  currentPeriodStart,
						EndTime:    currentDate.Add(-1 * time.Second),
						ReasonCode: currentReason,
						Details:    currentDetails,
					})
					id++
				}

				// Add maintenance period (4-8 hours)
				maintenanceDuration := time.Duration(4+rand.Intn(5)) * time.Hour
				maintenanceStart := time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 8, 0, 0, 0, time.UTC)
				maintenanceEnd := maintenanceStart.Add(maintenanceDuration)

				maintenanceTypes := []string{
					"Oil and filter change",
					"Tire rotation and inspection",
					"Brake system check",
					"General inspection and service",
				}

				result = append(result, VehicleAvailability{
					ID:         id,
					VehicleID:  vehicle.ID,
					StartTime:  maintenanceStart,
					EndTime:    maintenanceEnd,
					ReasonCode: ReasonMaintenance,
					Details:    maintenanceTypes[rand.Intn(len(maintenanceTypes))],
				})
				id++

				// Start new ready period after maintenance
				currentPeriodStart = maintenanceEnd.Add(1 * time.Second)
				currentReason = ReasonReady
				currentDetails = "Vehicle ready for dispatch"

				// Schedule next maintenance
				nextMaintenance = nextMaintenance.AddDate(0, 0, maintenanceInterval)
			}

			// Random chance of breakdown (very rare - 0.5% per day)
			if rand.Float64() < 0.005 && currentDate.Before(endDate.AddDate(0, 0, -1)) {
				// End current period
				if currentPeriodStart.Before(currentDate) {
					result = append(result, VehicleAvailability{
						ID:         id,
						VehicleID:  vehicle.ID,
						StartTime:  currentPeriodStart,
						EndTime:    currentDate.Add(-1 * time.Second),
						ReasonCode: currentReason,
						Details:    currentDetails,
					})
					id++
				}

				// Add breakdown period (2-12 hours)
				breakdownDuration := time.Duration(2+rand.Intn(11)) * time.Hour
				breakdownStart := time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 10+rand.Intn(8), 0, 0, 0, time.UTC)
				breakdownEnd := breakdownStart.Add(breakdownDuration)

				breakdownTypes := []string{
					"Engine malfunction repair",
					"Electrical system fault",
					"Tire replacement",
					"Transmission issue",
					"Cooling system repair",
				}

				result = append(result, VehicleAvailability{
					ID:         id,
					VehicleID:  vehicle.ID,
					StartTime:  breakdownStart,
					EndTime:    breakdownEnd,
					ReasonCode: ReasonBreakdown,
					Details:    breakdownTypes[rand.Intn(len(breakdownTypes))],
				})
				id++

				// Start new ready period after repair
				currentPeriodStart = breakdownEnd.Add(1 * time.Second)
				currentReason = ReasonReady
				currentDetails = "Vehicle ready for dispatch"
			}

			// Weekly washing (every Monday morning)
			if currentDate.Weekday() == time.Monday && rand.Float64() < 0.8 { // 80% chance on Mondays
				// End current period
				if currentPeriodStart.Before(currentDate) {
					result = append(result, VehicleAvailability{
						ID:         id,
						VehicleID:  vehicle.ID,
						StartTime:  currentPeriodStart,
						EndTime:    time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 7, 0, 0, 0, time.UTC).Add(-1 * time.Second),
						ReasonCode: currentReason,
						Details:    currentDetails,
					})
					id++
				}

				// Add washing period (1-2 hours)
				washStart := time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 7, 0, 0, 0, time.UTC)
				washEnd := washStart.Add(time.Duration(1+rand.Intn(2)) * time.Hour)

				result = append(result, VehicleAvailability{
					ID:         id,
					VehicleID:  vehicle.ID,
					StartTime:  washStart,
					EndTime:    washEnd,
					ReasonCode: ReasonWashing,
					Details:    "Vehicle washing and cleaning",
				})
				id++

				// Start new ready period
				currentPeriodStart = washEnd.Add(1 * time.Second)
				currentReason = ReasonReady
				currentDetails = "Vehicle ready for dispatch"
			}

			currentDate = currentDate.AddDate(0, 0, 1)
		}

		// Close final period
		if currentPeriodStart.Before(endDate) {
			result = append(result, VehicleAvailability{
				ID:         id,
				VehicleID:  vehicle.ID,
				StartTime:  currentPeriodStart,
				EndTime:    endDate.Add(-1 * time.Second),
				ReasonCode: currentReason,
				Details:    currentDetails,
			})
			id++
		}
	}

	return result
}

// GenerateDriverAvailabilityInsertStatements generates SQL INSERT statements
func GenerateDriverAvailabilityInsertStatements(availabilityList []DriverAvailability) string {
	if len(availabilityList) == 0 {
		return ""
	}

	var sb strings.Builder
	sb.WriteString("-- Driver Availability Records\n")
	sb.WriteString("INSERT INTO driver_availability (id, driver_id, start_time, end_time, reason_code, details) VALUES\n")

	for i, avail := range availabilityList {
		sb.WriteString(fmt.Sprintf("(%d, %d, '%s', '%s', '%s', '%s')",
			avail.ID,
			avail.DriverID,
			avail.StartTime.Format("2006-01-02 15:04:05"),
			avail.EndTime.Format("2006-01-02 15:04:05"),
			avail.ReasonCode,
			escapeSQL(avail.Details)))

		if i < len(availabilityList)-1 {
			sb.WriteString(",\n")
		} else {
			sb.WriteString(";\n\n")
		}
	}

	return sb.String()
}

// GenerateVehicleAvailabilityInsertStatements generates SQL INSERT statements
func GenerateVehicleAvailabilityInsertStatements(availabilityList []VehicleAvailability) string {
	if len(availabilityList) == 0 {
		return ""
	}

	var sb strings.Builder
	sb.WriteString("-- Vehicle Availability Records\n")
	sb.WriteString("INSERT INTO vehicle_availability (id, vehicle_id, start_time, end_time, reason_code, details) VALUES\n")

	for i, avail := range availabilityList {
		sb.WriteString(fmt.Sprintf("(%d, %d, '%s', '%s', '%s', '%s')",
			avail.ID,
			avail.VehicleID,
			avail.StartTime.Format("2006-01-02 15:04:05"),
			avail.EndTime.Format("2006-01-02 15:04:05"),
			avail.ReasonCode,
			escapeSQL(avail.Details)))

		if i < len(availabilityList)-1 {
			sb.WriteString(",\n")
		} else {
			sb.WriteString(";\n\n")
		}
	}

	return sb.String()
}

// escapeSQL escapes single quotes in SQL strings
func escapeSQL(s string) string {
	return strings.ReplaceAll(s, "'", "''")
}
