function handleCrawlingStarted() {
  console.log("Crawling Started");
  const button = document.querySelector("#crawlBtn");
  button.disabled = true;
  const loader = document.querySelector("#crawlerSection .loader");
  loader.classList.remove("hide");
}

function handleCrawlingCompleted(data) {
  console.log("Crawling Completed");
  const loader = document.querySelector("#crawlerSection .loader");
  loader.classList.add("hide");
  const button = document.querySelector("#crawlBtn");
  button.disabled = false;
  const outputPanel = document.querySelector(
    "#crawlerSection .outputPanel .container"
  );
  const output = data.result;
  const outputWithLineBreaks = output.replace(/\n/g, "<br>");
  outputPanel.innerHTML = outputWithLineBreaks;
}

function handleEmbeddingStarted() {
  console.log("Embedding Started");
  const button = document.querySelector("#embeddingBtn");
  button.disabled = true;
  const loader = document.querySelector("#embeddingSection .loader");
  loader.classList.remove("hide");
}

function handleEmbeddingCompleted(data) {
  console.log("Embedding Completed");
  const loader = document.querySelector("#embeddingSection .loader");
  loader.classList.add("hide");
  const button = document.querySelector("#embeddingBtn");
  button.disabled = false;
  const outputPanel = document.querySelector(
    "#embeddingSection .outputPanel .container"
  );
  const output = data.result;
  const outputWithLineBreaks = output.replace(/\n/g, "<br>");
  outputPanel.innerHTML = outputWithLineBreaks;
}

function handleAnswerStarted() {
  console.log("Answer Started");
  const button = document.querySelector("#answerBtn");
  button.disabled = true;
  const loader = document.querySelector("#answerSection .loader");
  const clear = document.querySelector("#answerSection .clear");

  loader.classList.remove("hide");
  clear.classList.add("hide");
}

function handleAnswerCompleted(data) {
  console.log("Answer Completed");
  const loader = document.querySelector("#answerSection .loader");
  const clear = document.querySelector("#answerSection .clear");
  loader.classList.add("hide");
  clear.classList.remove("hide");
  const button = document.querySelector("#answerBtn");
  button.disabled = false;
  const outputPanel = document.querySelector(
    "#answerSection .outputPanel .container"
  );

  const output = data.result;
  const outputWithLineBreaks = output.replace(/\n/g, "<br>");
  outputPanel.innerHTML =
    outputWithLineBreaks +
    returnFormatNowIn24Hour() +
    "<br/>" +
    "<br/>" +
    outputPanel.innerHTML;

  document.querySelector("#answerSection #question").value = "";
}

function clearAnswerPanel() {
  const outputPanel = document.querySelector(
    "#answerSection .outputPanel .container"
  );
  outputPanel.innerHTML = "";
}

// Function to convert
// single digit input
// to two digits
const formatData = (input) => {
  if (input > 9) {
    return input;
  } else return `0${input}`;
};

// Data about date

const returnFormatNowIn24Hour = () => {
  const date = new Date();
  const dd = formatData(date.getDate());
  const mm = formatData(date.getMonth() + 1);
  const yyyy = date.getFullYear();
  const HH = formatData(date.getHours());
  const MM = formatData(date.getMinutes());
  const SS = formatData(date.getSeconds());

  return `${yyyy}-${mm}-${dd} ${HH}:${MM}:${SS}`;
};
