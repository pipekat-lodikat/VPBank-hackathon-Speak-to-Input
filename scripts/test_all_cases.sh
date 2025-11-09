#!/bin/bash

echo "🧪 Testing All 5 Banking Use Cases"
echo "==================================="
echo ""

# Test data for each case
declare -A CASES=(
    ["Case 1: Loan & KYC"]="https://vpbank-shared-form-fastdeploy.vercel.app/"
    ["Case 2: CRM Updates"]="https://case2-ten.vercel.app/"
    ["Case 3: HR Workflows"]="https://case3-seven.vercel.app/"
    ["Case 4: Compliance"]="https://case4-beta.vercel.app/"
    ["Case 5: Operations"]="https://case5-chi.vercel.app/"
)

# Test each case
for case in "${!CASES[@]}"; do
    url="${CASES[$case]}"
    echo "📋 Testing: $case"
    echo "   URL: $url"
    
    # Check if URL is accessible
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    if [ "$status" = "200" ]; then
        echo "   ✅ Form accessible"
    else
        echo "   ❌ Form not accessible (HTTP $status)"
    fi
    echo ""
done

echo "🎤 Voice Bot Test"
echo "-----------------"
curl -s http://localhost:7860 > /dev/null 2>&1 && echo "✅ Voice Bot ready" || echo "❌ Voice Bot down"

echo ""
echo "🤖 Browser Agent Test"
echo "---------------------"
curl -s http://localhost:7863/api/health | jq . 2>&1 | grep -q "healthy" && echo "✅ Browser Agent ready" || echo "❌ Browser Agent down"

echo ""
echo "🌐 Frontend Test"
echo "----------------"
curl -s http://localhost:5173 > /dev/null 2>&1 && echo "✅ Frontend ready" || echo "❌ Frontend down"

echo ""
echo "✅ Test complete!"
echo ""
echo "📝 Next steps:"
echo "1. Open http://localhost:5173"
echo "2. Test voice interaction for each case"
echo "3. Verify form auto-fill works"
echo "4. Record demo video"
