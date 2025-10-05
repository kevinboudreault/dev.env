import * as express from 'express';
var app = express();
var port = 4000;
app.get('/', function (_req, res) {
    res.send('Hello from TypeScript with Express!');
});
app.listen(port, function () {
    console.log("Server running at http://localhost:".concat(port, "/"));
});
