const express = require("express");
const cors = require("cors");
const multer = require("multer");
const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(cors());

const FLASK_API_URL = "http://127.0.0.1:5000";

app.get("/api/health", async (req, res) => {
  try {
    const response = await axios.get(`${FLASK_API_URL}/api/health`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: "Flask API not reachable" });
  }
});

app.post("/api/analyze", upload.array("documents"), async (req, res) => {
  try {
    const form = new FormData();
    req.files.forEach((file) => {
      form.append("documents", fs.createReadStream(file.path), file.originalname);
    });

    const response = await axios.post(`${FLASK_API_URL}/api/analyze`, form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity,
    });

    req.files.forEach((file) => fs.unlinkSync(file.path)); // cleanup temp files

    res.json(response.data);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: "Failed to analyze documents" });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Express server running on http://localhost:${PORT}`);
});