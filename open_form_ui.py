#!/usr/bin/env python
"""
Open Form in Browser UI
Opens form in a new browser tab that you can see
"""
import asyncio
import aiohttp
import webbrowser
import sys

FORMS = {
    "loan": "https://vpbank-shared-form-fastdeploy.vercel.app/",
    "crm": "https://case2-ten.vercel.app/",
    "hr": "https://case3-seven.vercel.app/",
    "compliance": "https://case4-beta.vercel.app/",
    "operations": "https://case5-chi.vercel.app/"
}

async def get_live_url():
    """Get live browser URL from Browser Agent"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:7863/api/live') as resp:
                data = await resp.json()
                return data.get('live_url')
    except:
        return None

async def open_form(form_type):
    """Open form in browser"""
    if form_type not in FORMS:
        print(f"❌ Unknown form type: {form_type}")
        print(f"Available: {', '.join(FORMS.keys())}")
        return
    
    url = FORMS[form_type]
    
    # Option 1: Get live browser URL
    live_url = await get_live_url()
    if live_url:
        print(f"🌐 Browser Agent is running in headless mode")
        print(f"📺 View live session: {live_url}")
        print(f"📋 Form URL: {url}")
        print(f"\n💡 To see the form, open the live URL above in your browser")
        return
    
    # Option 2: Open directly in local browser
    print(f"🌐 Opening {form_type.upper()} form in your browser...")
    print(f"📋 URL: {url}")
    webbrowser.open(url)
    print("✅ Form opened in new tab!")

if __name__ == '__main__':
    form_type = sys.argv[1] if len(sys.argv) > 1 else 'hr'
    asyncio.run(open_form(form_type))
