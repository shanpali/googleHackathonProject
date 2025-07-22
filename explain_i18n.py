#!/usr/bin/env python3
"""
Detailed explanation and demonstration of how locale detection works.
This shows the complete flow from HTTP request to localized response.
"""

def explain_locale_detection():
    print("🌍 HOW LOCALE DETECTION WORKS IN OUR I18N SYSTEM")
    print("=" * 60)
    
    print("\n📡 1. CLIENT SENDS REQUEST")
    print("-" * 30)
    print("Example HTTP request:")
    print("POST /api/mcp/prompt HTTP/1.1")
    print("Content-Type: application/json")
    print("Accept-Language: es,en;q=0.9,fr;q=0.8")  # Spanish preferred, English backup
    print("Authorization: Bearer abc123")
    print('{"mcp_server_id": "test", "prompt_id": "test"}')
    
    print("\n🔍 2. FLASK RECEIVES REQUEST")
    print("-" * 30)
    print("Flask automatically parses headers into request.headers object:")
    print("request.headers['Accept-Language'] = 'es,en;q=0.9,fr;q=0.8'")
    
    print("\n⚙️  3. OUR I18N SERVICE DETECTS LOCALE")
    print("-" * 30)
    print("When get_localized_error() is called:")
    print("├── Calls get_locale() method")
    print("├── Checks if Flask request context exists")
    print("├── Gets Accept-Language header")
    print("├── Parses 'es,en;q=0.9,fr;q=0.8' → takes first: 'es'")
    print("├── Checks if 'es' locale files exist")
    print("└── Returns 'es' (or fallback to 'en' if not found)")
    
    print("\n📂 4. LOADS APPROPRIATE MESSAGE FILE")
    print("-" * 30)
    print("System loads: i18n/locales/es/errors.json")
    print("Looks up error code: 'AUTH_001'")
    print("Returns: 'Se requiere un encabezado de autorización con token Bearer.'")
    
    print("\n📤 5. FLASK SENDS RESPONSE")
    print("-" * 30)
    print("HTTP/1.1 401 Unauthorized")
    print("Content-Type: application/json")
    print('{"error": "Se requiere un encabezado de autorización con token Bearer."}')
    
    print("\n🔄 COMPLETE FLOW DIAGRAM")
    print("-" * 30)
    print("""
    Client Request                    Flask App                    I18n Service
    ┌─────────────┐                 ┌─────────────┐              ┌─────────────┐
    │ HTTP POST   │────────────────▶│ app.py      │─────────────▶│ service.py  │
    │ Accept-     │                 │ mcp_prompt()│              │ get_locale()│
    │ Language: es│                 │             │              │             │
    └─────────────┘                 └─────────────┘              └─────────────┘
           │                               │                             │
           │                               │                             ▼
           │                               │                    ┌─────────────┐
           │                               │                    │Parse header │
           │                               │                    │'es,en;q=0.9'│
           │                               │                    │→ 'es'       │
           │                               │                    └─────────────┘
           │                               │                             │
           │                               │                             ▼
           │                               │                    ┌─────────────┐
           │                               │                    │Load es/     │
           │                               │                    │errors.json  │
           │                               │◀────────────────────│Return msg   │
           │                               │                    └─────────────┘
           │                               ▼
           │                    ┌─────────────┐
           │◀───────────────────│Return JSON  │
           │                    │with Spanish │
           │                    │error message│
           │                    └─────────────┘
    """)

def demonstrate_with_examples():
    print("\n\n🧪 PRACTICAL EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "header": "es",
            "description": "Spanish client",
            "result": "Spanish message"
        },
        {
            "header": "fr,en;q=0.9",
            "description": "French preferred, English fallback",
            "result": "French message"
        },
        {
            "header": "de,es;q=0.8,en;q=0.7",
            "description": "German (not available), falls back to Spanish",
            "result": "Spanish message (fallback)"
        },
        {
            "header": "",
            "description": "No header",
            "result": "English message (default)"
        },
        {
            "header": "zh-CN,zh;q=0.9",
            "description": "Chinese (not available)",
            "result": "English message (fallback)"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   Accept-Language: '{example['header']}'")
        print(f"   Result: {example['result']}")

if __name__ == "__main__":
    explain_locale_detection()
    demonstrate_with_examples()
    
    print("\n\n💡 KEY POINTS:")
    print("-" * 15)
    print("✅ Uses standard HTTP Accept-Language header")
    print("✅ Works automatically - no client code changes needed")
    print("✅ Graceful fallback to English if language not supported")
    print("✅ Parses complex headers (quality values, multiple languages)")
    print("✅ Thread-safe and works with Flask request context")
    print("✅ Can be overridden by passing locale parameter explicitly")
