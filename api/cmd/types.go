// Data structures for the ML Service communication
package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
)

type AnalysisRequest struct {
	URL        string                 `json:"url" binding:"required"`
	DOMContent string                 `json:"dom_content"`
	Metadata   map[string]interface{} `json:"metadata"`
}

type AnalysisResponse struct {
	IsSpoof         bool     `json:"is_spoof"`
	ConfidenceScore float64  `json:"confidence_score"`
	ThreatLevel     string   `json:"threat_level"`
	Anomalies       []string `json:"detected_anomalies"`
}

// Function to call your Python ML service
func forwardToMLService(data AnalysisRequest) (*AnalysisResponse, error) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}

	// Assuming your Python FastAPI/Flask server runs on port 8000
	resp, err := http.Post("http://localhost:8000/analyze", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result AnalysisResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	return &result, nil
}