import hmac
import hashlib
import os
import secrets
import resend
import uvicorn
from fastapi import FastAPI, Request, Header, HTTPException

app = FastAPI(title="Veltra AI Security Middleware")

WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "veltra_wh_secret_2026")
resend.api_key = os.getenv("RESEND_API_KEY", "")

API_KEYS_DB = {}

# Required for Replit Production Health Checks
@app.get("/")
def health_check():
    return {"status": "ok", "service": "Veltra AI Security Engine"}

def send_api_key_email(user_email: str, api_key: str):
    """Sends the Veltra API key to the customer upon subscription."""
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
                        {api_key}
                    </div>
                    <p style="margin-top: 20px;">Keep this key secret. You can now use it in your Veltra SDK configuration.</p>
                    <p>Best regards,<br><strong>Jayanth & The Veltra Team</strong></p>
                </div>
            """
        })
        print(f"[+] Email successfully sent to {user_email}")
    except Exception as e:
        print(f"[-] Failed to send email to {user_email}: {e}")

@app.post("/v1/webhooks/lemonsqueezy")
async def handle_lemonsqueezy_webhook(
    request: Request, 
    x_signature: str = Header(None)
):
    raw_body = await request.body()
    digest = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'), 
        raw_body, 
        hashlib.sha256
    ).hexdigest()

    if not x_signature or not hmac.compare_digest(digest, x_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event_name = payload.get("meta", {}).get("event_name")
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    
    user_email = attributes.get("user_email")
    subscription_status = attributes.get("status")

    if event_name in ["subscription_created", "subscription_updated"]:
        if subscription_status in ["active", "on_trial"]:
            new_key = f"veltra_live_{secrets.token_hex(16)}"
            API_KEYS_DB[user_email] = {
                "api_key": new_key,
                "status": subscription_status,
                "tier": "Pro"
            }
            print(f"[+] Issued new Veltra API Key for {user_email}: {new_key}")
            
            if user_email:
                send_api_key_email(user_email, new_key)

    elif event_name == "subscription_cancelled":
        if user_email in API_KEYS_DB:
            API_KEYS_DB[user_email]["status"] = "cancelled"
            print(f"[-] Subscription cancelled for {user_email}")

    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
