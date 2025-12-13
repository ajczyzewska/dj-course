package availability

import "time"

// AppliesTo represents which entity the reason applies to
type AppliesTo string

const (
	AppliesDriver  AppliesTo = "DRIVER"
	AppliesVehicle AppliesTo = "VEHICLE"
	AppliesBoth    AppliesTo = "BOTH"
)

// AvailabilityReason represents a reason code for availability/unavailability
type AvailabilityReason struct {
	ReasonCode        string
	ReasonDescription string
	IsAvailable       bool
	AppliesTo         AppliesTo
}

// DriverAvailability represents a driver availability period
type DriverAvailability struct {
	ID         int
	DriverID   int
	StartTime  time.Time
	EndTime    time.Time
	ReasonCode string
	Details    string
}

// VehicleAvailability represents a vehicle availability period
type VehicleAvailability struct {
	ID         int
	VehicleID  int
	StartTime  time.Time
	EndTime    time.Time
	ReasonCode string
	Details    string
}

// Driver reason codes
const (
	ReasonWorking   = "WORKING"
	ReasonRest      = "REST"
	ReasonHoliday   = "HOLIDAY"
	ReasonSick      = "SICK"
	ReasonTraining  = "TRAINING"
	ReasonAvailable = "AVAILABLE"
)

// Vehicle reason codes
const (
	ReasonReady        = "READY"
	ReasonMaintenance  = "MAINTENANCE"
	ReasonBreakdown    = "BREAKDOWN"
	ReasonRegistration = "REGISTRATION"
	ReasonWashing      = "WASHING"
)
