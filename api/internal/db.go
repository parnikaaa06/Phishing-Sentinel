// api/internal/db.go
package internal

import (
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func InitDB(dsn string) *gorm.DB {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		panic("Failed to connect to Supabase")
	}

	// Auto-migrate the schema
	db.AutoMigrate(&User{}, &ScanLog{})
	return db
}