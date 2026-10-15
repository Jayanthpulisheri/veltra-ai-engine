import os
import secrets
import resend
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI(title="Veltra AI Security Middleware")

resend.api_key = os.getenv("RESEND_API_KEY", "")

API_KEYS_DB = {}

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Veltra AI Security Engine"}

@app.post("/v1/webhooks/lemonsqueezy")
async def handle_lemonsqueezy_webhook(request: Request):
    payload = await request.json()
    event_name = payload.get("meta", {}).get("event_name")
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    
    # Extract customer email
    user_email = attributes.get("user_email") or attributes.get("customer_email") or "jayanth@example.com"
    subscription_status = attributes.get("status", "active")

    print(f"[+] Webhook triggered! Event: {event_name} | User: {user_email}")

    # Generate key and dispatch email
    new_key = f"veltra_live_{secrets.token_hex(16)}"
    API_KEYS_DB[user_email] = {
        "api_key": new_key,
        "status": subscription_status,
        "tier": "Pro"
    }
    print(f"[+] Issued Veltra Key: {new_key} for {user_email}")

    try:
        resend.Emails.send({
            "from": "Veltra AI Security <onboarding@resend.dev>",
            "to": [user_email],
            "subject": "Your Veltra Pro API Key is Ready! 🔑",
            "html": f"""
                <div style="font-family: sans-serif; padding: 20px; color: #333;">
                    <h2>Welcome to Veltra AI Security! 🎉</h2>
                    <p>Thank you for subscribing to Veltra Pro.</p>
                    <p>Your live API key has been provisioned:</p>
                    <div style="background: #1e1e2e; color: #a6e3a1; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 16px;">
                        {new_key}
                    </div>
                    <p style="margin-top: 20px;">Keep this key secret. You can now use it in your Veltra SDK configuration.</p>
                    <p>Best regards,<br><strong>Jayanth & The Veltra Team</strong></p>
                </div>
            """
        })
        print(f"[+] Email successfully dispatched to {user_email}")
    except Exception as e:
        print(f"[-] Failed to send email via Resend: {e}")

    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
