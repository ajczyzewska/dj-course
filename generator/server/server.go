package server

import (
	"fmt"
	"log"
	"net/http"
	"tms-data-generator/generator"
)

func generateHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	log.Println("Starting data generation via API request...")
	err := generator.Generate()
	if err != nil {
		http.Error(w, "Failed to generate data: "+err.Error(), http.StatusInternalServerError)
		log.Printf("Error generating data: %v", err)
		return
	}

	log.Println("Data generation finished successfully.")
	fmt.Fprintln(w, "Data generation finished successfully. Check output/tms-latest.sql")
}

func StartServer(port string) {
	http.HandleFunc("/generate", generateHandler)

	log.Printf("Starting server on port %s...", port)
	log.Println("Use POST /generate to trigger data generation.")
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("could not start server: %v", err)
	}
}
