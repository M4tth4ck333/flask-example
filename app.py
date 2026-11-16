import os
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox, scrolledtext
import flask
import requests_oauthlib

# --- 1. Konfiguration & Umgebung ---
CLIENT_ID = os.environ.get("CLIENT_ID", "DEINE_SIMPLELOGIN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "DEINESIMPLELOGIN_CLIENT_SECRET")

# Für lokale HTTP-Tests während der Entwicklung
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Flask App Initialisierung
app = flask.Flask("Area51-OAuth-Desktop")
app.secret_key = "systemtuv-super-secret-key-area51"

# Globaler Zustand für das Tkinter Dashboard
auth_user_data = {"logged_in": False, "name": "Gast", "email": "Nicht authentifiziert", "avatar": ""}


# --- 2. Flask OAuth Routes (SimpleLogin) ---
@app.route("/")
def index():
    if auth_user_data["logged_in"]:
        return f"""
        <body style="background:#05070a; color:#00ffcc; font-family:monospace; padding:30px;">
            <h2>🌌 SystemT Area51 // Autorisierung erfolgreich</h2>
            <p>Willkommen, <b>{auth_user_data['name']}</b> ({auth_user_data['email']})</p>
            <p>Du kannst dieses Browserfenster nun schliessen und zum Tkinter-Desktop zurückkehren.</p>
        </body>
        """
    return """
    <body style="background:#05070a; color:#00ffcc; font-family:monospace; padding:30px;">
        <h2>🌌 SystemT Area51 // Login erforderlich</h2>
        <a href="/login" style="color:#00ffcc; font-size:1.2rem; text-decoration:none; border:1px solid #00ffcc; padding:10px 20px; display:inline-block;">🔐 Login with SimpleLogin</a>
    </body>
    """


@app.route("/login")
def login():
    sl = requests_oauthlib.OAuth2Session(
        CLIENT_ID,
        redirect_uri="http://localhost:5000/callback",
    )
    redirect_url, state = sl.authorization_url(
        "https://app.simplelogin.io/oauth2/authorize"
    )
    flask.session["oauth_state"] = state
    return flask.redirect(redirect_url)


@app.route("/callback")
def callback():
    try:
        sl = requests_oauthlib.OAuth2Session(
            CLIENT_ID, state=flask.session.get("oauth_state")
        )
        sl.fetch_token(
            "https://app.simplelogin.io/oauth2/token",
            client_secret=CLIENT_SECRET,
            authorization_response=flask.request.url,
        )
        user_info = sl.get("https://app.simplelogin.io/oauth2/userinfo").json()
        
        # Aktualisiere globalen Status für das Tkinter-Dashboard
        auth_user_data["logged_in"] = True
        auth_user_data["name"] = user_info.get("name", "User")
        auth_user_data["email"] = user_info.get("email", "unknown@simplelogin")
        auth_user_data["avatar"] = user_info.get("avatar_url", "")
        
        return flask.redirect("/")
    except Exception as e:
        return f"<h3>OAuth Authentifizierungsfehler:</h3><p>{str(e)}</p>"


# --- 3. Tkinter Desktop Control Center ---
class Area51DesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Area51 // SystemTUV Desktop Node")
        self.root.geometry("650+450")
        self.root.configure(bg="#05070a")

        # UI Header
        title_lbl = tk.Label(root, text="🌌 SystemT Area51 // Native Control Center", bg="#05070a", fg="#00ffcc", font=("Courier", 14, "bold"))
        title_lbl.pack(pady=15)

        # Status Frame
        status_frame = tk.LabelFrame(root, text=" Metakernel & OAuth Status ", bg="#05070a", fg="#00ffcc", font=("Courier", 10), bd=1, relief="solid")
        status_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_status = tk.Label(status_frame, text="Status: Nicht angemeldet (Warte auf SimpleLogin)", bg="#05070a", fg="#ff5577", font=("Courier", 10, "bold"), anchor="w")
        self.lbl_status.pack(fill="x", padx=10, pady=10)

        # Action Buttons
        btn_frame = tk.Frame(root, bg="#05070a")
        btn_frame.pack(pady=10)

        self.btn_login = tk.Button(btn_frame, text="SimpleLogin Browser öffnen", command=self.open_login, bg="#0b0f19", fg="#00ffcc", font=("Courier", 10), relief="groove", padx=10, pady=5)
        self.btn_login.grid(row=0, column=0, padx=10)

        self.btn_refresh = tk.Button(btn_frame, text="Status aktualisieren", command=self.check_auth_status, bg="#0b0f19", fg="#00ffcc", font=("Courier", 10), relief="groove", padx=10, pady=5)
        self.btn_refresh.grid(row=0, column=1, padx=10)

        # Console Log Area
        log_frame = tk.LabelFrame(root, text=" SystemT Terminal Log ", bg="#05070a", fg="#00ffcc", font=("Courier", 10), bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.console = scrolledtext.ScrolledText(log_frame, bg="#000000", fg="#00ffcc", font=("Courier", 9), insertbackground="#00ffcc")
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        self.log("🚀 Tkinter Desktop Node erfolgreich gestartet.")
        self.log("ℹ️ Klicke auf 'SimpleLogin Browser öffnen', um die OAuth-Identifikation durchzuführen.")

        # Periodischer Check des Auth-Status
        self.root.after(2000, self.auto_poll_auth)

    def log(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)

    def open_login(self):
        self.log("🌐 Öffne Standard-Browser für SimpleLogin OAuth...")
        webbrowser.open("http://localhost:5000/login")

    def check_auth_status(self):
        if auth_user_data["logged_in"]:
            self.lbl_status.config(text=f"Status: Authentifiziert als {auth_user_data['name']} ({auth_user_data['email']})", fg="#00ffcc")
            self.log(f"[OAuth ACK] Benutzer eingeloggt: {auth_user_data['name']} <{auth_user_data['email']}>")
        else:
            self.lbl_status.config(text="Status: Wartet auf Authentifizierung...", fg="#ff5577")

    def auto_poll_auth(self):
        if auth_user_data["logged_in"] and "verified" not in self.console.get("1.0", tk.END):
            self.check_auth_status()
            self.log("✨ Metakernel-Sitzung erfolgreich gesichert.")
        self.root.after(3000, self.auto_poll_auth)


# --- 4. Server-Daemon Thread ---
def run_flask_server():
    print("[Area51 Daemon] Starte lokalen OAuth-Callback Server auf Port 5000...")
    # socketserver / werkzeug läuft im Hintergrundthread
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Starte den Flask-Server im Hintergrund-Daemon-Thread
    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()

    # Starte die Tkinter Hauptschleife (Main Thread)
    root = tk.Tk()
    app_gui = Area51DesktopApp(root)
    root.mainloop()
