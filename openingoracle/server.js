const express = require('express');
const app = express();
app.use(express.json()) 
const port = 8080;

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "http://localhost:3000");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.listen(port, () => console.log(`Listening on port ${port}`));

app.post('/postRequestOpening', async (req, res) => {
  let body = req.body;
  console.log(body);
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms))
  await delay(1000)
  res.send({ message: body.message});
});