#!/bin/bash
# Autonomous 48-hour API testing with hourly reports

START_TIME=$(date +%s)
END_TIME=$((START_TIME + 172800))  # 48 hours = 172800 seconds
HOUR=0

echo "Starting 48-hour autonomous testing"
echo "Start: $(date)"
echo "End: $(date -d @$END_TIME)"

while [ $(date +%s) -lt $END_TIME ]; do
    HOUR=$((HOUR + 1))
    CURRENT=$(date +%s)
    REMAINING=$((END_TIME - CURRENT))
    HOURS_LEFT=$((REMAINING / 3600))
    
    # Collect stats
    TESTED=$(grep -c "RELIABILITY:" /tmp/free-apis-verified/recursive_test.log 2>/dev/null || echo 0)
    VERIFIED=$(grep -c "✓ YES" /tmp/free-apis-verified/recursive_test.log 2>/dev/null || echo 0)
    FAILED=$(grep -c "✗ NO" /tmp/free-apis-verified/recursive_test.log 2>/dev/null || echo 0)
    PARTNERS=$(grep -c "Partners Found:" /tmp/free-apis-verified/recursive_test.log 2>/dev/null || echo 0)
    
    # Send hourly report
    manus-mcp-cli tool call gmail_send_messages --server gmail --input "{\"messages\":[{\"to\":[\"npoinsette@gmail.com\",\"king.thedros@gmail.com\"],\"subject\":\"Hour ${HOUR}/48 - API Testing Report\",\"content\":\"Autonomous Testing Report\n\nHour: ${HOUR} of 48\nRemaining: ${HOURS_LEFT} hours\n\nProgress:\n- APIs Tested: ${TESTED}\n- Verified: ${VERIFIED}\n- Failed: ${FAILED}\n- Partners Discovered: ${PARTNERS}\n\nAll data saved to:\nhttps://github.com/onlyecho822-source/free-apis-verified\n\nNext report in 1 hour.\"}]}" > /dev/null 2>&1
    
    # Upload to Drive every hour
    if [ -f /tmp/free-apis-verified/complete_verification.json ]; then
        rclone copy /tmp/free-apis-verified/complete_verification.json manus_google_drive:API-Test-Results/hour-${HOUR}/ --config /home/ubuntu/.gdrive-rclone.ini
    fi
    
    # Sleep 1 hour
    sleep 3600
done

# Final report
echo "48 hours complete - sending final report"
manus-mcp-cli tool call gmail_send_messages --server gmail --input "{\"messages\":[{\"to\":[\"npoinsette@gmail.com\",\"king.thedros@gmail.com\"],\"subject\":\"FINAL REPORT - 48 Hour API Testing Complete\",\"content\":\"48-Hour Autonomous Testing Complete\n\nFinal Stats:\n- Total APIs Tested: ${TESTED}\n- Verified: ${VERIFIED}\n- Failed: ${FAILED}\n- Partners Discovered: ${PARTNERS}\n\nAll results saved to:\nhttps://github.com/onlyecho822-source/free-apis-verified\nhttps://drive.google.com/drive/folders/API-Test-Results\n\nTesting terminated as scheduled.\"}]}" > /dev/null 2>&1

# Terminate processes
pkill -f test_all_apis_recursive.py
pkill -f monitor_and_email.sh

echo "Autonomous testing ended: $(date)"
