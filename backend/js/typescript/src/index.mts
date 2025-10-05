import * as express from 'express';

const app: express.Application = express();
const port: number = 4000;

app.get('/', (_req, res) => {
  res.send('Hello from TypeScript with Express!');
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});
