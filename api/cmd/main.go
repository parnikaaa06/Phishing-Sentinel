package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

// ScanLog represents a saved security event
type ScanLog struct {
	ID              int       `json:"id"`
	URL             string    `json:"url"`
	IsSpoof         bool      `json:"is_spoof"`
	ConfidenceScore float64   `json:"confidence_score"`
	ThreatLevel     string    `json:"threat_level"`
	Timestamp       time.Time `json:"timestamp"`
}

// In-memory storage for hackathon demo
var (
	logs      []ScanLog
	logMutex  sync.Mutex
	logCounter int
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

func main() {
	r := gin.Default()

	// Enhanced CORS for local development
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "API is active", "count": len(logs)})
	})

	// NEW: Endpoint for the Dashboard to fetch real logs
	r.GET("/logs", func(c *gin.Context) {
		logMutex.Lock()
		defer logMutex.Unlock()
		c.JSON(http.StatusOK, logs)
	})

	// NEW: Endpoint for Dashboard stats
	r.GET("/stats", func(c *gin.Context) {
		logMutex.Lock()
		defer logMutex.Unlock()
		
		threats := 0
		for _, l := range logs {
			if l.IsSpoof {
				threats++
			}
		}
		
		c.JSON(http.StatusOK, gin.H{
			"scanned":        len(logs),
			"threatsBlocked": threats,
			"trustScore":     98.4, // Simplified for demo
		})
	})

	r.POST("/analyze", func(c *gin.Context) {
		var req AnalysisRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Forward request to ML Service
		mlResponse, err := forwardToMLService(req)
		if err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{"error": "ML Service Unreachable"})
			return
		}

		// Save to real-time log
		logMutex.Lock()
		logCounter++
		newLog := ScanLog{
			ID:              logCounter,
			URL:             req.URL,
			IsSpoof:         mlResponse.IsSpoof,
			ConfidenceScore: mlResponse.ConfidenceScore,
			ThreatLevel:     mlResponse.ThreatLevel,
			Timestamp:       time.Now(),
		}
		// Prepend to show newest first
		logs = append([]ScanLog{newLog}, logs...)
		logMutex.Unlock()

		c.JSON(http.StatusOK, mlResponse)
	})

	log.Println("Sentinel API Gateway running on :8080")
	r.Run(":8080")
}

func forwardToMLService(data AnalysisRequest) (*AnalysisResponse, error) {
	jsonData, _ := json.Marshal(data)
	resp, err := http.Post("http://localhost:8000/analyze", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result AnalysisResponse
	json.Unmarshal(body, &result)
	return &result, nil
}