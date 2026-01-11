#!/bin/bash
# Monitor API testing progress and send batch emails every 20 completions

LOG_FILE="/tmp/free-apis-verified/recursive_test.log"
RESULT_FILE="/tmp/free-apis-verified/complete_verification.json"
LAST_COUNT=0

while true; do
    sleep 30  # Check every 30 seconds
    
    # Count completed tests
    CURRENT_COUNT=$(grep -c "RELIABILITY:" "$LOG_FILE" 2>/dev/null || echo 0)
    
    # Check if we've completed 20 more
    if [ $((CURRENT_COUNT - LAST_COUNT)) -ge 20 ]; then
        # Extract last 20 results
        BATCH_RESULTS=$(tail -100 "$LOG_FILE" | grep -A 3 "LIVE TEST:" | tail -80)
        
        # Send email
        manus-mcp-cli tool call gmail_send_messages --server gmail --input "{\"messages\":[{\"to\":[\"npoinsette@gmail.com\",\"king.thedros@gmail.com\"],\"subject\":\"API Testing Progress - ${CURRENT_COUNT} APIs Completed\",\"content\":\"Batch Update: ${CURRENT_COUNT} APIs tested\n\nRecording:\n- API name and URL\n- Status code (200, 404, etc)\n- Response time (seconds)\n- Response size (bytes)\n- Success/failure\n- Partner APIs discovered\n- Headers received\n- Sample data\n\nLast 20 completed:\n${BATCH_RESULTS}\n\nTesting continues...\"}]}" > /dev/null 2>&1
        
        LAST_COUNT=$CURRENT_COUNT
    fi
    
    # Check if testing is complete
    if [ -f "$RESULT_FILE" ] && ! pgrep -f "test_all_apis_recursive.py" > /dev/null; then
        echo "Testing complete - final email will be sent"
        break
    fi
done
