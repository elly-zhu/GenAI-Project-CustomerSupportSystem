import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import http from "http";
import dotenv from "dotenv";
import { spawn } from "child_process";
import { Server as SocketServer } from "socket.io"; // Import Socket.io

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const port = 8080;
const app = express();

const server = http.createServer(app);
const io = new SocketServer(server); // Create a Socket.io server

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use("/static", express.static(path.join(__dirname, "static")));

server.listen(port, () => {
  console.log(`Node app listening on port ${port}!`);
});

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/index.html");
});

app.post("/crawl", (req, res) => {
  io.emit("crawlingStarted");
  console.log("start crawling...");
  const domainName = req.body.domainName;
  const fullUrl = req.body.fullUrl;
  const scrapedFilePath = req.body.scrapedFilePath;
  const limit = req.body.limit;

  runBy(
    "./crawler.py",
    "setup_crawler",
    domainName,
    fullUrl,
    scrapedFilePath,
    limit
  )
    .then((data) => {
      // Emit a socket event to notify the client that the crawling is finished
      io.emit("crawlingFinished", { result: data.toString() });
      console.log("crawling completed...");
      console.log(data.toString());
    })
    .catch((error) => {
      console.error("Error running Python script:", error.toString());
    });
});

app.post("/embedding", (req, res) => {
  io.emit("embeddingStarted");
  console.log("start embedding...");
  const scrapedFilePath = req.body.scrapedFilePath;
  runBy("./embedding.py", scrapedFilePath)
    .then((data) => {
      // Emit a socket event to notify the client that the crawling is finished
      io.emit("embeddingFinished", { result: data.toString() });
      console.log("embedding completed...");
      console.log(data.toString());
    })
    .catch((error) => {
      console.error("Error running Python script:", error.toString());
    });
});

app.post("/answer", (req, res) => {
  console.log("start answer...");
  const embeddingFile = req.body.embeddingFile;
  const question = req.body.question;

  io.emit("answerStarted");

  try {
    runBy("./answer.py", embeddingFile, question)
      .then((data) => {
        // Emit a socket event to notify the client that the crawling is finished
        io.emit("answerFinished", { result: data.toString() });
        console.log("answer completed...");
        console.log(data.toString());
      })
      .catch((error) => {
        console.error("Error running Python script:", error.toString());
      });
  } catch (err) {
    console.err(err);
  }
});

async function runBy(scriptName, ...args) {
  return new Promise(async (resolve, reject) => {
    try {
      // Modify this array to include any additional arguments you want to pass to the Python script
      const pyArgs = [scriptName, ...args];

      const pyprog = spawn("python3", pyArgs);

      let stdoutData = "";
      let stderrData = "";

      pyprog.stdout.on("data", function (data) {
        stdoutData += data.toString();
      });

      pyprog.stderr.on("data", (data) => {
        stderrData += data.toString();
      });

      pyprog.on("close", (code) => {
        if (code === 0) {
          resolve(stdoutData);
        } else {
          reject(stderrData);
        }
      });
    } catch (error) {
      reject(error);
    }
  });
}
