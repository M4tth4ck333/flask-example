import os
import threading
import webbrowser
import tkinter as tk
from tkinter import scrolledtext
import flask
import requests_oauthlib

# --- 1. Konfiguration & Umgebung ---
CLIENT_ID = os.environ.get("CLIENT_ID", "DEINE_SIMPLELOGIN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "DEINESIMPLELOGIN_CLIENT_SECRET")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Flask App Initialisierung
app = flask.Flask("Area51-PyReact-Desktop")
app.secret_key = "systemtuv-pyreact-super-secret"

# Globaler Zustand für Desktop und Web
auth_user_data = {"logged_in": False, "name": "Gast", "email": "Nicht authentifiziert"}


# --- 2. Flask Web-Server & PyReact-Render-Engine ---
@app.route("/")
def index():
    # PyReact-adaptierte HTML/JSX Ansicht für den Client
    user_status_html = f"<b>{auth_user_data['name']}</b> ({auth_user_data['email']})" if auth_user_data["logged_in"] else "Nicht angemeldet"
    login_btn_html = '<a href="/login" style="color:#00ffcc; border:1px solid #00ffcc; padding:8px 15px; text-decoration:none;">🔐 Login via SimpleLogin</a>' if not auth_user_data["logged_in"] else '<p style="color:#00ffcc;">Sitzung aktiv & verifiziert.</p>'

    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Area51 // PyReact Control Plane</title>
        <style>
            body {{ background: #05070a; color: #00ffcc; font-family: monospace; padding: 40px; }}
            .card {{ border: 1px solid #00ffcc; padding: 20px; background: #000; box-shadow: 0 0 15px rgba(0,255,204,0.15); border-radius: 6px; max-width: 600px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🌌 SystemT Area51 // PyReact Node</h2>
            <p>Auth-Status: {user_status_html}</p>
            <hr style="border-color: #1a3a3a;">
            <p>Metakernel Gateway: Aktiv (Bitbreite: 32-bit, CFFI-Modus)</p>
            <br>
            {login_btn_html}
        </div>
    </body>
    </html>
    """


@app.route("/login")
def login():
    sl = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri="http://localhost:5000/callback")
    redirect_url, state = sl.authorization_url("https://app.simplelogin.io/oauth2/authorize")
    flask.session["oauth_state"] = state
    return flask.redirect(redirect_url)


@app.route("/callback")
def callback():
    try:
        sl = requests_oauthlib.OAuth2Session(CLIENT_ID, state=flask.session.get("oauth_state"))
        sl.fetch_token(
            "https://app.simplelogin.io/oauth2/token",
            client_secret=CLIENT_SECRET,
            authorization_response=flask.request.url,
        )
        user_info = sl.get("https://app.simplelogin.io/oauth2/userinfo").json()
        
        auth_user_data["logged_in"] = True
        auth_user_data["name"] = user_info.get("name", "Operator")
        auth_user_data["email"] = user_info.get("email", "operator@v1rtu4lyz1um.com")
        
        return flask.redirect("/")
    except Exception as e:
        return f"<h3>Auth Fehler:</h3><p>{str(e)}</p>"


# --- 3. Tkinter Desktop Control Panel ---
class PyReactDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Area51 // PyReact & Metakernel Desktop")
        self.root.geometry("700+500")
        self.root.configure(bg="#05070a")

        title_lbl = tk.Label(root, text="🚀 SystemT Area51 // PyReact Native Studio", bg="#05070a", fg="#00ffcc", font=("Courier", 13, "bold"))
        title_lbl.pack(pady=15)

        # Status Frame
        status_frame = tk.LabelFrame(root, text=" PyReact & OAuth Runtime ", bg="#05070a", fg="#00ffcc", font=("Courier", 10), bd=1, relief="solid")
        status_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_status = tk.Label(status_frame, text="Status: Warte auf SimpleLogin Authentifizierung...", bg="#05070a", fg="#ff5577", font=("Courier", 9, "bold"), anchor="w")
        self.lbl_status.pack(fill="x", padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#05070a")
        btn_frame.pack(pady=10)

        self.btn_browser = tk.Button(btn_frame, text="PyReact Web-App öffnen", command=lambda: webbrowser.open("http://localhost:5000"), bg="#0b0f19", fg="#00ffcc", font=("Courier", 10), relief="groove", padx=10, pady=5)
        self.btn_browser.grid(row=0, column=0, padx=10)

        self.btn_refresh = tk.Button(btn_frame, text="Status synchronisieren", command=self.update_status, bg="#0b0f19", fg="#00ffcc", font=("Courier", 10), relief="groove", padx=10, pady=5)
        self.btn_refresh.grid(row=0, column=1, padx=10)

        # Terminal Log
        log_frame = tk.LabelFrame(root, text=" Metakernel & PyReact Log ", bg="#05070a", fg="#00ffcc", font=("Courier", 10), bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.console = scrolledtext.ScrolledText(log_frame, bg="#000000", fg="#00ffcc", font=("Courier", 9), insertbackground="#00ffcc")
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        self.log("✨ PyReact Desktop Node gestartet.")
        self.log("ℹ️ Der Flask/PyReact Server läuft im Hintergrund auf Port 5000.")

        self.root.after(2000, self.poll_state)

    def log(self, msg):
        self.console.insert(tk.END, msg + "\n")
        self.console.see(tk.END)

    def update_status(self):
        if auth_user_data["logged_in"]:
            self.lbl_status.config(text=f"Status: Verbunden als {auth_user_data['name']} <{auth_user_data['email']}>", fg="#00ffcc")
            self.log(f"[PyReact Sync] Benutzer erfolgreich autorisiert: {auth_user_data['name']}")
        else:
            self.lbl_status.config(text="Status: Nicht angemeldet", fg="#ff5577")

    def poll_state(self):
        if auth_user_data["logged_in"] and "synced" not in self.console.get("1.0", tk.END):
            self.update_status()
            self.log("🔒 Token verifiziert. PyReact DOM-Brücke aktiv.")
        self.root.after(3000, self.poll_state)


def run_server():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Server im Hintergrund-Thread starten
    threading.Thread(target=run_server, daemon=True).start()
    
    # Tkinter Loop im Hauptthread
    root = tk.Tk()
    app_gui = PyReactDesktopApp(root)
    root.mainloop()
