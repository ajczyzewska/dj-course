import "dotenv/config";
import express from "express";
import { connectMongo } from "./db/mongo";
import invoiceRoutes from "./routes/invoices";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use("/invoices", invoiceRoutes);

async function start() {
  await connectMongo();
  app.listen(PORT, () => {
    console.log(`API running on port ${PORT}`);
  });
}

start().catch((err) => {
  console.error("Failed to start:", err);
  process.exit(1);
});
