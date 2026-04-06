~/usm_server $ cat << 'EOF' > README.md
<p align="center">
  <img src="https://img.shields.io/badge/Language-Python_3.x-blue" />
  <img src="https://img.shields.io/badge/Architecture-USM_Server-black" />
  <img src="https://img.shields.io/badge/Telemetry-JSON+Binary-success" />
  <img src="https://img.shields.io/badge/Transport-WebSocket-orange" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Android-lightgrey" />
</p>

Universal State Mirror (USM)

A lightweight, ROS‑agnostic real‑time telemetry router for robots, simulations, and distributed systems.

---

🚀 Why USM Exists
Robotics teams struggle with fragmented telemetry, inconsistent logging, and no unified way to introspect robot state in real time.
ROS topics don’t extend cleanly across devices, ROS bags are offline‑only, and custom dashboards are brittle and stack‑specific.
> Run the server:
                                                                        `
python3 -m usm_server
`

Run the test client:

`
python3 testclient.py
`

You’ll immediately see live telemetry flowing through the system.

---

🧠 Architecture Overview

Publishers
Send JSON or binary frames to the USM server.

USM Server
- timestamps
- stores
- routes
- mirrors
- broadcasts

Viewers
Subscribe to patterns and receive live data instantly.

---

📡 Example Usage

Publisher (JSON)
`python
await ws.send(json.dumps({
  "type": "publish",
  "namespace": "robot/alpha/state",
  "data": {"x": 1.2, "y": 0.4}
}))
`

Viewer
`python
await ws.send(json.dumps({
  "type": "subscribe",
  "pattern": "#"
}))
`

---

🧩 Use Cases

- Robot → dashboard telemetry
- Simulation → robot state mirroring
- Sensor → viewer binary streaming
- Multi‑robot coordination
- Remote debugging
- Real‑time introspection during autonomy development
- Lightweight alternative to ROS tools

---

🆚 Why USM Is Different

USM is:

- ROS‑agnostic
- DDS‑free
- language‑agnostic
- device‑agnostic
- simple to integrate
- built for introspection, not message passing

It’s the missing layer robotics teams keep rebuilding internally.

---

👤 About the Author

Created by Kevin Price
Inventor, systems architect, and creator of the Universal State Mirror architecture.

---

📄 License
MIT License — free for commercial and research use
