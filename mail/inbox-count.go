package main

/*
Invoke commands:
	Run with config from environment variables:
		GMAIL_ACCOUNT=<redact> GMAIL_PASSWORD=<redact> GO111MODULE=off go run inbox-count.go
	Run with config from mutt:
		GO111MODULE=off go run inbox-count.go
*/

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"

	"github.com/emersion/go-imap"
	"github.com/emersion/go-imap/client"
)

// Read muttrc file to get imap_user and imap_pass settings
func getField(fieldName string) string {
	var result string
	homeDir, _ := os.UserHomeDir()
	content, err := os.ReadFile(filepath.Join(homeDir, "/.mutt/muttrc"))
	if err != nil {
		log.Fatal(err)
	}
	pattern := fmt.Sprintf(`set imap_%s = "(?P<%s>[^ ]+)"`, fieldName, fieldName)
	re := regexp.MustCompile(pattern)
	match := re.FindAllStringSubmatch(string(content), -1)
	if len(match) != 0 {
		result = match[0][re.SubexpIndex(fieldName)]
	}

	return result
}

// Returns the imap username from mutt config
func getLogin() string {
	return getField("user")
}

// Returns the imap password from mutt config
func getPassword() string {
	return getField("pass")
}

// Output the number of mails unread/total into IMAP `INBOX` folder (e.g. label:inbox)
func main() {
	var userName string
	var userPassword string

	userName = os.Getenv("GMAIL_ACCOUNT")
	if userName == "" {
		userName = getLogin()
	}
	userPassword = os.Getenv("GMAIL_PASSWORD")
	if userPassword == "" {
		userPassword = getPassword()
	}

	c, err := client.DialTLS("imap.gmail.com:993", nil)
	if err != nil {
		log.Fatal(err)
	}

	err = c.Login(userName, userPassword)
	if err != nil {
		log.Fatal(err)
	}
	defer c.Logout()

	var readOnly = true
	mboxStatus, err := c.Select(imap.InboxName, readOnly)
	if err != nil {
		log.Fatal(err)
	}

	criteria := imap.NewSearchCriteria()
	criteria.WithoutFlags = []string{imap.SeenFlag}
	unreadIds, err := c.Search(criteria)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("%d/%d\n", len(unreadIds), mboxStatus.Messages)

	os.Exit(0)
}
