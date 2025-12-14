package main

import (
	"flag"
	"log"
	"tms-data-generator/generator"
	"tms-data-generator/generator/server"
)

func main() {
	serverMode := flag.Bool("server", false, "Run in server mode")
	port := flag.String("port", "8080", "Port for server mode")
	flag.Parse()

	if *serverMode {
		log.Println("Starting in server mode.")
		server.StartServer(*port)
	} else {
		log.Println("Starting in data generation mode.")
		if err := generator.Generate(); err != nil {
			log.Fatalf("Error during data generation: %v", err)
		}
	}
}
